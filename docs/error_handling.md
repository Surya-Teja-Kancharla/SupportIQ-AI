# Error Handling

## Overview

SupportIQ-AI uses centralized error handling to provide predictable API responses, preserve useful debugging context, prevent sensitive information leakage, and maintain consistent application behavior.

The error-handling strategy covers:

* Domain and service-layer exceptions.
* Authentication and authorization failures.
* Request validation errors.
* Database failures.
* External service failures.
* AI provider failures.
* Email ingestion and SMTP failures.
* Background job failures.
* Unexpected internal errors.

---

## Error-Handling Principles

Application code should follow these principles:

1. Raise specific exceptions instead of generic `Exception` instances.
2. Convert known application exceptions into standardized API responses.
3. Log unexpected failures with traceback information.
4. Never expose stack traces, credentials, tokens, SQL statements, or internal infrastructure details to API clients.
5. Preserve exception chaining with `raise ... from exc`.
6. Retry only transient failures.
7. Avoid silently suppressing failures.
8. Include request or correlation identifiers when available.

---

## Error Categories

### Validation Errors

Validation errors occur when client input violates API contracts.

Examples:

```text
Missing required fields
Invalid email address
Invalid ticket status
Unsupported priority value
Malformed pagination parameters
```

Recommended HTTP status:

```text
422 Unprocessable Entity
```

---

### Authentication Errors

Authentication errors occur when credentials are missing, invalid, or expired.

Examples:

```text
Missing bearer token
Invalid JWT
Expired JWT
Invalid login credentials
```

Recommended HTTP status:

```text
401 Unauthorized
```

Authentication failures should not reveal whether a specific account exists.

---

### Authorization Errors

Authorization errors occur when an authenticated user does not have permission to perform an operation.

Examples:

```text
Agent accessing an admin-only endpoint
Viewer attempting to modify a ticket
User accessing a restricted resource
```

Recommended HTTP status:

```text
403 Forbidden
```

---

### Resource Not Found Errors

Raised when a requested resource does not exist.

Examples:

```text
Ticket not found
User not found
Reply suggestion not found
Background job not found
```

Recommended HTTP status:

```text
404 Not Found
```

---

### Conflict Errors

Raised when an operation conflicts with existing state.

Examples:

```text
Duplicate user email
Duplicate external ticket identifier
Duplicate external message identifier
Invalid state transition
```

Recommended HTTP status:

```text
409 Conflict
```

---

### Rate-Limit Errors

Raised when a client exceeds configured API limits.

Recommended HTTP status:

```text
429 Too Many Requests
```

Responses may include:

```text
Retry-After
```

when a meaningful retry interval is available.

---

### External Service Errors

External integrations may fail because of:

```text
Connection failures
Timeouts
Provider rate limits
Authentication failures
Malformed provider responses
Temporary provider outages
```

Examples of integrations:

```text
Groq LLM API
SMTP server
IMAP email server
External ticket providers
```

External provider exceptions should be translated into application-level exceptions before reaching API routes.

Recommended HTTP statuses:

```text
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout
```

depending on the failure type.

---

### Database Errors

Database errors may include:

```text
Connection failures
Transaction failures
Constraint violations
Serialization failures
Timeouts
```

Database exceptions should not be returned directly to clients.

Integrity violations caused by user input may become:

```text
409 Conflict
```

Infrastructure failures should normally become:

```text
503 Service Unavailable
```

or:

```text
500 Internal Server Error
```

depending on whether the failure is expected to be temporary.

---

### Internal Errors

Unexpected application failures should return:

```text
500 Internal Server Error
```

The client response must contain a generic message.

Example:

```json
{
  "error": {
    "code": "internal_server_error",
    "message": "An unexpected internal error occurred."
  }
}
```

The complete exception traceback should be recorded only in server logs.

---

## Standard Error Response

SupportIQ-AI APIs should return errors using a consistent envelope.

Example:

```json
{
  "error": {
    "code": "ticket_not_found",
    "message": "The requested ticket was not found.",
    "details": null,
    "request_id": "req_123456"
  }
}
```

Fields:

| Field        | Description                              |
| ------------ | ---------------------------------------- |
| `code`       | Stable machine-readable error identifier |
| `message`    | Safe human-readable description          |
| `details`    | Optional structured validation metadata  |
| `request_id` | Request or correlation identifier        |

Clients should depend on `code`, not on the exact text of `message`.

---

## Application Exception Hierarchy

Recommended exception hierarchy:

```text
SupportIQError
|
+-- ValidationError
|
+-- AuthenticationError
|
+-- AuthorizationError
|
+-- ResourceNotFoundError
|
+-- ConflictError
|
+-- RateLimitError
|
+-- ExternalServiceError
|   |
|   +-- LLMServiceError
|   |
|   +-- EmailServiceError
|   |
|   +-- SMTPServiceError
|
+-- DatabaseServiceError
|
+-- BackgroundJobError
```

---

## Service-Layer Pattern

Services should raise application exceptions.

Example:

```python
def get_ticket(ticket_id: int) -> Ticket:
    ticket = repository.get_by_id(ticket_id)

    if ticket is None:
        raise ResourceNotFoundError(
            code="ticket_not_found",
            message="The requested ticket was not found.",
        )

    return ticket
```

Routes should not contain repeated low-level exception conversion logic.

---

## External Provider Pattern

Low-level provider exceptions should be translated into domain-specific exceptions.

Example:

```python
try:
    response = llm_client.generate(prompt)

except TimeoutError as exc:
    logger.warning(
        "LLM provider request timed out",
        exc_info=True,
    )

    raise LLMServiceError(
        code="llm_timeout",
        message="The AI service timed out.",
    ) from exc

except Exception as exc:
    logger.exception(
        "Unexpected LLM provider failure"
    )

    raise LLMServiceError(
        code="llm_service_unavailable",
        message="The AI service is temporarily unavailable.",
    ) from exc
```

---

## Database Transaction Pattern

Database operations should explicitly handle rollback.

Example:

```python
try:
    repository.create(ticket)

    session.commit()

except IntegrityError as exc:
    session.rollback()

    raise ConflictError(
        code="database_conflict",
        message="The operation conflicts with existing data.",
    ) from exc

except SQLAlchemyError as exc:
    session.rollback()

    logger.exception(
        "Database operation failed"
    )

    raise DatabaseServiceError(
        code="database_unavailable",
        message="The database operation could not be completed.",
    ) from exc
```

---

## Background Job Failures

Background jobs should record:

```text
Job identifier
Job type
Failure category
Safe error message
Retry count
Start timestamp
Completion timestamp
```

Transient failures may be retried using bounded exponential backoff.

Permanent failures should be marked as:

```text
failed
```

Jobs must not retry indefinitely.

---

## Logging Errors

Expected application errors should normally use:

```text
INFO
WARNING
```

Unexpected failures should normally use:

```text
ERROR
CRITICAL
```

Use:

```python
logger.exception(...)
```

inside exception handlers when traceback information is required.

Logs must not contain:

```text
Passwords
JWT tokens
API keys
SMTP credentials
Database passwords
Full authentication headers
Sensitive customer message contents unless explicitly required and protected
```

---

## Testing Error Handling

Tests should verify:

* Correct HTTP status code.
* Stable machine-readable error code.
* Safe client-facing message.
* Expected error response structure.
* Internal exceptions do not leak into responses.
* Database transactions roll back after failures.
* External provider failures are translated correctly.
* Retryable failures are retried only within configured limits.
* Unexpected exceptions return a generic 500 response.
* Request identifiers are included when supported.

---

## Error-Handling Checklist

Before completing an endpoint or service:

* Input validation is defined.
* Known failure modes use specific exception types.
* Service exceptions are converted consistently.
* Database rollback occurs after failed transactions.
* External service errors are translated.
* Retry logic is bounded.
* Unexpected failures are logged with traceback context.
* Client responses contain no sensitive internal information.
* Tests cover success and failure paths.
