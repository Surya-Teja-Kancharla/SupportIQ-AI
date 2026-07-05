from app.core.exceptions import LLMResponseError
from app.schemas.email_schema import ParsedEmail
from app.schemas.normalized_ticket_schema import NormalizedTicketAnalysis
from app.schemas.reply_suggestion_schema import (
    ReplySuggestionRequest,
    ReplySuggestionResponse,
)
from app.services.llm_service import LLMService
from app.utils.text_normalizer import normalize_text


class ReplySuggestionService:
    """
    Application service responsible for orchestrating AI-generated
    customer-support reply suggestions.

    Responsibilities:
    - construct the provider-independent reply-suggestion request,
    - call the provider-independent LLMService boundary,
    - validate the returned reply,
    - normalize reply whitespace deterministically,
    - enforce the maximum reply-length policy,
    - return an immutable ReplySuggestionResponse.

    This service does not:
    - call a concrete LLM provider directly,
    - persist reply suggestions,
    - send customer emails,
    - approve generated replies,
    - mutate the source email or normalized ticket analysis.
    """

    def __init__(
        self,
        llm_service: LLMService,
        *,
        max_reply_length: int = 4000,
    ) -> None:
        if max_reply_length <= 0:
            raise ValueError(
                "max_reply_length must be greater than zero."
            )

        self.llm_service = llm_service
        self.max_reply_length = max_reply_length

    def generate_suggestion(
        self,
        *,
        email: ParsedEmail,
        normalized_analysis: NormalizedTicketAnalysis,
    ) -> ReplySuggestionResponse:
        """
        Generate, validate, normalize, and enforce policy on an AI-generated
        customer-support reply suggestion.
        """

        request = self._build_request(
            email=email,
            normalized_analysis=normalized_analysis,
        )

        response = self.llm_service.generate_reply_suggestion(request)

        return self._process_response(response)

    @staticmethod
    def _build_request(
        *,
        email: ParsedEmail,
        normalized_analysis: NormalizedTicketAnalysis,
    ) -> ReplySuggestionRequest:
        """
        Construct the provider-independent reply-suggestion request.

        Only the customer context required by the reply-generation subsystem is
        copied from ParsedEmail.
        """

        return ReplySuggestionRequest(
            sender_email=str(email.sender_email),
            email_subject=email.subject,
            email_body=email.body,
            normalized_analysis=normalized_analysis,
        )

    def _process_response(
        self,
        response: ReplySuggestionResponse,
    ) -> ReplySuggestionResponse:
        """
        Normalize the provider response and enforce application-level policy.

        A new ReplySuggestionResponse is returned instead of mutating the
        provider response.
        """

        normalized_reply = normalize_text(
            response.suggested_reply
        )

        if not normalized_reply:
            raise LLMResponseError(
                "LLM returned an empty reply suggestion."
            )

        if len(normalized_reply) > self.max_reply_length:
            raise LLMResponseError(
                (
                    "LLM reply suggestion exceeded the maximum "
                    f"allowed length of {self.max_reply_length} characters."
                ),
                context={
                    "maximum_reply_length": self.max_reply_length,
                    "actual_reply_length": len(normalized_reply),
                },
            )

        return ReplySuggestionResponse(
            suggested_reply=normalized_reply,
        )
