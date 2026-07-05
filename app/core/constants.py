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

class TicketStatus:
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_CUSTOMER = "WAITING_FOR_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class AuditAction:
    TICKET_CREATED = "TICKET_CREATED"
    CATEGORY_CHANGED = "CATEGORY_CHANGED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    TEAM_REASSIGNED = "TEAM_REASSIGNED"
    STATUS_CHANGED = "STATUS_CHANGED"
    NOTE_ADDED = "NOTE_ADDED"
    REPLY_REGENERATED = "REPLY_REGENERATED"
    SUGGESTED_REPLY_REGENERATED = "SUGGESTED_REPLY_REGENERATED"
    ACKNOWLEDGEMENT_SENT = "ACKNOWLEDGEMENT_SENT"
    SUGGESTED_REPLY_EDITED = "SUGGESTED_REPLY_EDITED"
    INTERNAL_NOTE_ADDED = "INTERNAL_NOTE_ADDED"
