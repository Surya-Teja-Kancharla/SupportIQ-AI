from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)
from pydantic import ValidationError

from app.config.settings import settings
from app.core.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMRequestError,
    LLMResponseError,
    LLMTimeoutError,
    RetryExhaustedError,
    RetryableLLMError,
)
from app.core.retry import RetryExecutor, RetryPolicy
from app.prompts.registry import get_prompt
from app.schemas.ticket_analysis_schema import (
    TicketAnalysisRequest,
    TicketAnalysisResponse,
)
from app.services.llm_service import LLMService
from app.utils.json_extractor import extract_json_object


class GroqLLMService(LLMService):

    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise LLMConfigurationError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.groq_api_key,
            timeout=settings.groq_timeout_seconds,
        )

        self.model = settings.groq_model
        self.max_tokens = settings.groq_max_tokens
        self.temperature = settings.groq_temperature
        self.prompt = get_prompt(settings.prompt_version)

        self.retry_executor = RetryExecutor(
            RetryPolicy(
                max_attempts=settings.llm_max_retries + 1,
            )
        )

    def analyze_ticket(
        self,
        request: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:

        try:
            return self.retry_executor.execute(
                self._analyze_ticket_once,
                request,
                retry_on=(RetryableLLMError,),
                operation_name="groq_ticket_analysis",
            )

        except RetryExhaustedError as exc:
            cause = exc.__cause__

            if isinstance(cause, RetryableLLMError):
                raise cause

            raise LLMProviderError(
                "Groq ticket analysis failed after retries."
            ) from exc

    def _analyze_ticket_once(
        self,
        request: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:

        email = request.email

        user_prompt = self.prompt.user_prompt_builder(
            sender_name=email.sender_name,
            sender_email=str(email.sender_email),
            subject=email.subject,
            body=email.body,
            attachment_text=request.attachment_text,
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt.system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                response_format={
                    "type": "json_object",
                },
            )

        except APITimeoutError as exc:
            raise LLMTimeoutError(
                "Groq request timed out."
            ) from exc

        except RateLimitError as exc:
            raise LLMRateLimitError(
                "Groq API rate limit exceeded."
            ) from exc

        except AuthenticationError as exc:
            raise LLMAuthenticationError(
                "Groq authentication failed."
            ) from exc

        except APIConnectionError as exc:
            raise LLMProviderError(
                "Unable to connect to Groq."
            ) from exc

        except APIStatusError as exc:
            if exc.status_code >= 500:
                raise LLMProviderError(
                    (
                        "Groq returned a transient server error "
                        f"with HTTP status {exc.status_code}."
                    ),
                    context={
                        "status_code": exc.status_code,
                    },
                ) from exc

            raise LLMRequestError(
                f"Groq rejected the request with HTTP status {exc.status_code}.",
                context={
                    "status_code": exc.status_code,
                },
            ) from exc

        try:
            content = completion.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMResponseError(
                "Groq returned an invalid completion structure."
            ) from exc

        if not content:
            raise LLMResponseError(
                "Groq returned empty response content."
            )

        payload = extract_json_object(content)

        try:
            return TicketAnalysisResponse.model_validate(payload)

        except ValidationError as exc:
            raise LLMResponseError(
                "Groq response violated the ticket analysis schema.",
                context={
                    "validation_errors": exc.errors(),
                },
            ) from exc
