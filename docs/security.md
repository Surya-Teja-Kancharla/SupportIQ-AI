# Security

## Overview

SupportIQ-AI applies defense-in-depth security controls across authentication, authorization, API boundaries, database access, AI integrations, email processing, logging, background jobs, configuration, and deployment.

Security controls should be enforced by application code, infrastructure configuration, and operational procedures.

---

## Security Principles

SupportIQ-AI follows these principles:

1. Least privilege.
2. Secure defaults.
3. Explicit authorization.
4. Defense in depth.
5. Input validation at trust boundaries.
6. Secret separation from source code.
7. Minimal exposure of sensitive information.
8. Auditable security-sensitive actions.
9. Dependency and configuration hygiene.
10. Fail securely.

---

## Authentication

SupportIQ-AI uses token-based authentication.

JWT access tokens should:

* Be signed using a strong secret or asymmetric key.
* Have a short expiration time.
* Validate signature and expiration.
* Validate issuer and audience when configured.
* Reject unsupported algorithms.
* Avoid storing sensitive data in token claims.

Passwords must never be stored in plaintext.

Passwords should be hashed using a password-hashing algorithm designed for credential storage, such as:

```text
Argon2
bcrypt
```

Authentication responses should not reveal whether a particular user account exists.

---

## Authorization

Authentication establishes identity.

Authorization determines permitted actions.

SupportIQ-AI roles may include:

```text
admin
agent
viewer
```

Authorization must be enforced server-side.

Example permission model:

| Operation                  | Admin | Agent | Viewer |
| -------------------------- | ----- | ----- | ------ |
| View tickets               | Yes   | Yes   | Yes    |
| Update tickets             | Yes   | Yes   | No     |
| Generate reply suggestions | Yes   | Yes   | No     |
| View analytics             | Yes   | Yes   | Yes    |
| Manage users               | Yes   | No    | No     |
| View security audit data   | Yes   | No    | No     |

Frontend controls must never be treated as authorization enforcement.

---

## Secret Management

Secrets must not be committed to Git.

Examples:

```text
JWT secret keys
Groq API keys
Database credentials
SMTP passwords
IMAP passwords
Third-party access tokens
```

Secrets should be provided through:

```text
Environment variables
Deployment secret stores
CI/CD secret managers
Cloud secret-management services
```

A `.env.example` file may document required configuration keys but must contain placeholder values only.

Production secrets should be rotated periodically and immediately after suspected exposure.

---

## Input Validation

All external input must be considered untrusted.

Input sources include:

```text
HTTP request bodies
Query parameters
Path parameters
Headers
Email messages
External ticket payloads
AI model output
Background job payloads
Database-imported data
```

Validation should enforce:

```text
Required fields
Type constraints
Length limits
Allowed enumerations
Numeric bounds
Email format
Pagination bounds
Payload size limits
```

AI-generated output must be validated before being stored or used in application workflows.

---

## SQL Injection Prevention

Database queries should use:

```text
SQLAlchemy ORM
SQLAlchemy parameterized queries
Database driver parameter binding
```

Application code must not construct SQL queries through untrusted string concatenation.

Unsafe example:

```python
query = f"SELECT * FROM users WHERE email = '{email}'"
```

Preferred pattern:

```python
user = (
    session.query(User)
    .filter(User.email == email)
    .first()
)
```

---

## Cross-Site Scripting

API responses and frontend rendering must treat customer-controlled content as untrusted.

Customer email content, ticket subjects, AI-generated replies, and external provider data must be escaped or safely rendered by the frontend.

Avoid rendering untrusted HTML directly.

If HTML rendering is required, use a well-maintained HTML sanitizer with a strict allowlist.

---

## Cross-Site Request Forgery

Bearer-token APIs that do not use browser cookies for authentication have lower CSRF exposure.

If authentication tokens are stored in cookies:

* Use `HttpOnly`.
* Use `Secure`.
* Configure an appropriate `SameSite` policy.
* Implement CSRF protection for state-changing requests.

---

## CORS

Production CORS configuration should explicitly list trusted frontend origins.

Avoid:

```text
Access-Control-Allow-Origin: *
```

for authenticated production APIs.

Only required HTTP methods and headers should be permitted.

---

## Rate Limiting

Rate limiting should protect:

```text
Login endpoints
AI-generation endpoints
Email ingestion endpoints
Expensive analytics endpoints
Administrative APIs
```

Rate limits may be applied by:

```text
Reverse proxy
API gateway
Application middleware
Distributed rate-limit storage
```

Rate-limit responses should use:

```text
429 Too Many Requests
```

---

## JWT Security

JWT implementations should:

* Explicitly configure accepted algorithms.
* Reject unsigned tokens.
* Validate expiration.
* Validate `nbf` when used.
* Validate issuer and audience when configured.
* Use sufficiently strong signing keys.
* Avoid logging complete tokens.
* Keep access-token lifetimes limited.

Long-lived credentials should use refresh-token rotation and revocation mechanisms when refresh tokens are introduced.

---

## AI and LLM Security

LLM integrations introduce additional trust boundaries.

SupportIQ-AI should protect against:

```text
Prompt injection
Untrusted instructions embedded in customer emails
Malformed structured model output
Sensitive data disclosure
Unbounded model input
Unexpected model responses
Provider outages
Excessive AI API consumption
```

Customer-provided content must be clearly separated from system instructions when constructing prompts.

AI output must not directly execute:

```text
SQL statements
Shell commands
Application code
Administrative actions
External API requests
```

without explicit validation and authorization.

AI-generated classifications and reply suggestions should be treated as untrusted application data.

---

## Email Security

Inbound emails are untrusted external input.

Email processing should:

* Enforce message size limits.
* Validate sender and recipient formats.
* Safely parse MIME content.
* Avoid executing attachments.
* Reject or isolate malformed messages.
* Sanitize HTML before rendering.
* Prevent duplicate ingestion using external message identifiers.
* Avoid logging complete email bodies unnecessarily.

SMTP credentials must be stored as secrets.

Outbound email headers must be protected against header injection.

---

## Database Security

Database security controls should include:

* Dedicated application database credentials.
* Least-privilege database roles.
* TLS for remote database connections.
* No public database exposure.
* Regular backups.
* Tested restore procedures.
* Migration access restricted to authorized deployment processes.
* Parameterized database queries.
* Database connection limits and timeouts.

Production applications should not connect using database superuser accounts.

---

## Logging Security

Logs must not expose secrets.

Do not log:

```text
Passwords
Password hashes
JWT tokens
Authorization headers
API keys
Database credentials
SMTP credentials
IMAP credentials
Private encryption keys
```

Sensitive customer information should be minimized or redacted.

Security-sensitive events should include enough context for investigation without exposing credentials.

---

## Audit Logging

Audit events should be recorded for security-sensitive operations.

Examples:

```text
Successful login
Failed login
User creation
User deactivation
Role changes
Ticket assignment changes
Administrative operations
Repeated authorization failures
Security configuration changes
```

Recommended audit fields:

```text
Actor user identifier
Event type
Resource type
Resource identifier
Source IP address
Timestamp
Structured metadata
```

Audit records should be append-only from normal application workflows.

---

## Background Job Security

Background workers must:

* Validate job payloads.
* Reject unknown job types.
* Use least-privilege credentials.
* Enforce retry limits.
* Avoid storing secrets in job payloads.
* Prevent sensitive exception information from leaking into persisted error messages.
* Authenticate access to job administration endpoints.

---

## Dependency Security

Dependencies should be pinned or constrained to known-compatible versions.

Security checks should include:

```bash
pip-audit

bandit -r app
```

Outdated dependencies should be reviewed regularly.

Dependency updates should be tested before production deployment.

---

## HTTP Security Headers

Production deployments should configure appropriate HTTP security headers.

Recommended headers include:

```text
Strict-Transport-Security
X-Content-Type-Options
Content-Security-Policy
Referrer-Policy
Permissions-Policy
```

Headers may be configured by the application, reverse proxy, API gateway, or frontend hosting layer.

---

## TLS

Production traffic must use HTTPS.

Plain HTTP should redirect to HTTPS.

TLS certificates should be automatically renewed where possible.

Internal service-to-service communication should use encryption when crossing untrusted networks.

---

## File and Attachment Handling

If SupportIQ-AI introduces attachment processing:

* Enforce maximum file sizes.
* Validate actual file types instead of trusting extensions.
* Generate server-side storage names.
* Store files outside executable directories.
* Prevent path traversal.
* Scan files when appropriate.
* Never execute uploaded files.
* Restrict download authorization.

---

## Configuration Security

Production configuration must:

* Disable debug mode.
* Use environment-specific secrets.
* Restrict allowed hosts.
* Restrict CORS origins.
* Configure secure token expiration.
* Configure database connection timeouts.
* Configure outbound service timeouts.
* Enable structured security logging.
* Avoid exposing internal exception details.

---

## Security Testing

Security verification should include:

```bash
bandit -r app

pip-audit
```

Application tests should verify:

* Protected routes reject unauthenticated requests.
* Role restrictions are enforced.
* Invalid JWTs are rejected.
* Expired JWTs are rejected.
* Malformed input is rejected.
* SQL injection payloads are safely handled.
* Sensitive data is absent from error responses.
* Secrets are absent from logs.
* Rate limits work as configured.
* Duplicate email ingestion is prevented.
* AI output is validated before persistence.
* Administrative routes enforce elevated permissions.

---

## Incident Response

If a security incident is suspected:

1. Preserve relevant logs and evidence.
2. Identify affected systems and credentials.
3. Revoke or rotate exposed secrets.
4. Restrict compromised access.
5. Determine the scope of affected data.
6. Patch the root cause.
7. Restore services safely.
8. Document the incident and corrective actions.
9. Add regression tests or monitoring to prevent recurrence.

---

## Production Security Checklist

Before deployment:

* Debug mode is disabled.
* HTTPS is enforced.
* Production secrets are not stored in Git.
* JWT signing keys are strong and protected.
* CORS origins are explicitly configured.
* Authentication is required for protected endpoints.
* Authorization is enforced server-side.
* Rate limiting protects sensitive endpoints.
* Database credentials follow least privilege.
* Database connections use encryption where required.
* Logs do not expose secrets.
* Audit events are persisted.
* AI input and output boundaries are validated.
* Email content is handled as untrusted input.
* Background jobs validate payloads and enforce retry limits.
* Dependency security checks pass.
* Security-focused tests pass.
