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
from app.schemas.reply_suggestion_schema import (
    ReplySuggestionRequest,
    ReplySuggestionResponse,
)
from app.schemas.ticket_analysis_schema import (
    TicketAnalysisRequest,
    TicketAnalysisResponse,
)
from app.services.llm_service import LLMService
from app.utils.json_extractor import extract_json_object


class GroqLLMService(LLMService):
    """
    Groq-backed implementation of the provider-independent LLMService contract.

    Supported capabilities:
    - structured ticket analysis,
    - customer-support reply suggestion generation.

    The Groq SDK performs no internal retries. Retry behavior is controlled by
    the application RetryExecutor so retry policy remains observable and
    testable.
    """

    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise LLMConfigurationError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.groq_api_key,
            timeout=settings.groq_timeout_seconds,
            max_retries=0,
        )

        self.model = settings.groq_model

        self.max_tokens = settings.groq_max_tokens
        self.temperature = settings.groq_temperature

        self.ticket_analysis_prompt = get_prompt(
            settings.prompt_version
        )

        self.prompt = self.ticket_analysis_prompt

        self.reply_suggestion_prompt = get_prompt(
            settings.reply_suggestion_prompt_version
        )

        self.reply_suggestion_max_tokens = (
            settings.reply_suggestion_max_tokens
        )

        self.reply_suggestion_temperature = (
            settings.reply_suggestion_temperature
        )

        self.retry_executor = RetryExecutor(
            RetryPolicy(
                max_attempts=settings.llm_max_retries + 1,
            )
        )

    def analyze_ticket(
        self,
        request: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:
        """
        Analyze a support ticket and return validated structured output.
        """

        try:
            return self.retry_executor.execute(
                self._analyze_ticket_once,
                request,
                retry_on=(RetryableLLMError,),
                operation_name="groq_ticket_analysis",
            )

        except RetryExhaustedError as exc:
            self._raise_retry_cause_or_provider_error(
                exc=exc,
                fallback_message=(
                    "Groq ticket analysis failed after retries."
                ),
            )

    def generate_reply_suggestion(
        self,
        request: ReplySuggestionRequest,
    ) -> ReplySuggestionResponse:
        """
        Generate a customer-support reply draft for human review.
        """

        try:
            return self.retry_executor.execute(
                self._generate_reply_suggestion_once,
                request,
                retry_on=(RetryableLLMError,),
                operation_name="groq_reply_suggestion",
            )

        except RetryExhaustedError as exc:
            self._raise_retry_cause_or_provider_error(
                exc=exc,
                fallback_message=(
                    "Groq reply suggestion failed after retries."
                ),
            )

    def _analyze_ticket_once(
        self,
        request: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:
        email = request.email

        user_prompt = (
            self.ticket_analysis_prompt.user_prompt_builder(
                sender_name=email.sender_name,
                sender_email=str(email.sender_email),
                subject=email.subject,
                body=email.body,
                attachment_text=request.attachment_text,
            )
        )

        completion = self._create_completion(
            system_prompt=self.ticket_analysis_prompt.system_prompt,
            user_prompt=user_prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={
                "type": "json_object",
            },
        )

        content = self._extract_completion_content(completion)

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

    def _generate_reply_suggestion_once(
        self,
        request: ReplySuggestionRequest,
    ) -> ReplySuggestionResponse:
        user_prompt = (
            self.reply_suggestion_prompt.user_prompt_builder(request)
        )

        completion = self._create_completion(
            system_prompt=self.reply_suggestion_prompt.system_prompt,
            user_prompt=user_prompt,
            temperature=self.reply_suggestion_temperature,
            max_tokens=self.reply_suggestion_max_tokens,
        )

        content = self._extract_completion_content(completion)

        try:
            return ReplySuggestionResponse(
                suggested_reply=content,
            )

        except ValidationError as exc:
            raise LLMResponseError(
                "Groq response violated the reply suggestion schema.",
                context={
                    "validation_errors": exc.errors(),
                },
            ) from exc

    def _create_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        response_format: dict[str, str] | None = None,
    ):
        """
        Execute one Groq completion request and map provider failures into
        application-level typed LLM exceptions.

        Retry decisions are intentionally not made here.
        """

        request_kwargs = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        if response_format is not None:
            request_kwargs["response_format"] = response_format

        try:
            return self.client.chat.completions.create(
                **request_kwargs
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
                (
                    "Groq rejected the request with HTTP status "
                    f"{exc.status_code}."
                ),
                context={
                    "status_code": exc.status_code,
                },
            ) from exc

    @staticmethod
    def _extract_completion_content(completion) -> str:
        """
        Extract non-empty text content from a Groq completion.
        """

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

        return content

    @staticmethod
    def _raise_retry_cause_or_provider_error(
        *,
        exc: RetryExhaustedError,
        fallback_message: str,
    ) -> None:
        """
        Preserve the typed retryable LLM failure after retry exhaustion.
        """

        cause = exc.__cause__

        if isinstance(cause, RetryableLLMError):
            raise cause

        raise LLMProviderError(
            fallback_message
        ) from exc
