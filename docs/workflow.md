# SupportIQ Workflow

## 1. Overview

SupportIQ processes customer-support emails through a multi-stage workflow that combines external integrations, AI-assisted analysis, deterministic business rules, transactional persistence, acknowledgement delivery, workflow execution tracking, audit logging, failure isolation, and durable recovery.

The primary workflow is:

```text
Mailbox Retrieval
        |
        v
Email Parsing
        |
        v
Attachment Processing
        |
        v
AI Ticket Analysis
        |
        v
Analysis Normalization
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
        |
        v
Workflow Completion
```

The workflow architecture follows several principles:

* Customer-controlled email content is untrusted.
* External LLM output is untrusted.
* AI output must pass schema validation and normalization.
* Priority and routing decisions are deterministic application decisions.
* Persistence operations participate in caller-controlled transactions.
* Workflow executions are tracked independently from ticket state.
* Failures are isolated between email messages.
* Transient failures may be retried.
* Exhausted workflow failures can be persisted for later recovery.
* Manual retry creates observable workflow execution lineage.
* Ticket changes are auditable.

---

## 2. Workflow Components

The primary workflow components are located in:

```text
app/services/
├── imap_service.py
├── email_ingestion_service.py
├── email_parser.py
├── attachment_service.py
├── workflow_service.py
├── groq_llm_service.py
├── ticket_analysis_normalizer.py
├── priority_service.py
├── routing_service.py
├── reply_suggestion_service.py
├── ticket_service.py
├── acknowledgement_service.py
├── smtp_service.py
├── workflow_execution_service.py
├── failure_handling_service.py
└── failure_recovery_service.py
```

Supporting components include:

```text
app/config/
app/core/
app/prompts/
app/repositories/
app/schemas/
```

The declarative workflow deliverable is stored at:

```text
workflow/workflow_definition.json
```

---

## 3. Workflow Diagram

The diagram represents the logical workflow.

Individual retry boundaries depend on the configured integration and workflow services.

```text
+-----------------------+
|    Mailbox Retrieval  |
|      IMAP Service     |
+-----------+-----------+
            |
            v
+-----------------------+
|     Email Parsing     |
|      Email Parser     |
+-----------+-----------+
            |
            v
+-----------------------+
| Attachment Processing |
|  Attachment Service   |
+-----------+-----------+
            |
            v
+-----------------------+
|   AI Ticket Analysis  |
|    Groq LLM Service   |
+-----------+-----------+
            |
            v
+-----------------------+
|  Response Extraction  |
|  + Schema Validation  |
+-----------+-----------+
            |
            v
+-----------------------+
| Analysis Normalization|
| Ticket Analysis       |
| Normalizer            |
+-----------+-----------+
            |
            v
+-----------------------+
|    Priority Decision  |
|    Priority Service   |
+-----------+-----------+
            |
            v
+-----------------------+
|     Routing Decision  |
|     Routing Service   |
+-----------+-----------+
            |
            v
+-----------------------+
|    Reply Suggestion   |
| Reply Suggestion Svc  |
+-----------+-----------+
            |
            v
+-----------------------+
|   Ticket Persistence  |
|     Ticket Service    |
+-----------+-----------+
            |
            v
+-----------------------+
|  Commit Transaction   |
+-----------+-----------+
            |
            v
+-----------------------+
|   Acknowledgement     |
| Acknowledgement Svc   |
|     + SMTP Service    |
+-----------+-----------+
            |
            v
+-----------------------+
|  Workflow Completion  |
| Workflow Execution Svc|
+-----------------------+

Failure Path:

Any Workflow Stage
        |
        v
Workflow Failure
        |
        v
Rollback Active Business Transaction
        |
        v
Record Failed Workflow Execution
        |
        v
Persist Dead Letter Record
        |
        v
Continue Processing Other Messages
        |
        v
Manual Retry When Requested
```

---

## 4. Workflow Entry

The mailbox-processing workflow begins in:

```text
app/services/email_ingestion_service.py
```

The email ingestion service coordinates mailbox-level processing.

Its responsibilities include:

* Retrieving messages through the IMAP service.
* Processing messages independently.
* Parsing email content.
* Processing attachment information.
* Invoking downstream workflow processing.
* Handling message-level success and failure.
* Preventing one failed message from stopping the entire ingestion cycle.

Conceptually:

```text
for each mailbox message:

    try:
        process message
    except workflow failure:
        record failure
        continue with next message
```

This failure-isolation model prevents one malformed email, provider failure, or workflow error from blocking unrelated messages.

---

## 5. Email Retrieval

Email retrieval is implemented by:

```text
app/services/imap_service.py
```

The IMAP integration is responsible for communicating with the configured mailbox.

The service handles operations such as:

* Establishing mailbox connections.
* Selecting the configured mailbox.
* Searching for messages.
* Fetching message content.
* Managing mailbox state.
* Handling IMAP failures.

Transient integration failures may be retried according to the application's retry configuration.

Credentials and mailbox configuration are loaded through application settings rather than being hard-coded into workflow logic.

---

## 6. Email Parsing

Email parsing is implemented by:

```text
app/services/email_parser.py
```

The parser converts raw email content into structured application data.

The parsed email representation contains information required by downstream services, including:

* Sender information.
* Sender email address.
* Subject.
* Message body.
* Received timestamp.
* Attachment metadata.

The parser supports multipart email structures.

When plain-text content is unavailable, HTML-derived content can be used as a fallback.

Customer-controlled email content remains untrusted after parsing.

Parsing converts transport data into structured application data; it does not make customer content trustworthy.

---

## 7. Attachment Processing

Attachment handling is implemented by:

```text
app/services/attachment_service.py
```

Attachment processing is responsible for:

* Receiving parsed attachment information.
* Validating attachment metadata.
* Generating storage paths.
* Persisting supported attachment files.
* Returning attachment records for downstream ticket persistence.

Attachment metadata is later persisted with the ticket aggregate.

The current implementation uses local attachment storage.

---

## 8. Workflow Execution Tracking

Workflow execution state is managed by:

```text
app/services/workflow_execution_service.py
```

Persistence is handled through:

```text
app/repositories/workflow_execution_repository.py
```

Workflow execution records provide operational visibility into ticket processing.

They support tracking information such as:

* Workflow execution identity.
* Processing state.
* Successful execution.
* Failed execution.
* Failure information.
* Retry execution lineage.
* Monitoring information.

Workflow execution records are separate from ticket records.

This separation allows the system to represent failed processing attempts even when no ticket was successfully created.

---

## 9. AI Ticket Analysis

The workflow requests structured ticket analysis through the external LLM integration.

The implementation includes:

```text
app/services/groq_llm_service.py
app/prompts/ticket_analysis_v1.py
app/prompts/registry.py
```

The analysis prompt instructs the model to return structured JSON containing ticket information.

Expected information includes:

* Customer name.
* Company.
* Issue summary.
* Detailed description.
* Category.
* Recommended priority.
* Sentiment.
* Product or service.
* Suggested department.
* Suggested tags.
* Confidence score.

The email body and attachment text are explicitly treated as untrusted data by the prompt.

The model is instructed not to follow customer-controlled instructions that attempt to override the ticket-analysis task.

---

## 10. AI Response Extraction and Validation

Raw LLM responses are not directly persisted.

The logical processing boundary is:

```text
External LLM Response
        |
        v
Structured Content Extraction
        |
        v
Pydantic Schema Validation
        |
        v
Ticket Analysis Normalization
```

Structured response extraction utilities are located in:

```text
app/utils/json_extractor.py
```

Ticket analysis schemas are located in:

```text
app/schemas/ticket_analysis_schema.py
app/schemas/normalized_ticket_schema.py
```

Invalid or incomplete model output causes workflow failure rather than silent persistence of malformed ticket state.

---

## 11. Ticket Analysis Normalization

Normalization is implemented by:

```text
app/services/ticket_analysis_normalizer.py
```

The normalizer converts validated model output into normalized application data.

Normalization behavior includes:

* Category normalization.
* Priority normalization.
* Sentiment normalization.
* Department normalization.
* Duplicate-tag removal.
* Empty-tag removal.
* Confidence-score clamping.
* Normalization metadata generation.

Conceptually:

```text
Validated AI Analysis
        |
        v
Canonical Category
        |
        v
Canonical Priority
        |
        v
Canonical Sentiment
        |
        v
Canonical Department
        |
        v
Clean Tags
        |
        v
Valid Confidence Range
        |
        v
Normalized Ticket Analysis
```

Normalization metadata records how the original model output was transformed.

---

## 12. Priority Decision

Priority assignment is implemented by:

```text
app/services/priority_service.py
```

Priority rules are configured in:

```text
app/config/priority_rules.py
```

The workflow does not blindly persist the AI-recommended priority.

Instead:

```text
Normalized AI Priority
        |
        v
Deterministic Priority Rules
        |
        v
Priority Decision
        |
        v
Final Ticket Priority
```

The priority decision records the final priority and the rule responsible for the decision.

This creates a deterministic decision boundary after AI inference.

---

## 13. Routing Decision

Routing is implemented by:

```text
app/services/routing_service.py
```

Routing configuration is stored in:

```text
app/config/routing_rules.py
```

The routing service maps normalized categories to configured support teams.

Conceptually:

```text
Normalized Category
        |
        v
Configured Routing Rules
        |
        v
Routing Decision
        |
        v
Assigned Team
```

Unsupported categories fail explicitly instead of silently routing to an arbitrary team.

The routing decision records the assigned team and the applied routing rule.

---

## 14. Reply Suggestion

Reply generation is implemented by:

```text
app/services/reply_suggestion_service.py
app/prompts/reply_suggestion_v1.py
```

The service generates a customer-support reply draft using:

* Customer email context.
* Normalized ticket context.

The prompt explicitly prevents unsupported claims.

The generated reply must not:

* Invent completed actions.
* Invent resolutions.
* Promise refunds or credits.
* Fabricate SLAs or deadlines.
* Expose internal classifications.
* Expose confidence scores.
* Expose prompts or implementation details.

Reply suggestions are intended for human review.

They are not automatically treated as approved customer responses.

---

## 15. Ticket Persistence

Ticket persistence is coordinated by:

```text
app/services/ticket_service.py
```

The ticket service creates the persistence aggregate:

```text
Ticket
  |
  +--> TicketAttachment records
  |
  +--> Initial TicketAuditLog record
```

The service uses:

* `TicketRepository`
* `AttachmentRepository`
* `AuditRepository`

The ticket service deliberately does not commit or roll back the database transaction.

Transaction ownership remains with the workflow-level caller.

This allows the entire persistence aggregate to participate in one transaction.

---

## 16. Ticket Persistence Transaction

The successful persistence path is:

```text
BEGIN TRANSACTION
        |
        v
Persist Ticket
        |
        v
Persist Attachment Metadata
        |
        v
Persist Initial Audit Event
        |
        v
Flush Pending Changes
        |
        v
COMMIT TRANSACTION
```

If persistence fails before commit:

```text
BEGIN TRANSACTION
        |
        v
Partial Persistence Work
        |
        v
Failure
        |
        v
ROLLBACK TRANSACTION
        |
        v
No Partial Ticket Aggregate Is Committed
```

Integration tests verify that rolled-back ticket creation does not leave a persisted ticket.

---

## 17. Acknowledgement Processing

Acknowledgement behavior is implemented by:

```text
app/services/acknowledgement_service.py
app/services/smtp_service.py
```

Acknowledgement rules are configured in:

```text
app/config/acknowledgement_rules.py
```

The acknowledgement workflow is conceptually:

```text
Persisted Ticket
        |
        v
Evaluate Acknowledgement Rule
        |
        +---- Not Required ----> Continue Workflow
        |
        v
Send SMTP Acknowledgement
        |
        v
Record Acknowledgement State
        |
        v
Continue Workflow
```

SMTP transport failures are handled according to the configured retry and workflow failure policies.

---

## 18. Workflow Completion

A successful workflow results in:

* Valid parsed email data.
* Validated and normalized AI analysis.
* Deterministic priority decision.
* Deterministic routing decision.
* Generated reply suggestion.
* Persisted ticket.
* Persisted attachment metadata where applicable.
* Initial ticket audit event.
* Acknowledgement processing according to configured rules.
* Successful workflow execution state.

The workflow result is returned through validated application schemas.

---

## 19. Sequence Diagram

The sequence diagram represents the logical interaction between major components.

Exact method-level calls may vary by implementation, but the diagram preserves the architectural responsibilities and trust boundaries of the implemented workflow.

```text
Mailbox
   |
   | Raw Messages
   v
EmailIngestionService
   |
   | Fetch Message
   +--------------------------> IMAPService
   |                               |
   |<------------------------------+
   |          Raw Email
   |
   | Parse Email
   +--------------------------> EmailParser
   |                               |
   |<------------------------------+
   |          ParsedEmail
   |
   | Start / Continue Execution
   +--------------------------> WorkflowExecutionService
   |                               |
   |<------------------------------+
   |          WorkflowExecution
   |
   | Process Email
   +--------------------------> WorkflowService
                                   |
                                   | Analyze Ticket
                                   +------------------> GroqLLMService
                                   |                       |
                                   |<----------------------+
                                   |       AI Analysis
                                   |
                                   | Normalize Analysis
                                   +------------------> TicketAnalysisNormalizer
                                   |                       |
                                   |<----------------------+
                                   |    Normalized Analysis
                                   |
                                   | Assign Priority
                                   +------------------> PriorityService
                                   |                       |
                                   |<----------------------+
                                   |    PriorityDecision
                                   |
                                   | Route Ticket
                                   +------------------> RoutingService
                                   |                       |
                                   |<----------------------+
                                   |    RoutingDecision
                                   |
                                   | Generate Reply
                                   +------------------> ReplySuggestionService
                                   |                       |
                                   |<----------------------+
                                   |    Reply Suggestion
                                   |
                                   | Create Ticket Aggregate
                                   +------------------> TicketService
                                   |                       |
                                   |                       +--> TicketRepository
                                   |                       |
                                   |                       +--> AttachmentRepository
                                   |                       |
                                   |                       +--> AuditRepository
                                   |                       |
                                   |<----------------------+
                                   |    Ticket Result
                                   |
                                   | Commit Business Transaction
                                   +------------------> Database
                                   |                       |
                                   |<----------------------+
                                   |
                                   | Attach Ticket to Execution
                                   +------------------> WorkflowExecutionService
                                   |                       |
                                   |<----------------------+
                                   |
   |<------------------------------+
   |          Ticket Result
   |
   | Process Acknowledgement
   +--------------------------> AcknowledgementService
   |                               |
   |                               +--------------> SMTPService
   |                               |                   |
   |                               |<------------------+
   |<------------------------------+
   |
   | Complete Workflow Execution
   +--------------------------> WorkflowExecutionService
   |                               |
   |<------------------------------+
   |
   v
Continue With Next Mailbox Message


Failure Sequence:

Workflow Stage
   |
   | Exception
   v
WorkflowService
   |
   | Roll Back Business Transaction
   +--------------------------> Database
   |
   | Record Failure
   +--------------------------> WorkflowExecutionService
   |                               |
   |                               +--> FailureHandlingService
   |                               |
   |                               +--> DeadLetterRepository
   |                               |
   |<------------------------------+
   |
   | Re-raise Original Exception
   v
EmailIngestionService
   |
   | Isolate Message Failure
   |
   v
Continue With Next Mailbox Message
```

---

## 20. Message-Level Failure Isolation

Mailbox messages are processed independently.

Conceptually:

```text
Message A
    |
    +--> Success

Message B
    |
    +--> Workflow Failure
    |
    +--> Record Failure
    |
    +--> Continue

Message C
    |
    +--> Success
```

A failed message does not terminate processing of all remaining messages.

This behavior is verified by automated tests of the email-ingestion service.

---

## 21. Retry Handling

Retry behavior is implemented in:

```text
app/core/retry.py
```

Retries are intended for transient failures.

Potential retryable operations include:

* External LLM requests.
* IMAP operations.
* SMTP operations.
* Other configured transient external failures.

Conceptually:

```text
Operation
    |
    v
Attempt 1
    |
    +---- Success ----> Continue
    |
    v
Retry Delay
    |
    v
Attempt 2
    |
    +---- Success ----> Continue
    |
    v
Retry Delay
    |
    v
Final Attempt
    |
    +---- Success ----> Continue
    |
    v
Retry Exhausted
    |
    v
Propagate Failure
```

Retry logic is separate from durable workflow recovery.

Retries handle short-lived operational failures.

Dead-letter recovery handles failures that outlive the immediate workflow attempt.

---

## 22. Failure Recording

Workflow failure persistence is coordinated by:

```text
app/services/failure_handling_service.py
```

Failure information is stored using workflow execution and dead-letter persistence components.

The failure path is:

```text
Workflow Failure
        |
        v
Rollback Active Transaction When Required
        |
        v
Record Failed Workflow Execution
        |
        v
Persist Dead Letter Record
        |
        v
Continue Processing Other Messages
```

Failure persistence provides durable operational state for later inspection and recovery.

---

## 23. Dead-Letter Recovery

Recovery is implemented by:

```text
app/services/failure_recovery_service.py
app/api/failure_recovery_routes.py
```

Failed workflows can be retried manually.

Conceptually:

```text
Dead Letter Record
        |
        v
Operator Requests Retry
        |
        v
Validate Retry Eligibility
        |
        v
Create Retry Workflow Execution
        |
        v
Execute Retry Operation
        |
        +---- Success
        |        |
        |        v
        |   Resolve Dead Letter
        |
        +---- Failure
                 |
                 v
          Preserve or Reopen Failure State
```

The recovery system preserves retry lineage.

A retry attempt is represented as a workflow execution rather than silently overwriting the original failed execution.

---

## 24. Ticket Lifecycle Workflow

Ticket status changes are controlled by:

```text
app/services/ticket_lifecycle_service.py
```

The allowed lifecycle is:

```text
OPEN
  |
  v
IN_PROGRESS
  |
  +----------------------+
  |                      |
  v                      v
WAITING_FOR_CUSTOMER   RESOLVED
  |                      |
  +----> IN_PROGRESS     v
  |                    CLOSED
  v
RESOLVED
  |
  v
CLOSED
```

Allowed transitions are enforced by the service.

Invalid transitions raise an application exception.

Successful transitions create ticket audit events.

No audit event is created for a rejected transition.

---

## 25. Manual Review Workflow

Manual review operations are implemented by:

```text
app/services/manual_review_service.py
app/api/manual_review_routes.py
```

The manual review layer allows operator-driven actions against persisted tickets.

Operations are coordinated through application services and repositories.

Auditable state changes are persisted rather than being performed directly by presentation-layer code.

---

## 26. Monitoring Workflow State

Monitoring is implemented by:

```text
app/services/monitoring_service.py
app/api/monitoring_routes.py
```

Monitoring services expose operational information derived from workflow execution state.

This allows operators to inspect workflow processing without directly querying database tables.

---

## 27. Workflow Definition Deliverable

The machine-readable workflow definition is stored at:

```text
workflow/workflow_definition.json
```

The JSON workflow definition complements this document.

The Markdown document explains architectural intent and runtime behavior.

The JSON file provides a structured deliverable describing workflow stages, dependencies, failure behavior, and outputs.

The workflow definition should remain synchronized with implemented services.

---

## 28. Workflow Testing

SupportIQ verifies workflow behavior through unit and integration tests.

Important integration tests include:

```text
tests/integration/test_email_groq_database_workflow.py
tests/integration/test_ticket_lifecycle_audit_workflow.py
tests/integration/test_failed_workflow_retry.py
tests/integration/test_email_ticket_workflow.py
tests/integration/test_ticket_processing_workflow.py
tests/integration/test_acknowledgement_workflow.py
```

The tests verify behavior including:

* Email-to-AI-to-database processing.
* Ticket persistence.
* Attachment persistence.
* Audit creation.
* Transaction rollback.
* Distinct ticket persistence.
* Ticket lifecycle transitions.
* Invalid lifecycle transition handling.
* Acknowledgement behavior.
* Failed workflow retry.
* Dead-letter resolution.
* Dead-letter reopening after retry failure.

The complete automated suite currently verifies:

```text
452 passed
```

Application coverage is:

```text
89%
```

---

## 29. Current Workflow Limitations

The current workflow has documented limitations.

### Synchronous Processing

The main workflow is synchronous and does not use a distributed background job system.

### External Provider Dependency

Live AI processing depends on external LLM availability and credentials.

### Local Attachment Storage

Attachments are stored locally.

### No Distributed Queue

Failed messages are persisted through application recovery mechanisms rather than a production message broker.

### Limited Production Access Control

The project does not currently provide a complete authentication, authorization, and role-based access-control system for operator endpoints.

### No Distributed Transaction

The application relies on local database transaction boundaries and does not coordinate distributed transactions across email, SMTP, LLM, and database systems.

These limitations are acceptable for the current project scope and provide clear targets for future evolution.

---

## 30. Future Workflow Improvements

Potential improvements include:

* Background worker processes.
* Durable message queues.
* Idempotency keys for mailbox processing.
* Distributed attachment storage.
* Automatic dead-letter retry policies.
* Retry scheduling and backoff persistence.
* Workflow cancellation.
* Workflow timeout enforcement.
* Per-stage latency metrics.
* Distributed tracing.
* Alerting on failure-rate thresholds.
* Provider failover.
* Human approval queues for reply suggestions.
* Authentication and role-based authorization.
* Workflow-definition validation against implementation.
* Automated workflow regression reports.

---

## 31. Summary

SupportIQ implements an end-to-end customer-support email processing workflow that combines:

```text
IMAP Email Retrieval
        |
        v
Email Parsing
        |
        v
Attachment Processing
        |
        v
AI Ticket Analysis
        |
        v
Schema Validation
        |
        v
Normalization
        |
        v
Deterministic Priority Decision
        |
        v
Deterministic Routing Decision
        |
        v
Reply Suggestion
        |
        v
Transactional Ticket Persistence
        |
        v
Acknowledgement Processing
        |
        v
Workflow Execution Tracking
        |
        v
Monitoring and Recovery
```

The workflow isolates message failures, validates AI-generated data, applies deterministic business rules, preserves transaction boundaries, records audit history, tracks workflow executions, persists durable failure state, and supports manual recovery.

The Workflow Diagram and Sequence Diagram provide complementary views of the implemented system behavior.

Together with automated unit and integration tests, the workflow architecture provides a repeatable and auditable foundation for SupportIQ ticket processing.
