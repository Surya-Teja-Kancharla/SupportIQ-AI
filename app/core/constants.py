from enum import StrEnum


class ProcessingStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    SKIPPED = "skipped"


class FailureType(StrEnum):
    CONNECTION_ERROR = "connection_error"
    AUTHENTICATION_ERROR = "authentication_error"
    MAILBOX_ERROR = "mailbox_error"
    FETCH_ERROR = "fetch_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    ATTACHMENT_ERROR = "attachment_error"
    SMTP_ERROR = "smtp_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class EmailContentType(StrEnum):
    PLAIN_TEXT = "text/plain"
    HTML = "text/html"


class LogEvent(StrEnum):
    APPLICATION_STARTED = "application_started"

    IMAP_CONNECTION_STARTED = "imap_connection_started"
    IMAP_CONNECTION_SUCCEEDED = "imap_connection_succeeded"
    IMAP_CONNECTION_FAILED = "imap_connection_failed"

    EMAIL_FETCH_STARTED = "email_fetch_started"
    EMAIL_FETCH_SUCCEEDED = "email_fetch_succeeded"
    EMAIL_FETCH_FAILED = "email_fetch_failed"

    EMAIL_PROCESSING_STARTED = "email_processing_started"
    EMAIL_PROCESSING_SUCCEEDED = "email_processing_succeeded"
    EMAIL_PROCESSING_FAILED = "email_processing_failed"

    SMTP_SEND_STARTED = "smtp_send_started"
    SMTP_SEND_SUCCEEDED = "smtp_send_succeeded"
    SMTP_SEND_FAILED = "smtp_send_failed"

    RETRY_SCHEDULED = "retry_scheduled"
    RETRIES_EXHAUSTED = "retries_exhausted"
