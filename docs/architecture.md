# SupportIQ Architecture

## 1. Overview

SupportIQ is an AI-assisted customer-support ticket processing system.

The application ingests customer-support emails, parses message content and attachments, analyzes ticket information using an external LLM service, normalizes and validates AI output, applies deterministic business rules, persists tickets and workflow execution records, generates reply suggestions, sends acknowledgements, exposes operational APIs and dashboard views, and supports failure recovery and manual review.

SupportIQ is implemented as a modular monolith.

Internal modules separate API delivery, orchestration, business rules, persistence, AI integration, evaluation, monitoring, and failure recovery.

The architecture prioritizes:

* Explicit service boundaries.
* Deterministic business rules after AI inference.
* Schema validation of AI-generated data.
* Repository-based persistence.
* Application-controlled transaction boundaries.
* Workflow execution tracking.
* Auditability.
* Retry and dead-letter recovery.
* Prompt versioning.
* Testability.
* Operational visibility.

---

## 2. Architectural Style

SupportIQ uses a layered modular-monolith architecture.

```text
External Systems
        |
        v
Integration Layer
        |
        v
Workflow Orchestration Layer
        |
        v
Domain and Application Services
        |
        v
Repository Layer
        |
        v
Relational Database
```

Internal separation is maintained through Python packages:

```text
app/
├── api/
├── config/
├── core/
├── database/
├── evaluation/
├── models/
├── prompts/
├── repositories/
├── schemas/
├── services/
└── utils/
```

This architecture avoids premature distributed-system complexity while maintaining clear module boundaries and extension points for future architectural evolution.

---

## 3. Architecture Diagram

```text
                         +---------------------------+
                         |       External Systems    |
                         |---------------------------|
                         | IMAP Server               |
                         | SMTP Server               |
                         | External LLM Provider     |
                         +-------------+-------------+
                                       |
                                       v
                         +---------------------------+
                         |     Integration Layer     |
                         |---------------------------|
                         | IMAP Service              |
                         | SMTP Service              |
                         | Groq LLM Service          |
                         | Email Parser              |
                         | Attachment Service        |
                         +-------------+-------------+
                                       |
                                       v
                         +---------------------------+
                         | Workflow Orchestration    |
                         |---------------------------|
                         | Email Ingestion Service   |
                         | Workflow Service          |
                         | Workflow Execution Service|
                         +-------------+-------------+
                                       |
                                       v
              +------------------------------------------------+
              |          Domain and Application Services        |
              |------------------------------------------------|
              | Ticket Analysis Normalizer                     |
              | Priority Service                               |
              | Routing Service                                |
              | Reply Suggestion Service                       |
              | Ticket Service                                 |
              | Ticket Lifecycle Service                       |
              | Acknowledgement Service                        |
              | Manual Review Service                          |
              | Failure Handling Service                       |
              | Failure Recovery Service                       |
              | Monitoring Service                             |
              | Dashboard Service                              |
              +------------------------+-----------------------+
                                       |
                                       v
                         +---------------------------+
                         |      Repository Layer     |
                         |---------------------------|
                         | Ticket Repository         |
                         | Attachment Repository     |
                         | Audit Repository          |
                         | Internal Note Repository  |
                         | Workflow Execution Repo   |
                         | Dead Letter Repository    |
                         +-------------+-------------+
                                       |
                                       v
                         +---------------------------+
                         |    Relational Database    |
                         |---------------------------|
                         | Tickets                   |
                         | Attachments               |
                         | Audit Logs                |
                         | Internal Notes            |
                         | Workflow Executions       |
                         | Dead Letter Records       |
                         +---------------------------+

Additional Cross-Cutting Components:

+----------------------+  +----------------------+  +----------------------+
| Configuration        |  | Prompt Management    |  | Evaluation           |
|----------------------|  |----------------------|  |----------------------|
| Settings             |  | Prompt Registry      |  | Classification Eval  |
| Priority Rules       |  | Ticket Analysis v1   |  | Metrics              |
| Routing Rules        |  | Reply Suggestion v1  |  | AI Evaluation        |
| Acknowledgement Rules|  | Prompt Versions      |  | Evaluation Reports   |
+----------------------+  +----------------------+  +----------------------+
```

---

## 4. Application Entry Point

The application entry point is:

```text
main.py
```

The entry point is responsible for application startup and composition.

Application dependencies are assembled from:

* Configuration.
* Database sessions.
* Repositories.
* External integration services.
* Domain services.
* Workflow services.
* API routes.

The application uses explicit dependency construction rather than hiding core workflow dependencies behind global state.

---

## 5. API and Presentation Layer

The API layer is located in:

```text
app/api/
```

Implemented route modules include:

```text
dashboard_routes.py
monitoring_routes.py
manual_review_routes.py
failure_recovery_routes.py
dependencies.py
```

The API layer is responsible for:

* Receiving HTTP requests.
* Resolving application dependencies.
* Validating request data.
* Calling application services.
* Returning response schemas or rendered views.

Business rules should remain in services rather than route handlers.

The dashboard presentation layer also uses:

```text
app/templates/
app/static/
```

These components provide server-rendered ticket views and dashboard styling.

---

## 6. Integration Layer

The integration layer communicates with external systems.

### IMAP Integration

```text
app/services/imap_service.py
```

Responsibilities include:

* Connecting to the configured mailbox.
* Retrieving email messages.
* Managing mailbox operations.
* Applying retry behavior to transient failures.

### SMTP Integration

```text
app/services/smtp_service.py
```

Responsibilities include:

* Establishing SMTP connections.
* Sending acknowledgement emails.
* Handling transport failures.
* Applying retry behavior where configured.

### External LLM Integration

```text
app/services/groq_llm_service.py
```

Responsibilities include:

* Sending prompts to the configured LLM provider.
* Receiving model responses.
* Extracting structured model output.
* Handling provider failures.
* Applying retry behavior.

External LLM output is not treated as trusted application state.

The output passes through extraction, schema validation, normalization, and deterministic business-rule processing.

### Email Parsing

```text
app/services/email_parser.py
```

Responsibilities include:

* Parsing email headers.
* Extracting sender information.
* Extracting subject and body content.
* Handling multipart email structures.
* Falling back from plain text to HTML-derived content when necessary.
* Identifying attachments.

### Attachment Processing

```text
app/services/attachment_service.py
```

Responsibilities include:

* Validating attachment metadata.
* Persisting supported attachment files.
* Generating safe storage paths.
* Returning attachment information for downstream ticket persistence.

---

## 7. Workflow Orchestration Layer

The workflow layer coordinates the end-to-end ticket-processing pipeline.

Important services include:

```text
email_ingestion_service.py
workflow_service.py
workflow_execution_service.py
```

### Email Ingestion Service

The email ingestion service coordinates mailbox-level processing.

Responsibilities include:

* Retrieving messages.
* Processing messages independently.
* Parsing email content.
* Invoking the ticket-processing workflow.
* Isolating failures between messages.
* Managing message-level success and failure behavior.

### Workflow Service

The workflow service coordinates ticket-processing stages.

Conceptually:

```text
Parsed Email
    |
    v
AI Ticket Analysis
    |
    v
Output Normalization
    |
    v
Priority Decision
    |
    v
Routing Decision
    |
    v
Reply Suggestion
    |
    v
Ticket Persistence
    |
    v
Acknowledgement Processing
```

The workflow service is responsible for orchestration.

Individual business decisions remain delegated to specialized services.

### Workflow Execution Service

The workflow execution service records workflow processing state.

Responsibilities include:

* Creating workflow execution records.
* Recording workflow progress.
* Tracking successful execution.
* Tracking failed execution.
* Recording retry lineage.
* Supporting monitoring and recovery workflows.

---

## 8. Domain and Application Services

Business behavior is separated into focused services.

### Ticket Analysis Normalizer

```text
ticket_analysis_normalizer.py
```

Converts AI-generated ticket analysis into validated normalized application data.

Responsibilities include:

* Category normalization.
* Priority normalization.
* Sentiment normalization.
* Department normalization.
* Tag cleanup.
* Confidence-score clamping.
* Normalization metadata generation.

### Priority Service

```text
priority_service.py
```

Applies deterministic priority rules after AI analysis.

The final ticket priority is therefore not blindly copied from the external model response.

### Routing Service

```text
routing_service.py
```

Maps normalized ticket categories to configured support teams.

Routing rules are stored in:

```text
app/config/routing_rules.py
```

### Reply Suggestion Service

```text
reply_suggestion_service.py
```

Generates customer-support reply drafts for human review.

Generated replies are not automatically trusted as approved support responses.

### Ticket Service

```text
ticket_service.py
```

Creates the ticket persistence aggregate.

The service coordinates persistence of:

* Ticket records.
* Ticket attachments.
* Initial audit events.

The service deliberately does not own transaction commit or rollback.

### Ticket Lifecycle Service

```text
ticket_lifecycle_service.py
```

Enforces allowed ticket status transitions and records lifecycle audit events.

### Acknowledgement Service

```text
acknowledgement_service.py
```

Determines and performs acknowledgement behavior.

### Manual Review Service

```text
manual_review_service.py
```

Supports operator-driven ticket review operations, including internal notes and auditable ticket changes.

### Failure Handling Service

```text
failure_handling_service.py
```

Coordinates persistence of workflow failures.

### Failure Recovery Service

```text
failure_recovery_service.py
```

Supports retry and recovery of failed workflow executions and dead-letter records.

### Monitoring Service

```text
monitoring_service.py
```

Provides operational workflow metrics.

### Dashboard Service

```text
dashboard_service.py
```

Provides ticket data required by dashboard routes and views.

---

## 9. Repository Layer

Persistence access is separated into repository classes.

Implemented repositories include:

```text
attachment_repository.py
audit_repository.py
dead_letter_repository.py
internal_note_repository.py
ticket_repository.py
workflow_execution_repository.py
```

Repositories are responsible for database access operations.

Services coordinate business behavior.

Transaction ownership remains outside low-level repository operations where workflow-level atomicity is required.

---

## 10. Data Model Layer

SQLAlchemy ORM models are located in:

```text
app/models/
```

Implemented models include:

* `Ticket`
* `TicketAttachment`
* `TicketAuditLog`
* `InternalNote`
* `WorkflowExecution`
* `DeadLetterRecord`

The relational database provides durable storage for:

* Ticket state.
* Attachment metadata.
* Audit history.
* Internal notes.
* Workflow execution history.
* Failure and dead-letter records.

Database schema evolution is managed through Alembic migrations.

---

## 11. Schema Validation Layer

Pydantic schemas are located in:

```text
app/schemas/
```

Schemas provide validated boundaries for:

* Parsed emails.
* AI analysis.
* Normalized ticket analysis.
* Priority decisions.
* Routing decisions.
* Reply suggestions.
* Ticket workflow results.
* Ingestion results.
* Monitoring responses.
* Dashboard responses.
* Manual review operations.
* Failure recovery operations.
* Evaluation data.

Schema validation is especially important at AI and API trust boundaries.

---

## 12. Configuration and Deterministic Rules

Configuration modules are located in:

```text
app/config/
```

These modules define:

* Application settings.
* Priority rules.
* Routing rules.
* Acknowledgement rules.

Deterministic business behavior is separated from LLM inference.

This allows rules to be tested, audited, and changed independently from prompt behavior.

---

## 13. Prompt Management

Versioned prompts are located in:

```text
app/prompts/
```

The prompt registry provides explicit prompt definitions containing:

* Prompt name.
* Prompt version.
* System prompt.
* User-prompt builder.

Implemented prompt families include:

* `ticket-analysis-v1`
* `reply-suggestion-v1`

Prompt versioning improves reproducibility and provides a foundation for future prompt evaluation and migration.

---

## 14. Evaluation Architecture

Evaluation components are located in:

```text
app/evaluation/
```

SupportIQ provides:

* Deterministic classification evaluation.
* Evaluation metrics.
* AI-assisted qualitative evaluation.

Evaluation runs independently from the production mailbox-ingestion workflow.

This separation allows regression testing without requiring live email processing.

---

## 15. Failure Recovery Architecture

SupportIQ separates transient retries from durable workflow recovery.

```text
Transient External Failure
        |
        v
Retry Utility
        |
        +---- Success ----> Continue Workflow
        |
        v
Retry Exhaustion / Workflow Failure
        |
        v
Persist Failure State
        |
        v
Dead Letter Record
        |
        v
Manual Retry
        |
        v
New Workflow Execution
        |
        +---- Success ----> Resolve Dead Letter
        |
        +---- Failure ----> Reopen / Preserve Failure State
```

This design provides:

* Immediate retry for transient operations.
* Durable failure records.
* Workflow execution history.
* Manual recovery.
* Retry lineage.
* Operational observability.

---

## 16. Transaction Ownership

Repositories perform persistence operations.

Services construct and coordinate domain changes.

Workflow-level callers own transaction commit and rollback boundaries.

This design allows related operations to participate in one database transaction.

For example:

```text
Create Ticket
    |
    +--> Persist Ticket
    |
    +--> Persist Attachments
    |
    +--> Persist Initial Audit Event
    |
    v
Caller Commits Transaction
```

If a failure occurs before commit:

```text
Workflow Failure
    |
    v
Caller Rolls Back Transaction
    |
    v
Partial Ticket State Is Not Committed
```

Integration tests verify rollback behavior.

---

## 17. Trust Boundaries

SupportIQ contains several explicit trust boundaries.

### Customer Email Boundary

Customer-controlled content is untrusted.

Email bodies and attachment text may contain:

* Invalid data.
* Malicious instructions.
* Prompt-injection attempts.
* Unsupported claims.

### External LLM Boundary

LLM output is untrusted until:

```text
Response Extraction
        |
        v
Schema Validation
        |
        v
Normalization
        |
        v
Deterministic Business Rules
```

### API Boundary

Incoming API requests are validated before application-service execution.

### Database Boundary

Database access is isolated through repositories and application-controlled transactions.

### Operator Boundary

Manual review and recovery operations modify durable application state and must remain auditable.

---

## 18. Architectural Strengths

The implemented architecture provides:

* Clear module boundaries.
* Testable services.
* Repository-based persistence.
* Deterministic rules after AI inference.
* Explicit AI trust boundaries.
* Versioned prompts.
* Workflow execution tracking.
* Durable failure handling.
* Dead-letter recovery.
* Audit logging.
* Manual review capabilities.
* Evaluation infrastructure.
* High automated test coverage.

---

## 19. Current Architectural Limitations

The current implementation also has limitations.

### Single Application Process

The modular monolith does not independently scale workflow stages.

### Synchronous External Integrations

External email, SMTP, and LLM operations can occupy application execution time.

### Local Attachment Storage

Attachment files are stored locally rather than in distributed object storage.

### External Provider Dependency

Live AI operations depend on external LLM availability and credentials.

### Limited API Security Infrastructure

The project does not currently implement a complete production authentication, authorization, and rate-limiting architecture.

### No Distributed Queue

Workflow processing is not backed by a production message broker.

These limitations are acceptable for the current project scope and are documented for future architectural evolution.

---

## 20. Future Architecture Evolution

Potential future improvements include:

* Background worker processes.
* Durable message queues.
* Object storage for attachments.
* Horizontal workflow processing.
* Centralized secrets management.
* API authentication and authorization.
* Role-based access control.
* Rate limiting.
* Distributed tracing.
* Centralized metrics and alerting.
* LLM provider abstraction and failover.
* Prompt experiment tracking.
* Evaluation regression gates.
* Database read replicas.
* Cache layers for dashboard queries.

---

## 21. Summary

SupportIQ uses a layered modular-monolith architecture that separates external integrations, workflow orchestration, deterministic business services, repositories, schemas, prompts, evaluation, monitoring, and failure recovery.

The architecture deliberately treats customer input and AI-generated output as untrusted data.

Deterministic business rules, schema validation, explicit transaction boundaries, workflow execution tracking, audit records, dead-letter recovery, and automated tests provide reliability and traceability.

The current architecture is suitable for the project scope while maintaining clear extension points for future asynchronous processing, stronger API security, distributed storage, and production observability.
