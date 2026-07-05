from typing import Any


class SupportIQError(Exception):
    """Base exception for all SupportIQ AI application errors."""

    default_message = "An unexpected SupportIQ AI error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.context = context or {}

        super().__init__(self.message)


# ============================================================
# Configuration Exceptions
# ============================================================


class ConfigurationError(SupportIQError):
    """Raised when application configuration is invalid."""

    default_message = "Application configuration is invalid."


# ============================================================
# Email Exceptions
# ============================================================


class EmailError(SupportIQError):
    """Base exception for all email-related failures."""

    default_message = "An email operation failed."


class EmailConnectionError(EmailError):
    """Raised when an email server connection cannot be established."""

    default_message = "Unable to connect to the email server."


class EmailAuthenticationError(EmailError):
    """Raised when email server authentication fails."""

    default_message = "Email server authentication failed."


class MailboxSelectionError(EmailError):
    """Raised when the configured mailbox cannot be selected."""

    default_message = "Unable to select the configured mailbox."


class EmailFetchError(EmailError):
    """Raised when email retrieval or IMAP flag updates fail."""

    default_message = "Unable to fetch email messages."


class EmailParsingError(EmailError):
    """Raised when an email message cannot be parsed."""

    default_message = "Unable to parse an email message."


class InvalidSenderError(EmailParsingError):
    """Raised when an email sender address is invalid."""

    default_message = "The email sender address is invalid."


# ============================================================
# Attachment Exceptions
# ============================================================


class AttachmentError(EmailError):
    """Base exception for attachment-related failures."""

    default_message = "Attachment processing failed."


class AttachmentValidationError(AttachmentError):
    """Raised when attachment validation fails."""

    default_message = "Attachment validation failed."


class AttachmentStorageError(AttachmentError):
    """Raised when attachment persistence fails."""

    default_message = "Attachment storage failed."


# ============================================================
# SMTP Exceptions
# ============================================================


class SMTPError(EmailError):
    """Base exception for SMTP-related failures."""

    default_message = "Unable to send email."


class SMTPConnectionError(SMTPError):
    """Raised when an SMTP connection cannot be established."""

    default_message = "Unable to connect to the SMTP server."


class SMTPAuthenticationError(SMTPError):
    """Raised when SMTP authentication fails."""

    default_message = "SMTP authentication failed."


class SMTPSendError(SMTPError):
    """Raised when SMTP message delivery fails."""

    default_message = "SMTP message delivery failed."


# ============================================================
# Retry Exceptions
# ============================================================


class RetryableError(SupportIQError):
    """Base exception for operations that may safely be retried."""

    default_message = "A retryable operation failed."


class RetryExhaustedError(SupportIQError):
    """Raised after all configured retry attempts are exhausted."""

    default_message = (
        "The operation failed after exhausting all retries."
    )

# ============================================================
# LLM Exceptions
# ============================================================


class LLMError(SupportIQError):
    """Base exception for all LLM-related failures."""

    default_message = "An LLM operation failed."


class LLMConfigurationError(LLMError):
    """Raised when the LLM provider configuration is invalid."""

    default_message = "LLM provider configuration is invalid."


class LLMAuthenticationError(LLMError):
    """Raised when LLM provider authentication fails."""

    default_message = "LLM provider authentication failed."


class RetryableLLMError(LLMError, RetryableError):
    """Base exception for transient LLM failures."""

    default_message = "A retryable LLM operation failed."


class LLMTimeoutError(RetryableLLMError):
    """Raised when the LLM provider request times out."""

    default_message = "The LLM provider request timed out."


class LLMRateLimitError(RetryableLLMError):
    """Raised when the LLM provider rate limit is exceeded."""

    default_message = "The LLM provider rate limit was exceeded."


class LLMProviderError(RetryableLLMError):
    """Raised for transient LLM provider-side failures."""

    default_message = "The LLM provider operation failed."


class LLMResponseError(LLMError):
    """Raised when the provider returns an unusable response."""

    default_message = "The LLM provider returned an unusable response."


class LLMJSONExtractionError(LLMResponseError):
    """Raised when valid JSON cannot be extracted."""

    default_message = "Valid JSON could not be extracted from the LLM response."

class LLMRequestError(LLMError):
    """Raised when the provider rejects a non-retryable request."""

    default_message = "The LLM provider rejected the request."
