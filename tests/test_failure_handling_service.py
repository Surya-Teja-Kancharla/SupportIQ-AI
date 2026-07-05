import pytest

from app.core.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMJSONExtractionError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)
from app.services.failure_handling_service import (
    MAX_SANITIZED_ERROR_LENGTH,
    FailureHandlingService,
)


@pytest.fixture
def service() -> FailureHandlingService:
    return FailureHandlingService()


@pytest.mark.parametrize(
    "exception",
    [
        LLMTimeoutError(),
        LLMRateLimitError(),
        LLMProviderError(),
        TimeoutError("operation timed out"),
        ConnectionError("connection unavailable"),
    ],
)
def test_retryable_failures_are_classified_as_retryable(
    service: FailureHandlingService,
    exception: Exception,
) -> None:
    result = service.classify(exception)

    assert result.retryable is True
    assert result.exception_type == type(exception).__name__
    assert result.sanitized_message


@pytest.mark.parametrize(
    "exception",
    [
        LLMAuthenticationError(),
        LLMConfigurationError(),
        LLMJSONExtractionError(),
        LLMResponseError(),
        ValueError("invalid input"),
    ],
)
def test_non_retryable_failures_are_classified_as_non_retryable(
    service: FailureHandlingService,
    exception: Exception,
) -> None:
    result = service.classify(exception)

    assert result.retryable is False
    assert result.exception_type == type(exception).__name__
    assert result.sanitized_message


def test_unknown_exception_defaults_to_non_retryable(
    service: FailureHandlingService,
) -> None:
    exception = RuntimeError(
        "unexpected workflow failure"
    )

    result = service.classify(exception)

    assert result.retryable is False
    assert result.exception_type == "RuntimeError"
    assert (
        result.sanitized_message
        == "unexpected workflow failure"
    )


@pytest.mark.parametrize(
    "message",
    [
        "api_key=secret-value",
        "apikey=secret-value",
        "password=super-secret",
        "Authorization: Bearer abc123",
        "Bearer abc123",
        "client_secret=secret-value",
        "access_token=secret-value",
    ],
)
def test_sensitive_messages_are_sanitized(
    service: FailureHandlingService,
    message: str,
) -> None:
    exception = RuntimeError(message)

    result = service.classify(exception)

    assert result.sanitized_message == (
        "Failure message contained potentially sensitive "
        "information and was sanitized."
    )

    assert message not in result.sanitized_message


def test_empty_error_message_uses_exception_type(
    service: FailureHandlingService,
) -> None:
    exception = RuntimeError()

    result = service.classify(exception)

    assert result.sanitized_message == "RuntimeError"


def test_error_message_is_truncated(
    service: FailureHandlingService,
) -> None:
    message = "x" * (
        MAX_SANITIZED_ERROR_LENGTH + 100
    )

    result = service.classify(
        RuntimeError(message)
    )

    assert (
        len(result.sanitized_message)
        == MAX_SANITIZED_ERROR_LENGTH
    )

    assert result.sanitized_message == (
        message[:MAX_SANITIZED_ERROR_LENGTH]
    )


def test_classification_preserves_exception_type(
    service: FailureHandlingService,
) -> None:
    exception = LLMTimeoutError(
        "provider timed out"
    )

    result = service.classify(exception)

    assert result.exception_type == "LLMTimeoutError"


def test_classification_preserves_safe_message(
    service: FailureHandlingService,
) -> None:
    exception = LLMProviderError(
        "provider temporarily unavailable"
    )

    result = service.classify(exception)

    assert result.sanitized_message == (
        "provider temporarily unavailable"
    )
