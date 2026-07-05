from dataclasses import dataclass

from app.core.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMJSONExtractionError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)

MAX_SANITIZED_ERROR_LENGTH = 500


@dataclass(frozen=True)
class FailureClassification:
    exception_type: str
    retryable: bool
    sanitized_message: str


class FailureHandlingService:
    """
    Classifies workflow failures and produces safe persistence metadata.
    """

    RETRYABLE_EXCEPTIONS = (
        LLMTimeoutError,
        LLMRateLimitError,
        LLMProviderError,
        TimeoutError,
        ConnectionError,
    )

    NON_RETRYABLE_EXCEPTIONS = (
        LLMAuthenticationError,
        LLMConfigurationError,
        LLMJSONExtractionError,
        LLMResponseError,
        ValueError,
    )

    @staticmethod
    def sanitize_error_message(exc: Exception) -> str:
        message = str(exc).strip()

        if not message:
            message = exc.__class__.__name__

        sensitive_markers = (
            "api_key",
            "apikey",
            "password",
            "authorization",
            "bearer ",
            "secret",
            "token",
        )

        lowered_message = message.lower()

        if any(
            marker in lowered_message
            for marker in sensitive_markers
        ):
            return (
                "Failure message contained potentially sensitive "
                "information and was sanitized."
            )

        return message[:MAX_SANITIZED_ERROR_LENGTH]

    def classify(
        self,
        exc: Exception,
    ) -> FailureClassification:
        if isinstance(exc, self.RETRYABLE_EXCEPTIONS):
            retryable = True

        elif isinstance(exc, self.NON_RETRYABLE_EXCEPTIONS):
            retryable = False

        else:
            retryable = False

        return FailureClassification(
            exception_type=exc.__class__.__name__,
            retryable=retryable,
            sanitized_message=self.sanitize_error_message(exc),
        )
