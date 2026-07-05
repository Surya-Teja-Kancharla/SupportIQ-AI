# SupportIQ AI

**SupportIQ AI** is an AI-powered customer support ticket automation system designed to ingest customer support emails, analyze unstructured support requests, classify issues, assign priorities, route tickets to appropriate teams, persist ticket data, generate AI-assisted reply suggestions for support agents, send customer acknowledgements, and maintain a complete support ticket lifecycle.

The project is being developed as part of the **Anthrasync AI Engineer Hiring Process – Round 3 Technical Assignment (Task 4: AI Customer Support Ticket Automation)**.

The system follows a production-oriented modular monolith architecture emphasizing:

* Maintainability
* Separation of concerns
* Explicit service boundaries
* Secure configuration management
* Reliable inbound email processing
* Reusable outbound email transport
* Structured data validation
* Centralized exception handling
* Structured observability
* Retry and resilience infrastructure
* Independent batch-item processing
* Testability
* Scalability
* Auditability
* Security and data privacy
* Provider-independent AI capabilities
* Deterministic normalization boundaries

> **Current Development Status:** Hours 1–8 completed, including the Hour 6.5 optional bonus feature — project foundation, PostgreSQL schema and Alembic migration infrastructure, centralized configuration, secure IMAP email ingestion, MIME parsing, attachment validation and storage, email ingestion orchestration, SMTP transport, structured JSON logging, centralized application exceptions, reusable retry infrastructure, Groq API integration, provider-independent LLM service boundaries, versioned prompt architecture, structured ticket-analysis contracts, robust JSON extraction, AI response validation, selective application-controlled LLM retries, real Groq integration verification, labeled AI evaluation dataset, evaluation metrics, confidence analysis, generated AI evaluation report, deterministic text and ticket-analysis normalization, immutable normalized ticket-analysis contracts, AI-generated support-agent reply suggestions, deterministic priority assignment, configurable category-to-team routing, SQLAlchemy ORM models, centralized database session infrastructure, Alembic-managed schema evolution, repository abstractions for tickets, attachments, audit logs, and workflow executions, repository-level exception translation, explicit transaction ownership boundaries, Message-ID-based workflow execution lookup for future idempotency orchestration, 100% focused repository-layer coverage, and 203 passing automated tests with zero regressions.

---

## Table of Contents

* [Project Objective](#project-objective)
* [Business Scenario](#business-scenario)
* [Planned End-to-End Workflow](#planned-end-to-end-workflow)
* [Current Implementation Status](#current-implementation-status)
* [Features Implemented](#features-implemented)
* [Technology Stack](#technology-stack)
* [Project Architecture](#project-architecture)
* [Project Structure](#project-structure)
* [Database Design](#database-design)
* [Email Infrastructure Architecture](#email-infrastructure-architecture)
* [Email Ingestion Orchestration](#email-ingestion-orchestration)
* [AI Analysis Architecture](#ai-analysis-architecture)
* [AI Evaluation Architecture](#ai-evaluation-architecture)
* [Ticket Analysis Normalization Architecture](#ticket-analysis-normalization-architecture)
* [AI Reply Suggestion Architecture](#ai-reply-suggestion-architecture)
* [Priority Assignment Architecture](#priority-assignment-architecture)
* [Routing Architecture](#routing-architecture)
* [Prompt Engineering and Documentation](#prompt-engineering-and-documentation)
* [SMTP Transport](#smtp-transport)
* [Exception Architecture](#exception-architecture)
* [Retry Infrastructure](#retry-infrastructure)
* [Structured Logging](#structured-logging)
* [Attachment Security](#attachment-security)
* [Configuration Management](#configuration-management)
* [Environment Variables](#environment-variables)
* [Installation and Setup](#installation-and-setup)
* [Running Integration Tests](#running-integration-tests)
* [Running AI Evaluation](#running-ai-evaluation)
* [Running Automated Tests](#running-automated-tests)
* [AI Evaluation Results](#ai-evaluation-results)
* [Test Coverage](#test-coverage)
* [Current Limitations](#current-limitations)
* [Security Considerations](#security-considerations)
* [Design Decisions](#design-decisions)
* [Development Roadmap](#development-roadmap)
* [Planned Deliverables](#planned-deliverables)
* [Assumptions](#assumptions)

---

## Project Objective

SupportIQ AI aims to automate the initial triage and management of customer support requests received through email while providing AI-assisted reply suggestions to support agents.

The completed system will:

1. Monitor a support inbox for incoming customer emails.
2. Extract sender metadata, email content, timestamps, Message-ID values, and attachments.
3. Validate inbound email contracts.
4. Analyze support requests using a Large Language Model.
5. Generate structured ticket information.
6. Validate and normalize AI-generated output.
7. Classify customer issues.
8. Determine ticket priority using AI recommendations and deterministic business rules.
9. Route tickets to appropriate support teams.
10. Persist tickets and related data in PostgreSQL.
11. Generate contextual AI-assisted reply suggestions for support agents.
12. Allow support agents to review and modify suggested replies before customer delivery.
13. Automatically acknowledge customer requests through email.
14. Allow support agents to review and modify AI-generated decisions.
15. Maintain a complete ticket lifecycle.
16. Record ticket changes in an audit trail.
17. Handle failures, retries, malformed AI responses, duplicate processing, and workflow edge cases.
18. Emit machine-readable operational logs for observability and debugging.

---

## Business Scenario

Customer support teams may receive hundreds or thousands of support requests through email.

Support agents traditionally perform several repetitive tasks manually:

* Read incoming customer emails.
* Identify the customer and organization.
* Understand the reported issue.
* Determine the issue category.
* Assign a priority.
* Route the request to an appropriate team.
* Create a support ticket.
* Send an acknowledgement email.
* Track ticket status changes.
* Maintain historical records of ticket updates.
* Draft an appropriate customer response.

SupportIQ AI is intended to automate the initial support triage workflow and provide contextual reply suggestions while keeping human support agents in control of ticket review, response approval, and resolution.

---

## Planned End-to-End Workflow

```text
Customer Email
      │
      ▼
Support Inbox
      │
      ▼
IMAP Transport
      │
      ▼
MIME Email Parser
      │
      ├── Sender Name
      ├── Sender Email
      ├── Subject
      ├── Email Body
      ├── Received Timestamp
      ├── Message-ID
      └── Attachments
      │
      ▼
Attachment Validation and Storage
      │
      ▼
Email Ingestion Orchestration
      │
      ├── Contract Validation
      ├── Per-Message Failure Isolation
      ├── Processing Result Construction
      ├── Batch Metrics
      └── Structured Logging
      │
      ▼
LLM Ticket Analysis
      │
      ▼
Structured JSON Validation
      │
      ▼
Ticket Analysis Normalization
      │
      ├── Unicode NFKC Normalization
      ├── Whitespace Normalization
      ├── Optional Text Normalization
      ├── Category Canonicalization
      ├── AI Priority Canonicalization
      ├── Sentiment Canonicalization
      ├── Department Canonicalization
      ├── Tag Normalization and Deduplication
      ├── Confidence Precision Normalization
      ├── Normalization Metadata
      ├── Original Customer Email Context
      ├── Normalized Ticket Analysis
      ├── Versioned Reply Prompt
      ├── Provider-Independent LLM Request
      ├── Reply Validation
      ├── Whitespace Normalization
      └── Maximum Reply-Length Enforcement
      │
      ▼
Priority Assignment Engine
      │
      ▼
Configurable Routing Engine
      │
      ▼
PostgreSQL Ticket Creation
      │
      ├── Ticket Record
      ├── Attachments
      ├── Tags
      ├── Audit Logs
      └── Internal Notes
      │
      ▼
Agent Review
      │
      ├── Ticket Decision Review
      └── Suggested Reply Review
      │
      ▼
SMTP Customer Acknowledgement / Approved Response
      │
      ▼
Ticket Lifecycle Management
      │
      ▼
Complete Audit Trail
```

---

## Current Implementation Status

### Hour 1 — Project Setup and Database Foundation

Completed:

* Product name selected: **SupportIQ AI**.
* Git repository initialized.
* Python virtual environment created.
* Required Python dependencies installed.
* `requirements.txt` generated.
* Modular project structure created.
* PostgreSQL selected as the primary database.
* PostgreSQL database created.
* Database tables created.
* Database indexes created.
* Environment configuration files created.
* Sensitive runtime configuration excluded from Git.
* Database schema designed for normalized ticket storage.

### Hour 2 — Secure Email Ingestion

Completed:

* Centralized application configuration.
* Environment variable loading through Pydantic Settings.
* Gmail IMAP SSL connection.
* Support inbox authentication using a Google App Password.
* Configurable mailbox selection.
* Detection of unread emails using IMAP `UNSEEN`.
* Non-destructive email retrieval using `BODY.PEEK[]`.
* MIME header decoding.
* Sender name extraction.
* Sender email extraction.
* Subject extraction.
* Message-ID extraction.
* Email timestamp parsing.
* Plain-text email body extraction.
* HTML email fallback and conversion to text.
* Multipart email processing.
* Attachment detection.
* Attachment filename decoding.
* Filename sanitization.
* Attachment extension allowlisting.
* Maximum attachment size enforcement.
* Unique attachment filename generation.
* Attachment storage.
* Structured email and attachment schemas.
* Manual Gmail IMAP integration testing.
* Automated unit tests.
* Test coverage reporting.

### Hour 3 — Email Infrastructure, Orchestration, Resilience, and Observability

Completed:

* Centralized application-specific exception hierarchy.
* Email transport exception taxonomy.
* IMAP connection, authentication, mailbox, and fetch exceptions.
* SMTP connection, authentication, and delivery exceptions.
* Attachment exception hierarchy.
* Retry exhaustion exception support.
* Machine-readable JSON logging formatter.
* Console logging.
* Application log file output.
* Dedicated error log output.
* Structured event vocabulary.
* Context-rich logging helper.
* Generic reusable retry policy.
* Exponential backoff calculation.
* Configurable maximum retry attempts.
* Maximum delay enforcement.
* Jitter support.
* Dependency injection for deterministic retry testing.
* Retry exhaustion handling.
* SMTP outbound email schemas.
* SMTP delivery result schemas.
* Multipart plain-text and HTML email construction.
* Message-ID generation.
* SMTP STARTTLS support.
* SMTP authentication.
* Recipient-refusal detection.
* SMTP exception translation.
* Real Gmail SMTP delivery verification.
* Ingestion failure schemas.
* Per-message processing result schemas.
* Batch ingestion result schemas.
* Batch success-rate calculation support.
* Email ingestion orchestration service.
* Inbound email contract validation.
* Empty Message-ID validation.
* Empty-body validation.
* Per-message failure isolation.
* Batch success/failure/skipped counters.
* Guaranteed IMAP disconnect attempts.
* IMAP service refactored to application-specific exceptions.
* Non-destructive email fetching preserved after refactoring.
* Real Gmail IMAP regression verification.
* Retry utility unit tests.
* SMTP service unit tests.
* Email ingestion orchestration unit tests.
* Full regression suite verification.
* Application-wide coverage measurement.

### Hour 4 — Groq Integration, LLM Architecture, Structured AI Analysis, and Resilience

Completed:

* Groq Python SDK integration.
* Centralized Groq API configuration.
* Configurable Groq model selection.
* Configurable LLM request timeout.
* Configurable maximum token output.
* Configurable LLM temperature.
* Configurable maximum LLM retries.
* Provider-independent `LLMService` abstraction.
* Groq-specific `GroqLLMService` adapter.
* Separation of application workflow logic from the concrete AI provider.
* Versioned ticket-analysis prompt architecture.
* Prompt registry for explicit prompt selection.
* Immutable prompt-version preservation strategy.
* Dedicated system prompt and user prompt construction.
* Explicit support-ticket category vocabulary.
* Explicit priority vocabulary.
* Explicit sentiment vocabulary.
* Explicit department vocabulary.
* Prompt instructions for JSON-only responses.
* Prompt instructions for null handling.
* Prompt instructions to reduce unsupported inference and hallucination.
* Confidence-score guidance.
* Prompt-injection mitigation instructions.
* Explicit treatment of email and attachment content as untrusted data.
* Structured `TicketAnalysisRequest` schema.
* Structured `TicketAnalysisResponse` schema.
* Strict Pydantic AI response validation.
* Rejection of unexpected AI response fields.
* Confidence-score range validation.
* Robust JSON object extraction.
* Direct JSON parsing support.
* JSON extraction from markdown code fences.
* JSON extraction from responses containing surrounding text.
* Correct handling of braces embedded inside JSON string values.
* Rejection of empty AI responses.
* Rejection of JSON arrays when an object is required.
* Rejection of responses without a valid JSON object.
* LLM-specific application exception hierarchy.
* Integration of LLM failures into the existing `SupportIQError` hierarchy.
* Explicit distinction between retryable and non-retryable LLM failures.
* Timeout failure classification.
* Rate-limit failure classification.
* Authentication failure classification.
* Connection failure classification.
* HTTP 4xx request failure classification.
* HTTP 5xx provider failure classification.
* Invalid completion structure handling.
* Empty completion content handling.
* Malformed JSON handling.
* Schema-invalid AI response handling.
* Selective integration with the reusable retry executor.
* Retry of LLM timeouts.
* Retry of provider rate limits.
* Retry of connection failures.
* Retry of HTTP 5xx provider failures.
* Immediate failure for authentication errors.
* Immediate failure for non-retryable HTTP 4xx errors.
* Immediate failure for malformed AI output.
* Immediate failure for schema-invalid AI output.
* Preservation of typed LLM failures after retry exhaustion.
* Mocked Groq provider unit tests without consuming API quota.
* Focused Hour 4 automated test verification.
* Full application regression test verification.

### Hour 5 — AI Evaluation, Prompt Quality Measurement, and Real Provider Verification

Completed:

* Corrected environment configuration used for real-provider execution.
* Disabled Groq SDK automatic retries so retry ownership remains application-controlled.
* Controlled real Groq API smoke testing.
* Successful structured analysis of a real support-ticket example.
* Verification of the complete provider path:
  * Prompt selection.
  * Prompt construction.
  * Groq request execution.
  * Raw completion retrieval.
  * JSON extraction.
  * Pydantic response validation.
  * Typed `TicketAnalysisResponse` creation.
* Labeled AI evaluation dataset.
* Versioned evaluation dataset metadata.
* Unique evaluation case identifiers.
* Explicit expected category labels.
* Explicit expected priority labels.
* Explicit expected sentiment labels.
* Explicit expected department labels.
* Standard ticket cases.
* Priority-sensitive ticket cases.
* Ambiguous ticket cases.
* Adversarial and prompt-injection-oriented ticket cases.
* Strict evaluation dataset schema validation.
* Rejection of unknown evaluation case types.
* Rejection of unexpected evaluation dataset fields.
* Evaluation result models.
* Per-case correctness tracking.
* Evaluation runner.
* Per-label accuracy calculation.
* Structured-output validity calculation.
* Case-type all-label accuracy calculation.
* Confidence statistics.
* Correct-prediction confidence measurement.
* Incorrect-prediction confidence measurement.
* High-confidence error detection.
* Failed-analysis accounting.
* Empty-result handling.
* Floating-point-safe metric calculation.
* Evaluation metrics unit tests.
* Evaluation dataset schema tests.
* Real Groq execution against the complete evaluation dataset.
* AI evaluation report generation.
* Persistent report output to `docs/ai_evaluation_report.json`.
* Baseline prompt-quality measurement for `ticket-analysis-v1`.
* Identification of classification and confidence-calibration limitations.
* Final full regression verification.

### Hour 6 — JSON Validation and Ticket Analysis Normalization Layer

Completed:

* Added a dedicated normalization boundary between validated AI output and downstream business logic.
* Added reusable text-normalization utilities.
* Added Unicode NFKC normalization.
* Added deterministic whitespace normalization.
* Added normalization of required textual fields.
* Added normalization of optional textual fields.
* Added conversion of empty optional values to `None`.
* Added provider-independent label normalization.
* Added case-insensitive label matching.
* Added separator normalization for spaces, underscores, and hyphens.
* Added canonical category normalization.
* Added category alias mappings.
* Added canonical AI-recommended priority normalization.
* Added priority alias mappings.
* Added canonical sentiment normalization.
* Added sentiment alias mappings.
* Added canonical suggested-department normalization.
* Added department alias mappings.
* Added preservation of unsupported normalized labels instead of silently mapping them to fallback classifications.
* Added deterministic tag normalization.
* Added lowercase tag canonicalization.
* Added slug-style tag formatting.
* Added special-character normalization for tags.
* Added empty-tag removal.
* Added duplicate-tag removal.
* Added preservation of first-seen tag ordering.
* Added duplicate-tag and empty-tag counters.
* Added deterministic confidence-score precision normalization.
* Added defensive confidence clamping support.
* Added explicit separation between AI-recommended priority and future final business priority.
* Added immutable `NormalizedTicketAnalysis` contract.
* Added immutable `NormalizationMetadata` contract.
* Added preservation of original classification labels in normalization metadata.
* Added metadata flags indicating which classification fields were normalized.
* Added normalization metadata for removed duplicate and empty tags.
* Added confidence-clamping metadata.
* Added strict rejection of unexpected normalized schema fields.
* Verified that normalization does not mutate the original `TicketAnalysisResponse`.
* Added 14 text-normalization unit tests.
* Added 23 ticket-analysis-normalization unit tests.
* Verified 37 focused Hour 6 tests.
* Verified the complete 105-test application regression suite.
* Completed Hour 6 with zero test failures and zero regressions.

### Hour 6.5 — Bonus Feature: AI-Generated Reply Suggestions for Support Agents
Completed:

* Added AI-generated reply suggestions as an optional bonus feature.
* Added a dedicated versioned reply-suggestion prompt.
* Registered the reply-suggestion prompt through the central prompt registry.
* Documented the reply-suggestion prompt in `docs/prompts.md`.
* Extended the provider-independent `LLMService` boundary with reply-suggestion generation capability.
* Added structured `ReplySuggestionRequest` contract.
* Added structured `ReplySuggestionResponse` contract.
* Added strict rejection of unexpected reply-suggestion fields.
* Added required input-text validation.
* Added empty suggested-reply rejection.
* Added whitespace-only suggested-reply rejection.
* Added immutable reply-suggestion response contracts.
* Extended `GroqLLMService` to support reply-suggestion generation.
* Reused the existing application-controlled selective retry infrastructure.
* Preserved typed provider failures after retry exhaustion.
* Reused timeout failure handling.
* Reused rate-limit failure handling.
* Reused connection failure handling.
* Reused authentication failure handling.
* Reused HTTP 4xx and HTTP 5xx failure classification.
* Added explicit plain-text completion handling for reply generation.
* Avoided JSON response-format enforcement for reply-suggestion requests.
* Added `ReplySuggestionService` as an application-level AI capability boundary.
* Constructed provider-independent reply requests from the original parsed email and normalized ticket analysis.
* Added deterministic suggested-reply whitespace normalization.
* Added configurable maximum reply-length policy enforcement.
* Added validation for non-positive maximum reply lengths.
* Preserved the original `ParsedEmail` without mutation.
* Preserved the original `NormalizedTicketAnalysis` without mutation.
* Returned a new validated reply response after normalization.
* Propagated typed provider failures through the reply-suggestion service boundary.
* Added reply-suggestion schema unit tests.
* Added reply-suggestion service unit tests.
* Added Groq reply-suggestion provider tests using mocked network boundaries.
* Added retry and failure-classification tests for reply generation.
* Added a test verifying that reply-suggestion requests do not use JSON response format.
* Added a real-provider manual reply-suggestion verification script.
* Verified the complete real-provider pipeline:
  * Customer email construction.
  * Real Groq ticket analysis.
  * Ticket-analysis schema validation.
  * Deterministic ticket-analysis normalization.
  * Reply-suggestion service orchestration.
  * Real Groq reply generation.
  * Reply-suggestion schema validation.
  * Suggested-reply normalization.
  * Maximum reply-length policy enforcement.
  * Validated suggested-reply output.
* Re-ran the original real Groq ticket-analysis smoke test successfully.
* Verified 43 focused Hour 6.5 tests.
* Verified the complete 137-test application regression suite.
* Completed Hour 6.5 with zero automated test failures and zero regressions.
* The optional real-provider AI evaluation rerun was interrupted during a provider/network read and is not considered part of the Hour 6.5 completion gate.

### Hour 7 — Deterministic Priority Assignment and Configurable Ticket Routing

Completed:

* Added deterministic priority assignment after the ticket-analysis normalization boundary.
* Added centralized priority-order configuration.
* Added configurable business-rule phrase collections for Critical, High, Medium, and Low priorities.
* Added deterministic matching of business rules against normalized ticket content.
* Added priority-rule evaluation across issue summaries, detailed descriptions, categories, product or service context, and normalized tags.
* Added case-insensitive business-rule matching.
* Added highest-priority rule selection when multiple business rules match the same ticket.
* Added reconciliation between AI-recommended priority and deterministic business rules.
* Added escalation of AI-recommended priority when a higher-priority business rule matches.
* Prevented lower-priority business rules from downgrading a higher AI-recommended priority.
* Preserved the AI recommendation when no deterministic business rule matches.
* Added explicit priority-decision output containing the AI-recommended priority, final priority, applied rule, and override status.
* Added priority-decision traceability through human-readable applied-rule descriptions.
* Added strict validation of the configured priority vocabulary.
* Added rejection of missing or additional configured priority levels.
* Added rejection of duplicate priority ranks.
* Added rejection of empty business-rule collections.
* Added rejection of empty business-rule phrases.
* Added configurable category-to-team routing rules.
* Added deterministic routing from normalized ticket categories to assigned support teams.
* Added explicit routing-decision output containing category, assigned team, and applied routing rule.
* Added dependency injection for routing configuration to improve testability and future configurability.
* Added validation of empty routing configurations.
* Added validation of empty routing categories.
* Added validation of empty routing-team values.
* Added explicit rejection of unsupported or unmapped ticket categories.
* Preserved `NormalizedTicketAnalysis` immutability during priority assignment and routing.
* Added dedicated application exceptions for priority-assignment failures, routing-configuration failures, and unmapped categories.
* Added focused unit tests for deterministic priority assignment.
* Added focused unit tests for configurable ticket routing.
* Verified all supported category-to-team mappings.
* Verified injected routing configuration behavior.
* Verified business-rule escalation behavior.
* Verified that lower-priority rules cannot downgrade higher AI recommendations.
* Verified AI-priority preservation when no rule matches.
* Verified highest-priority selection when multiple rules match.
* Verified case-insensitive priority-rule matching.
* Verified normalized-tag participation in priority assignment.
* Verified priority and routing configuration validation.
* Verified non-mutation of normalized ticket analyses.
* Verified 36 focused Hour 7 tests.
* Measured 97% focused coverage across the Hour 7 priority and routing services.
* Achieved 96% coverage for `priority_service.py`.
* Achieved 100% coverage for `routing_service.py`.
* Verified the complete 173-test application regression suite.
* Completed Hour 7 with zero automated test failures and zero regressions.

### Hour 8 — Completed

* SQLAlchemy declarative base infrastructure.
* Centralized database engine and session infrastructure.
* SQLAlchemy ORM ticket model.
* SQLAlchemy ORM ticket-attachment model.
* SQLAlchemy ORM ticket-audit-log model.
* SQLAlchemy ORM workflow-execution model.
* Alembic migration infrastructure.
* Baseline existing-schema migration.
* Workflow-executions table migration.
* Ticket-index restoration migration.
* Dedicated repository package.
* Ticket repository.
* Attachment repository.
* Audit repository.
* Workflow-execution repository.
* Ticket persistence and lookup operations.
* Attachment persistence and lookup operations.
* Audit-event persistence and lookup operations.
* Workflow-execution persistence and Message-ID lookup.
* Duplicate Message-ID rejection.
* SQLAlchemy exception translation.
* Integrity-error translation.
* Explicit caller-owned transaction boundaries.
* Repository non-commit behavior.
* 30 focused repository tests.
* 100% focused repository-package coverage.
* 98 repository statements covered with zero misses.
* 203-test full regression verification.
* Zero automated test failures and zero regressions.

### Hour 9 — Planned

* End-to-end ticket-processing workflow orchestration.
* Transaction coordination across repositories.
* Ticket creation persistence integration.
* Attachment persistence integration.
* Tag persistence integration.
* Audit-log persistence integration.
* Workflow-execution persistence integration.
* Message-ID-based idempotency enforcement.
* Duplicate email processing prevention.
* Rollback behavior for partial workflow failures.
* Acknowledgement orchestration after successful persistence.
* Email processed-state update after the complete success boundary.
* Workflow integration tests.
* PostgreSQL-backed persistence integration tests.


### Automated Testing Status

203 tests passed
1 third-party dependency deprecation warning
0 test failures
0 regressions

Focused Hour 6 normalization suite:

37 tests passed

Focused Hour 6.5 reply-suggestion suite:

43 tests passed

Focused Hour 7 priority and routing suite:

36 tests passed

Focused Hour 7 coverage:

97% total service coverage
96% priority-service coverage
100% routing-service coverage

Focused Hour 8 repository suite:

30 tests passed

Focused Hour 8 repository coverage:

100% total repository-package coverage
98 statements covered
0 statements missed

Full application regression suite:

203 tests passed

The warning originates from the BeautifulSoup/lxml HTML parser dependency and does not affect application functionality.

---

## Features Implemented

### Centralized Configuration

Application configuration is loaded from environment variables using `pydantic-settings`.

All services consume settings through a centralized configuration module instead of independently accessing environment variables.

### Secure IMAP Connection

SupportIQ AI connects to Gmail using IMAP over SSL.

Authentication uses a Google App Password instead of the normal Google account password.

### Unread Email Detection

The application searches the configured mailbox for:

```text
UNSEEN
```

messages.

### Non-Destructive Email Fetching

Messages are fetched using:

```text
BODY.PEEK[]
```

This prevents retrieval from automatically marking messages as read.

Emails will be explicitly marked as processed only after the complete downstream processing boundary succeeds.

### MIME Email Parsing

The parser supports:

* Plain-text messages.
* HTML messages.
* Multipart messages.
* MIME-encoded headers.
* UTF-8 headers.
* Sender extraction.
* Subject extraction.
* Message-ID extraction.
* Timestamp parsing.
* Plain-text preference when both plain text and HTML are available.
* HTML-to-text fallback.

### Secure Attachment Processing

Attachments are:

1. Detected from multipart messages.
2. Decoded.
3. Validated.
4. Sanitized.
5. Checked against the configured extension allowlist.
6. Checked against the configured maximum size.
7. Assigned collision-resistant filenames.
8. Stored under the configured upload directory.
9. Returned as structured attachment metadata.

### Email Ingestion Orchestration

The `EmailIngestionService` acts as the application-level coordination boundary for inbound email processing.

Responsibilities include:

* Establishing the IMAP connection.
* Retrieving unread parsed emails.
* Validating inbound email contracts.
* Processing messages independently.
* Preventing one malformed message from terminating the entire batch.
* Classifying processing failures.
* Creating structured processing results.
* Maintaining batch-level processing counters.
* Recording completion timestamps.
* Attempting IMAP cleanup through a `finally` boundary.

### SMTP Transport

The `SMTPService` provides reusable outbound email delivery infrastructure.

Implemented capabilities include:

* Plain-text email delivery.
* HTML alternative bodies.
* Multipart email generation.
* Message-ID generation.
* Date header generation.
* Optional Reply-To support.
* STARTTLS encryption.
* SMTP authentication.
* Recipient-refusal detection.
* Application-specific exception translation.
* Structured send-start, send-success, and send-failure events.
* Structured delivery results.

The SMTP service is currently infrastructure only.

Automatic ticket acknowledgement and delivery of AI-generated reply suggestions are intentionally deferred until ticket IDs, database persistence, workflow transaction boundaries, and agent approval flows are implemented.

### Centralized Exception Handling

All application-specific failures inherit from:

```text
SupportIQError
```

Current hierarchy:

```text
SupportIQError
│
├── ConfigurationError
│
├── EmailError
│   │
│   ├── EmailConnectionError
│   ├── EmailAuthenticationError
│   ├── MailboxSelectionError
│   ├── EmailFetchError
│   ├── EmailParsingError
│   │   └── InvalidSenderError
│   │
│   ├── AttachmentError
│   │   ├── AttachmentValidationError
│   │   └── AttachmentStorageError
│   │
│   └── SMTPError
│       ├── SMTPConnectionError
│       ├── SMTPAuthenticationError
│       └── SMTPSendError
│
├── RetryableError
│
└── RetryExhaustedError
```

The hierarchy prevents infrastructure-specific exceptions from leaking across application boundaries and supports typed failure handling for email infrastructure, retries, LLM providers, validation failures, and downstream orchestration.

### Retry Infrastructure

SupportIQ AI includes a generic retry executor designed for reusable transient-failure handling.

Implemented capabilities:

* Configurable maximum attempts.
* Configurable initial delay.
* Exponential backoff.
* Maximum delay enforcement.
* Random jitter.
* Exception-type filtering.
* Retry scheduling events.
* Retry exhaustion events.
* Exception chaining.
* Dependency injection for sleep and random functions.
* Deterministic unit testing.

The retry executor is now selectively integrated into the Groq LLM provider adapter (see [AI Analysis Architecture](#ai-analysis-architecture)).

The retry executor is selectively integrated into both Groq-backed AI capabilities:

```text
Ticket Analysis
Reply Suggestion Generation
```

Transport-level retry integration for IMAP and SMTP has not yet been added.

### Structured Logging

SupportIQ AI emits machine-readable JSON logs.

Example:

```json
{
  "timestamp": "2026-07-05T07:33:42.344287+00:00",
  "level": "INFO",
  "logger": "app.services.smtp_service",
  "message": "SMTP email delivery succeeded.",
  "event": "smtp_send_succeeded",
  "recipient": "customer@example.com",
  "message_id": "<generated-message-id@example.com>"
}
```

Logging infrastructure includes:

* UTC timestamps.
* Log levels.
* Logger names.
* Event names.
* Human-readable messages.
* Context fields.
* Exception serialization.
* Console output.
* Application log output.
* Dedicated error log output.

Logs must not contain credentials, API keys, database passwords, Google App Passwords, or sensitive customer content beyond explicitly approved operational metadata.

### Structured Data Contracts

Pydantic schemas currently represent:

* Parsed attachments.
* Parsed emails.
* Outbound emails.
* Email delivery results.
* Ingestion failures.
* Per-message processing results.
* Batch ingestion results.
* Ticket-analysis requests.
* Ticket-analysis responses.
* Normalized ticket analyses.
* Normalization metadata.
* Reply-suggestion requests.
* Reply-suggestion responses.

These models establish validated contracts between application layers.

### Provider-Independent LLM Service Boundary

The application defines an abstract `LLMService` contract for multiple AI capabilities.

Current capabilities:

```text
analyze_ticket(...)
suggest_reply(...)
```

The concrete Groq integration is implemented by `GroqLLMService`.

This design prevents ticket-processing and agent-assistance workflows from becoming directly coupled to the Groq SDK.

### Versioned Prompt Architecture

SupportIQ AI stores ticket-analysis prompts as versioned application artifacts.

Current prompt capabilities include:

```text
ticket-analysis-v1
reply-suggestion-v1
```

Prompt versions are selected through a central registry.

Prompt definitions provide:

* Explicit prompt identifiers.
* Versioned system instructions.
* Capability-specific user prompt builders.
* Runtime traceability.
* Safer prompt evolution.
* Reproducible evaluation and regression analysis.

Prompt versions are selected through a central registry.

### Robust AI Response Processing

LLM responses are never trusted directly.

The processing pipeline performs:

* Response structure inspection.
* Empty-content detection.
* JSON object extraction.
* JSON object-type validation.
* Pydantic schema validation.
* Unexpected-field rejection.
* Confidence-score range validation.
* Translation into a typed `TicketAnalysisResponse`.

Reply-suggestion responses are also validated before entering downstream workflow logic.

The reply-suggestion pipeline performs:

* Provider completion structure inspection.
* Empty-content detection.
* Whitespace-only content rejection.
* Pydantic reply-response validation.
* Deterministic whitespace normalization.
* Maximum reply-length enforcement.
* Construction of a new validated response object.

### Selective LLM Retry Integration

The generic retry infrastructure is integrated into the Groq provider adapter for both ticket analysis and reply generation.

Retryable failures include:

* Request timeouts.
* Rate-limit failures.
* Connection failures.
* HTTP 5xx provider failures.
* Invalid completion structures.
* Empty suggested replies.
* Whitespace-only suggested replies.

Non-retryable failures include:

* Authentication failures.
* HTTP 4xx request failures.
* Empty model responses.
* Malformed JSON.
* Schema-invalid model responses.

This avoids wasting API quota and processing time retrying permanent failures.

### AI Evaluation Framework

SupportIQ AI includes a reproducible AI evaluation subsystem.

The evaluation pipeline:

```text
Versioned Evaluation Dataset
          │
          ▼
Strict Dataset Validation
          │
          ▼
Evaluation Runner
          │
          ▼
LLMService
          │
          ▼
Validated TicketAnalysisResponse
          │
          ▼
Expected vs Actual Comparison
          │
          ▼
Per-Case EvaluationResult
          │
          ▼
Metric Aggregation
          │
          ├── Structured Output Validity
          ├── Category Accuracy
          ├── Priority Accuracy
          ├── Sentiment Accuracy
          ├── Department Accuracy
          ├── Case-Type Accuracy
          ├── Confidence Statistics
          └── High-Confidence Errors
          │
          ▼
AI Evaluation Report
```

The evaluation framework separates:

* Evaluation data.
* Provider execution.
* Typed analysis results.
* Correctness comparison.
* Metric aggregation.
* Report generation.

This allows prompt versions and future model configurations to be evaluated reproducibly. The current evaluation framework does not yet score reply-suggestion quality.

### Ticket Analysis Normalization Layer

SupportIQ AI includes a dedicated normalization boundary between validated LLM output and deterministic downstream business logic.

The normalization pipeline operates as follows:

```text
TicketAnalysisResponse
        │
        ▼
Text Normalization
        │
        ├── Unicode NFKC Normalization
        ├── Whitespace Normalization
        └── Optional Text Normalization
        │
        ▼
Classification Canonicalization
        │
        ├── Category
        ├── AI-Recommended Priority
        ├── Sentiment
        └── Suggested Department
        │
        ▼
Tag Normalization
        │
        ├── Lowercase Canonicalization
        ├── Slug Formatting
        ├── Empty-Tag Removal
        ├── Duplicate Removal
        └── First-Seen Order Preservation
        │
        ▼
Confidence Normalization
        │
        ├── Defensive Range Clamping
        └── Deterministic Precision
        │
        ▼
Normalization Metadata
        │
        ├── Original Classification Labels
        ├── Classification Change Flags
        ├── Removed Duplicate Tags
        ├── Removed Empty Tags
        └── Confidence Clamp Indicator
        │
        ▼
NormalizedTicketAnalysis
```

The normalization service accepts only a validated `TicketAnalysisResponse` and produces an immutable `NormalizedTicketAnalysis`.

This creates an explicit trust boundary:

```text
Untrusted Provider Output
        │
        ▼
JSON Extraction
        │
        ▼
Strict AI Schema Validation
        │
        ▼
Validated TicketAnalysisResponse
        │
        ▼
Deterministic Normalization
        │
        ▼
Immutable NormalizedTicketAnalysis
        │
        ▼
Priority Assignment and Routing
```

The normalization layer does not:

* Call an LLM provider.
* Assign final business priority.
* Route tickets.
* Persist ticket data.
* Send acknowledgement emails.

These responsibilities remain isolated in downstream services.

Unknown classifications are preserved in normalized textual form instead of being silently mapped to fallback values. This keeps unsupported AI classifications observable for downstream validation, monitoring, and failure handling.

The AI-generated priority is stored as `ai_recommended_priority` rather than the final ticket priority.

This preserves the architectural boundary between:

```text
LLM Recommendation
        │
        ▼
Deterministic Normalization
        │
        ▼
Business Priority Assignment
```

### AI-Generated Reply Suggestions

SupportIQ AI includes an optional bonus capability that generates contextual customer-response drafts for support agents.

The capability consumes:

```text
ParsedEmail
        +
NormalizedTicketAnalysis
```

and produces:

```text
ReplySuggestionResponse
```

The service uses both the original customer message and the trusted normalized ticket-analysis representation.

Generated replies are treated as untrusted AI output and must pass:

```text
Provider Completion Validation
        │
        ▼
Non-Empty Content Validation
        │
        ▼
ReplySuggestionResponse Validation
        │
        ▼
Deterministic Whitespace Normalization
        │
        ▼
Maximum Reply-Length Enforcement
        │
        ▼
Validated Suggested Reply
```

The capability does not automatically send the generated reply.

The intended workflow is:

```text
AI Suggested Reply
        │
        ▼
Agent Review
        │
        ├── Approve
        ├── Edit
        └── Reject
        │
        ▼
SMTP Delivery
```

This preserves human control over customer-facing communication.

---

### Deterministic Priority Assignment

SupportIQ AI includes a deterministic business-rule layer that converts normalized ticket analysis into an explicit final-priority decision.

The priority pipeline operates as follows:

```text
NormalizedTicketAnalysis
        │
        ▼
AI-Recommended Priority Validation
        │
        ▼
Searchable Ticket Context Construction
        │
        ├── Issue Summary
        ├── Detailed Description
        ├── Category
        ├── Product or Service
        └── Normalized Tags
        │
        ▼
Deterministic Business-Rule Matching
        │
        ├── Critical Rules
        ├── High Rules
        ├── Medium Rules
        └── Low Rules
        │
        ▼
Highest Matching Rule Selection
        │
        ▼
AI Recommendation and Rule Reconciliation
        │
        ├── Higher Business Priority → Escalate
        ├── Lower Business Priority → Preserve AI Recommendation
        └── No Rule Match → Preserve AI Recommendation
        │
        ▼
PriorityDecision
```

The priority service produces a new immutable decision object rather than mutating the normalized ticket analysis.

Each priority decision records:

* AI-recommended priority.
* Final business priority.
* Applied rule description.
* Whether the AI recommendation was overridden.

The deterministic rules are evaluated in descending priority order so the highest matching business rule is selected when multiple rules match.

Business rules can escalate priority but cannot downgrade a higher AI-recommended priority.

Priority configuration is validated during service initialization to reject incomplete priority vocabularies, duplicate ranks, empty rule collections, and empty rule phrases.

### Configurable Ticket Routing

SupportIQ AI includes a deterministic routing service that maps canonical normalized ticket categories to configured support teams.

The routing pipeline operates as follows:

```text
NormalizedTicketAnalysis
        │
        ▼
Canonical Category
        │
        ▼
Configured Category-to-Team Mapping
        │
        ├── Technical Support
        ├── Finance
        ├── Sales
        ├── Product Team
        └── Customer Success
        │
        ▼
RoutingDecision
```

Each routing decision records:

* Canonical ticket category.
* Assigned support team.
* Applied routing-rule description.

Routing configuration can be injected into the service, preserving testability and allowing future configuration sources to replace static application mappings.

The routing service validates configuration during initialization and rejects empty routing configurations, empty category values, and empty team values.

Unsupported normalized categories are rejected explicitly through `UnmappedCategoryError` rather than silently routed to a fallback team.

The routing service does not mutate the normalized ticket analysis.

---

### SQLAlchemy Persistence and Repository Architecture

SupportIQ AI includes a dedicated repository layer that isolates application workflow logic from SQLAlchemy persistence operations.

The current persistence boundary is:

```text
Application / Workflow Services
        │
        ▼
Repository Layer
        │
        ├── TicketRepository
        ├── AttachmentRepository
        ├── AuditRepository
        └── WorkflowExecutionRepository
        │
        ▼
SQLAlchemy Session
        │
        ▼
PostgreSQL
```

## Technology Stack

### Backend

* Python 3.12
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### AI Provider

* Groq API
* Groq Python SDK
* Llama 3.3 70B Versatile
* Provider-independent `LLMService` 
* Versioned prompt registry
* Pydantic AI response contracts
* Ticket-analysis generation
* AI-assisted reply generation

### AI Evaluation

* Versioned labeled JSON dataset
* Strict Pydantic evaluation schemas
* Evaluation runner
* Per-label accuracy metrics
* Case-type metrics
* Confidence analysis
* JSON report generation

### Validation and Normalization

* Pydantic structured contracts
* Unicode NFKC normalization
* Deterministic whitespace normalization
* Canonical classification mappings
* Immutable alias maps
* Tag slug normalization
* Stable tag deduplication
* Confidence precision normalization
* Immutable normalized domain contracts
* Normalization metadata
* Suggested-reply normalization
* Maximum reply-length enforcement
* Deterministic priority business rules
* Priority-order configuration
* AI recommendation and business-rule reconciliation
* Immutable priority-decision contracts
* Configurable category-to-team routing
* Immutable routing-decision contracts

### Database

* PostgreSQL
* SQLAlchemy
* Alembic

### Email Integration

* Python `imaplib`
* Python `smtplib`
* Python standard library `email`
* Gmail IMAP
* Gmail SMTP

### Email Parsing

* Python standard library email package
* BeautifulSoup
* lxml

### Resilience and Observability

* Application-specific exception hierarchy
* Generic retry executor
* Exponential backoff
* Jitter support
* Python standard-library logging
* Structured JSON logs
* Typed LLM exception hierarchy
* Selective provider retry integration
* LLM timeout handling
* LLM rate-limit handling
* HTTP 4xx/5xx failure classification
* Application-owned provider retry policy

### Scheduling

Planned:

* APScheduler

### Testing

* pytest
* pytest-cov
* `unittest.mock`

---

## Project Architecture

SupportIQ AI follows a production-oriented modular monolith architecture.

```text
External Interfaces
        │
        ├── Gmail IMAP
        ├── Gmail SMTP
        ├── Groq API
        ├── REST API
        └── Agent Dashboard
        │
        ▼
Application / Orchestration Layer
        │
        ├── Email Ingestion Service
        ├── Ticket Processing Workflow
        ├── Reply Suggestion Service
        └── Ticket Lifecycle Services
        │
        ▼
Domain Services
        │
        ├── Email Parsing
        ├── Attachment Processing
        ├── LLM Analysis
        ├── AI Response Validation
        ├── Ticket Analysis Normalization
        ├── Priority Assignment
        ├── Routing
        ├── AI Reply Suggestion
        └── Acknowledgement Generation
        │
        ▼
Repository / Persistence Layer
        │
        ▼
PostgreSQL
```

Cross-cutting infrastructure:

```text
                    Application Components
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
 Exception Hierarchy    Structured Logging    Retry Executor
```

The architecture minimizes coupling between external infrastructure providers and business logic.

```text
                            LLMService
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            analyze_ticket()          suggest_reply()
                    │                       │
                    ▼                       ▼
        TicketAnalysisResponse    ReplySuggestionResponse
                    │                       │
                    ▼                       ▼
      TicketAnalysisNormalizer    ReplySuggestionService
                    │                       │
                    ▼                       ▼
     NormalizedTicketAnalysis    Validated Suggested Reply
                    │
                    ▼
       Priority Assignment Engine
```
---

---

## Project Structure

```text
SupportIQ-AI/
├── .env
├── .env_example
├── .gitignore
├── README.md
├── app/
│   ├── api/
│   │   └── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── priority_rules.py
│   │   ├── routing_rules.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── retry.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── schema.sql
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   └── runner.py
│   ├── models/
│   │   ├── ticket_attachment.py
│   │   ├── ticket_audit_log.py
│   │   ├── ticket.py
│   │   ├── workflow_execution.py
│   │   └── __init__.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── reply_suggestion_v1.py
│   │   └── ticket_analysis_v1.py
│   ├── scheduler/
│   │   └── __init__.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── ticket_attachment.py
│   │   ├── ticket_audit_log.py
│   │   ├── ticket.py
│   │   └── workflow_execution.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── email_schema.py
│   │   ├── evaluation_schema.py
│   │   ├── ingestion_schema.py
│   │   ├── normalized_ticket_schema.py
│   │   ├── smtp_schema.py
│   │   ├── reply_suggestion_schema.py
│   │   ├── ticket_decision_schema.py
│   │   └── ticket_analysis_schema.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── attachment_service.py
│   │   ├── email_ingestion_service.py
│   │   ├── email_parser.py
│   │   ├── groq_llm_service.py
│   │   ├── imap_service.py
│   │   ├── llm_service.py
│   │   ├── reply_suggestion_service.py
│   │   ├── smtp_service.py
│   │   ├── priority_service.py
│   │   ├── routing_service.py
│   │   └── ticket_analysis_normalizer.py
│   └── utils/
│       ├── __init__.py
│       ├── json_extractor.py
│       └── text_normalizer.py
├── docs/
│   ├── ai_evaluation_report.json
│   └── prompts.md
├── logs/
├── main.py
├── pytest.ini
├── requirements.txt
├── sample_data/
│   └── ai_evaluation_dataset.json
├── tests/
│   ├── __init__.py
│   ├── confest.py
│   ├── manual_run_ai_evaluation.py
│   ├── manual_test_groq.py
│   ├── manual_test_imap.py
│   ├── manual_test_smtp.py
│   ├── test_attachment_service.py
│   ├── test_email_ingestion_service.py
│   ├── test_email_parser.py
│   ├── test_evaluation_metrics.py
│   ├── test_evaluation_schema.py
│   ├── test_groq_llm_service.py
│   ├── test_json_extractor.py
│   ├── test_retry.py
│   ├── test_smtp_service.py
│   ├── test_text_normalizer.py
│   ├── test_ticket_analysis_normalizer.py
│   ├── manual_test_reply_suggestion.py
│   ├── test_reply_suggestion_schema.py
│   ├── test_priority_service.py
│   ├── test_reply_suggestion_service.py
│   ├── test_routing_service.py
│   ├── test_ticket_analysis_schema.py
│   ├── test_attachment_repository.py
│   ├── test_audit_repository.py
│   ├── test_ticket_repository.py
│   └── test_workflow_execution_repository.py
├── uploads/
│   ├── attachments/
│   └── emails/
└── workflow/
```

Runtime-generated attachments, logs, secrets, virtual environments, Python cache files, test caches, coverage artifacts, and local customer data should be excluded from version control.

---

## Database Design

SupportIQ AI uses PostgreSQL as the primary relational database.

Database name:

```text
supportiq-ai
```

### `tickets`

Stores the primary customer support ticket.

Fields include:

* Internal database ID.
* Unique ticket number.
* Customer name.
* Company.
* Sender email.
* Email subject.
* Original email body.
* AI-generated issue summary.
* Detailed description.
* Category.
* Priority.
* Sentiment.
* Product or service.
* Suggested department.
* Assigned team.
* Confidence score.
* Ticket status.
* Received timestamp.
* Updated timestamp.

### `attachments`

Stores attachment metadata associated with tickets.

```text
Ticket 1 ──────── * Attachments
```

### `tags`

Stores normalized ticket tags.

```text
Ticket 1 ──────── * Tags
```

Tags are stored as individual records rather than comma-separated values.

### `audit_logs`

Stores historical ticket actions and changes.

Examples:

* Ticket created.
* Category changed.
* Priority changed.
* Assigned team changed.
* Status changed.
* Ticket resolved.
* Ticket closed.

```text
Ticket 1 ──────── * Audit Logs
```

### `internal_notes`

Stores support-agent comments that are not visible to customers.

```text
Ticket 1 ──────── * Internal Notes
```

### Database Relationships

```text
                       tickets
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    attachments          tags        audit_logs

                          │
                          ▼
                   internal_notes
```

Database indexes are defined for frequently queried fields such as:

* Ticket status.
* Priority.
* Category.
* Sender email.
* Received timestamp.

---

## Email Infrastructure Architecture

The implemented email infrastructure currently operates as follows:

```text
                        Gmail
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
        IMAP Transport            SMTP Transport
             │                         │
             ▼                         ▼
       MIME Email Parser        OutboundEmail Schema
             │                         │
             ▼                         ▼
     Attachment Processing       Message Construction
             │                         │
             ▼                         ▼
     ParsedEmail Contract        STARTTLS + Authentication
             │                         │
             ▼                         ▼
   EmailIngestionService       EmailDeliveryResult
             │
             ▼
     IngestionBatchResult
```

Emails are intentionally not marked as read during retrieval.

The final workflow will explicitly update email processing state only after reaching the defined success boundary.

---

## Email Ingestion Orchestration

The ingestion orchestration pipeline currently operates as follows:

```text
EmailIngestionService
        │
        ▼
Connect to IMAP
        │
        ▼
Fetch Unread Emails
        │
        ▼
Process Each Message Independently
        │
        ├── Validate Message-ID
        ├── Validate Body
        ├── Record Structured Failure
        └── Record Structured Success
        │
        ▼
Aggregate Batch Metrics
        │
        ├── Total Messages
        ├── Successful Messages
        ├── Failed Messages
        └── Skipped Messages
        │
        ▼
Attempt IMAP Disconnect
        │
        ▼
Return IngestionBatchResult
```

A malformed message does not terminate processing of all other messages in the batch.

This establishes the application orchestration boundary that will later coordinate:

```text
Email
  ↓
LLM Analysis
  ↓
Validation
  ↓
Priority Assignment
  ↓
Routing
  ↓
Database Transaction
  ↓
Acknowledgement
  ↓
Mark Email as Processed
```

---

## AI Analysis Architecture

SupportIQ AI isolates AI-provider infrastructure from the application workflow through a provider-independent service contract.

```text
ParsedEmail
    │
    ▼
TicketAnalysisRequest
    │
    ▼
Prompt Registry
    │
    ├── Prompt Name
    ├── Prompt Version
    ├── System Prompt
    └── User Prompt Builder
    │
    ▼
LLMService
    │
    ▼
GroqLLMService
    │
    ├── Groq API Client
    ├── Timeout Handling
    ├── Rate-Limit Handling
    ├── HTTP Failure Classification
    └── Selective Retry Execution
    │
    ▼
Raw Model Response
    │
    ▼
JSON Object Extraction
    │
    ▼
Pydantic Schema Validation
    │
    ▼
TicketAnalysisResponse
```

Application workflow code depends on:

```text
LLMService
```

rather than directly depending on:

```text
Groq
```

This service boundary reduces provider coupling and allows a different LLM provider to be introduced without redesigning the downstream ticket-processing workflow.

### Structured Ticket Analysis

The AI analysis contract currently produces:

* Customer name.
* Company.
* Issue summary.
* Detailed issue description.
* Issue category.
* Recommended priority.
* Sentiment.
* Product or service.
* Suggested department.
* Suggested tags.
* Confidence score.

AI output is treated as untrusted data.

Every response must pass through:

```text
Raw Provider Output
        │
        ▼
JSON Extraction
        │
        ▼
Object-Type Validation
        │
        ▼
TicketAnalysisResponse Validation
        │
        ▼
Validated Structured Analysis
```

The validated AI response will later pass through deterministic category normalization, priority assignment, routing, and persistence layers.

### Prompt Versioning

AI prompts are explicitly versioned by capability.

Current version:

```text
ticket-analysis-v1
reply-suggestion-v1
```

Prompt definitions contain:

* Prompt name.
* Prompt version.
* System prompt.
* User prompt builder.

Prompt selection is performed through a prompt registry.

Existing prompt versions should not be overwritten when prompt behavior changes.

Future prompt improvements should create a new version:

```text
ticket-analysis-v1
        │
        ├── Original Instructions
        ├── Evaluation Dataset
        └── Evaluation Results

ticket-analysis-v2
        │
        ├── Modified Instructions
        ├── New Evaluation Results
        └── Measurable Comparison
```

This supports reproducibility, regression analysis, and explicit prompt-engineering evaluation.

### LLM Retry and Failure Classification

Only transient provider failures are retried.

```text
LLM Request
    │
    ├── Timeout ───────────────► Retry
    ├── Rate Limit ────────────► Retry
    ├── Connection Failure ────► Retry
    ├── HTTP 5xx ──────────────► Retry
    │
    ├── Authentication Error ──► Fail Immediately
    ├── HTTP 4xx ──────────────► Fail Immediately
    ├── Empty Response ────────► Fail Immediately
    ├── Malformed JSON ────────► Fail Immediately
    └── Invalid Schema ────────► Fail Immediately
```

The Groq adapter uses the application's generic retry executor rather than implementing a provider-specific retry loop.

After retry exhaustion, the original typed LLM failure is preserved at the service boundary.

This allows downstream workflow components to distinguish between:

* Timeouts.
* Rate limits.
* Provider availability failures.
* Authentication failures.
* Invalid requests.
* Malformed responses.
* Schema-invalid responses.

---

## AI Evaluation Architecture

Hour 5 introduced a reproducible AI evaluation subsystem.

```text
sample_data/ai_evaluation_dataset.json
                    │
                    ▼
          Evaluation Dataset Schema
                    │
                    ▼
              EvaluationRunner
                    │
                    ▼
                 LLMService
                    │
                    ▼
         TicketAnalysisResponse
                    │
                    ▼
         Expected Label Comparison
                    │
                    ▼
           EvaluationResult Models
                    │
                    ▼
          calculate_evaluation_metrics()
                    │
                    ▼
             EvaluationMetrics
                    │
                    ▼
      docs/ai_evaluation_report.json
```

The dataset includes:

* Standard support tickets.
* Priority-sensitive cases.
* Ambiguous requests.
* Adversarial and prompt-injection-oriented cases.

The evaluation framework measures:

* Structured-output validity.
* Category accuracy.
* Priority accuracy.
* Sentiment accuracy.
* Department accuracy.
* Per-case-type all-label accuracy.
* Average confidence.
* Average confidence for correct predictions.
* Average confidence for incorrect predictions.
* High-confidence error count.

---

## Ticket Analysis Normalization Architecture

Hour 6 introduced a deterministic normalization layer between validated AI output and downstream business decision logic.

```text
Raw LLM Response
        │
        ▼
JSON Object Extraction
        │
        ▼
TicketAnalysisResponse
        │
        ▼
TicketAnalysisNormalizer
        │
        ├── Text Normalization
        ├── Classification Canonicalization
        ├── Tag Normalization
        ├── Confidence Normalization
        └── Metadata Construction
        │
        ▼
NormalizedTicketAnalysis
        │
        ▼
Priority Assignment Engine
        │
        ▼
Routing Engine
        │
        ▼
Persistence
```

### Text Normalization

Text normalization provides deterministic cleanup of AI-generated textual values.

Implemented behavior includes:

* Unicode NFKC normalization.
* Leading and trailing whitespace removal.
* Repeated whitespace collapsing.
* Newline and tab normalization.
* Optional empty-value conversion to None.

### Classification Canonicalization

The normalization service canonicalizes known aliases for:

* Category.
* AI-recommended priority.
* Sentiment.
* Suggested department.

Examples:

```text
tech_support
        ↓
Technical Support

urgent
        ↓
Critical

frustrated
        ↓
Negative

engineering
        ↓
Technical Support
```

Alias mappings are immutable application configuration.

Canonical values remain aligned with the current ticket-analysis prompt vocabulary.

Unknown values are preserved in normalized textual form rather than silently converted to fallback classifications.

This ensures unsupported AI classifications remain observable.

### Tag Normalization

Suggested AI tags are normalized into deterministic slug-style values.

Example:

```text
Payment API
HTTP 503 / Payment Failure!
PAYMENT_API
""
```

becomes:

```text
payment-api
http-503-payment-failure
```

The normalization algorithm:

* Applies Unicode normalization.
* Normalizes whitespace.
* Converts text to lowercase.
* Converts separators and unsupported characters to hyphens.
* Removes leading and trailing hyphens.
* Removes empty normalized tags.
* Removes duplicate normalized tags.
* Preserves first-seen order.

### Confidence Normalization

Confidence scores are normalized to deterministic precision.

Example:

```text
0.876543
```

becomes:

```text
0.8765
```

Defensive clamping support exists to keep values within:

```text
0.0 <= confidence_score <= 1.0
```

The upstream TicketAnalysisResponse contract already rejects out-of-range confidence values, so clamping is defensive rather than a replacement for schema validation.

### Normalization Metadata

Each normalized analysis contains metadata describing normalization behavior.

Metadata includes:

* Original category.
* Original priority.
* Original sentiment.
* Original department.
* Whether category normalization occurred.
* Whether priority normalization occurred.
* Whether sentiment normalization occurred.
* Whether department normalization occurred.
* Number of removed duplicate tags.
* Number of removed empty tags.
* Whether confidence clamping occurred.

This provides observability and future audit support without mutating the original AI response.

### Immutability

NormalizedTicketAnalysis and NormalizationMetadata are immutable Pydantic contracts.

This prevents downstream services from accidentally modifying normalized AI analysis after the normalization boundary.

### Separation of AI Recommendation and Business Decision

The normalized schema stores the AI priority as:

```text
ai_recommended_priority
```

The final ticket priority will be assigned by the deterministic priority engine.

This produces the intended architecture:

```text
AI Recommendation
        │
        ▼
Schema Validation
        │
        ▼
Deterministic Normalization
        │
        ▼
Business Priority Assignment
        │
        ▼
Final Ticket Priority
```

---

## AI Reply Suggestion Architecture

Hour 6.5 introduced the optional AI-generated reply-suggestion capability.

```text
ParsedEmail
      │
      │
      ├────────────────────────────┐
      │                            │
      ▼                            ▼
Ticket Analysis          Original Customer Context
      │                            │
      ▼                            │
Schema Validation                 │
      │                            │
      ▼                            │
Ticket Analysis Normalization     │
      │                            │
      ▼                            │
NormalizedTicketAnalysis          │
      │                            │
      └──────────────┬─────────────┘
                     ▼
          ReplySuggestionService
                     │
                     ▼
          ReplySuggestionRequest
                     │
                     ▼
              LLMService
                     │
                     ▼
             GroqLLMService
                     │
                     ▼
         Versioned Reply Prompt
                     │
                     ▼
         Raw Plain-Text Completion
                     │
                     ▼
         ReplySuggestionResponse
                     │
                     ▼
       Deterministic Reply Normalization
                     │
                     ▼
        Maximum Reply-Length Policy
                     │
                     ▼
         Validated Suggested Reply
                     │
                     ▼
              Future Agent Review
```

### Reply Suggestion Input Boundary

The reply-suggestion service consumes:

```text
ParsedEmail
NormalizedTicketAnalysis
```

This provides the model with:

* Original sender context.
* Original email subject.
* Original customer message.
* Normalized issue summary.
* Normalized detailed description.
* Canonical category.
* AI-recommended priority.
* Canonical sentiment.
* Product or service context.
* Suggested department.
* Normalized tags.
* Confidence metadata when included by the prompt contract.

### Provider-Independent Reply Generation

Reply generation is exposed through:

```text
LLMService.suggest_reply(...)
```

The Groq-specific implementation remains isolated inside:

```text
GroqLLMService
```

This prevents `ReplySuggestionService` from depending directly on the Groq SDK.

### Reply Response Validation

Suggested replies are treated as untrusted provider output.

The provider adapter rejects:

* Invalid completion structures.
* Empty completion content.
* Whitespace-only completion content.

The reply-suggestion service then performs:

* Typed response handling.
* Deterministic whitespace normalization.
* Maximum reply-length enforcement.
* New validated response construction.

### Human-in-the-Loop Boundary

The reply-suggestion capability does not send email automatically.

The intended boundary is:

```text
AI Draft
   │
   ▼
Agent Review
   │
   ├── Approve
   ├── Edit
   └── Reject
   │
   ▼
SMTP Delivery
```

This preserves support-agent control over customer-facing communication.

---

## Prompt Engineering and Documentation

Executable prompt definitions are stored under:

```text
app/prompts/
```

The current evaluated prompt implementation is:

```text
app/prompts/ticket_analysis_v1.py
```

Prompt selection is performed through:

```text
app/prompts/registry.py
```

Human-readable prompt documentation required for submission is stored in:

```text
docs/prompts.md
```

The prompt documentation records:

* Prompt identifier.
* Prompt version.
* Prompt purpose.
* Runtime implementation path.
* Runtime usage path.
* Model configuration.
* System prompt.
* User prompt template.
* Input contract.
* Output contract.
* Allowed classification vocabularies.
* Null semantics.
* Confidence-score semantics.
* Hallucination-reduction constraints.
* Prompt-injection defenses.
* Validation behavior.
* Evaluation dataset.
* Baseline evaluation results.
* Known limitations.
* Prompt evolution policy.

The generated evaluation evidence is stored in:

```text
docs/ai_evaluation_report.json
```

---

## SMTP Transport

SupportIQ AI sends outbound emails through Gmail SMTP using:

```text
smtp.gmail.com:587
```

Transport security:

```text
SMTP
  ↓
EHLO
  ↓
STARTTLS
  ↓
TLS Context
  ↓
EHLO
  ↓
Authentication
  ↓
Message Delivery
```

Real SMTP delivery has been manually verified using the configured support account and an actual recipient mailbox.

The received message successfully rendered the HTML alternative body.

Automatic customer acknowledgements are not yet enabled because the complete ticket-processing transaction boundary has not been implemented.

---

## Exception Architecture

Infrastructure-specific failures are translated into application-specific exceptions.

Example:

```text
smtplib.SMTPAuthenticationError
              │
              ▼
SMTPAuthenticationError
              │
              ▼
Application Orchestration Layer
```

This design provides:

* Stable application contracts.
* Reduced infrastructure coupling.
* Explicit failure categories.
* Easier retry decisions.
* Easier API error translation.
* Improved unit testing.
* Better operational observability.

---

## Retry Infrastructure

The retry subsystem uses a configurable policy and generic executor.

Example backoff progression:

```text
Attempt 1 fails
      │
      ▼
Initial Delay + Jitter
      │
      ▼
Attempt 2 fails
      │
      ▼
Initial Delay × Exponential Base + Jitter
      │
      ▼
Attempt 3 fails
      │
      ▼
RetryExhaustedError
```

Only configured exception types are retried.

Permanent failures should not be retried.

Examples of permanent failures:

* Invalid credentials.
* Invalid customer input.
* Unsupported attachments.
* AI schema validation failures after repair limits are exhausted.
* SMTP recipient rejection.

Examples of potentially transient failures:

* Connection timeouts.
* Temporary network failures.
* Provider rate limits.
* Temporary Groq service failures.
* Temporary database connectivity failures.

---

## Structured Logging

Logging is configured centrally in:

```text
app/core/logging.py
```

Current destinations:

```text
Console
logs/supportiq.log
logs/errors.log
```

Structured logs improve:

* Failure investigation.
* Event correlation.
* Automated log processing.
* Future metrics extraction.
* Demo visibility.
* Production readiness.

---

## Attachment Security

Incoming email attachments are treated as untrusted input.

### Filename Sanitization

Directory path components are removed and unsafe characters are replaced.

Example:

```text
../../customer screenshots/error image.png

↓

error_image.png
```

### Extension Allowlist

Only configured attachment extensions are accepted.

Example configuration:

```text
pdf,png,jpg,jpeg,txt,docx
```

### Maximum Attachment Size

Attachments exceeding the configured maximum size are rejected.

Example default:

```text
10 MB
```

### Unique Stored Filenames

Accepted attachments are assigned UUID-based stored filenames to reduce collision risk.

### Runtime Storage Exclusion

Runtime attachment directories should be excluded from Git to prevent customer data and test artifacts from being committed.

---

## Configuration Management

Configuration is centralized in:

```text
app/config/settings.py
```

The application uses `pydantic-settings` to:

* Load environment variables.
* Apply default values.
* Validate numeric constraints.
* Normalize attachment extension configuration.
* Expose configuration through a centralized settings object.
* Cache application settings.

Application services do not independently load `.env` values.

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_actual_groq_api_key

GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TIMEOUT_SECONDS=30
GROQ_MAX_TOKENS=1200
GROQ_TEMPERATURE=0.1
LLM_MAX_RETRIES=3

PROMPT_VERSION=ticket-analysis-v1

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/supportiq-ai

EMAIL_ADDRESS=your_support_email@gmail.com
EMAIL_PASSWORD=your_google_app_password

IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

EMAIL_POLL_INTERVAL_SECONDS=60
EMAIL_FOLDER=INBOX
EMAIL_MARK_AS_READ_AFTER_SUCCESS=true

MAX_ATTACHMENT_SIZE_MB=10
ALLOWED_ATTACHMENT_TYPES=pdf,png,jpg,jpeg,txt,docx
```

Never commit `.env`.

The repository should contain `.env_example` with placeholders only.

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SupportIQ-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Command Prompt:

```cmd
venv\Scripts\activate
```

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Create the PostgreSQL Database

```sql
CREATE DATABASE "supportiq-ai";
```

### 6. Create Database Tables

Execute:

```text
app/database/schema.sql
```

The schema creates:

```text
tickets
attachments
tags
audit_logs
internal_notes
```

### 7. Configure Environment Variables

Copy:

```text
.env_example
```

to:

```text
.env
```

Then configure the required credentials and database connection.

### 8. Configure Gmail Authentication

The support inbox requires:

* A Google account.
* 2-Step Verification enabled.
* A Google App Password.

Use the generated App Password as:

```text
EMAIL_PASSWORD
```

Do not use the normal Google account password.

---

## Running Integration Tests

### IMAP

```bash
python -m tests.manual_test_imap
```

### SMTP

```bash
python -m tests.manual_test_smtp
```

### Real Groq Smoke Test

```bash
python -m tests.manual_test_groq
```

The Groq smoke test verifies:

* Real provider connectivity.
* Prompt registry selection.
* Prompt construction.
* Structured provider output.
* JSON extraction.
* Pydantic validation.
* Typed ticket-analysis response creation.

---

## Running AI Evaluation

Run the complete real-provider AI evaluation:

```bash
python -m tests.manual_run_ai_evaluation
```

The evaluation:

1. Loads the versioned labeled dataset.
2. Validates the dataset schema.
3. Executes every case through `LLMService`.
4. Validates structured model output.
5. Compares actual labels with expected labels.
6. Calculates aggregate metrics.
7. Calculates confidence statistics.
8. Generates the persistent evaluation report.

Output:

```text
docs/ai_evaluation_report.json
```

Real-provider evaluation consumes Groq API quota and may encounter provider rate limits.

---

## Running Automated Tests

Run the complete automated test suite:

```bash
python -m pytest -v
```

Current result:

```text
203 passed
1 warning
0 failures
```

Run the Hour 6 normalization tests:

```bash
python -m pytest tests/test_text_normalizer.py tests/test_ticket_analysis_normalizer.py -v
```

Current result:

```text
43 passed
```

Run the focused Hour 6.5 reply-suggestion tests:

```bash
python -m pytest tests/test_reply_suggestion_schema.py tests/test_reply_suggestion_service.py tests/test_groq_llm_service.py -v
```

Run the focused Hour 7 priority and routing tests:

```bash
python -m pytest tests/test_priority_service.py tests/test_routing_service.py -v
```

Run the focused Hour 8 repository tests:

```bash
python -m pytest tests/test_ticket_repository.py tests/test_attachment_repository.py tests/test_audit_repository.py tests/test_workflow_execution_repository.py -v
```

The complete automated suite verifies:

* Attachment security and validation.
* Email parsing.
* Email ingestion orchestration.
* SMTP transport behavior.
* Generic retry behavior.
* JSON extraction.
* Ticket-analysis schema contracts.
* Groq provider behavior with mocked network boundaries.
* LLM failure classification.
* Selective retry behavior.
* Evaluation dataset validation.
* Evaluation metric calculation.
* Failed-analysis accounting.
* Case-type accuracy.
* Confidence statistics.
* Empty evaluation result handling.
* Unicode text normalization.
* Whitespace normalization.
* Optional-text normalization.
* Classification alias canonicalization.
* Unknown classification preservation.
* Tag normalization.
* Empty-tag removal.
* Duplicate-tag removal.
* Stable tag ordering.
* Confidence precision normalization.
* Normalization metadata.
* Original AI response immutability.
* Normalized contract immutability.
* Strict normalized schema validation.
* Reply-suggestion schema validation.
* Reply-suggestion service orchestration.
* Reply normalization.
* Maximum reply-length enforcement.
* Groq reply-generation behavior.
* Reply-generation retry classification.
* Plain-text response-format behavior.
* Deterministic priority business-rule matching.
* Highest-priority rule selection.
* AI recommendation and business-rule reconciliation.
* Prevention of priority downgrading.
* Priority configuration validation.
* Category-to-team routing.
* Routing configuration injection.
* Routing configuration validation.
* Unsupported-category rejection.
* Priority and routing input immutability.
* SQLAlchemy ticket persistence.
* Ticket lookup by ID.
* Ticket lookup by ticket number.
* Attachment metadata persistence.
* Attachment lookup by ticket ID.
* Attachment query-order preservation.
* Audit-event persistence.
* Audit-event lookup by ticket ID.
* Workflow-execution persistence.
* Workflow-execution lookup by Message-ID.
* Duplicate Message-ID rejection.
* Repository exception translation.
* Integrity-error translation.
* Explicit caller-owned transaction boundaries.
* Repository non-commit behavior.

Automated tests do not consume Groq API quota.

---

## Test Coverage

Generate application-wide coverage:

python -m pytest --cov=app --cov-report=term-missing -v

Generate focused Hour 7 service coverage:

python -m pytest tests/test_priority_service.py tests/test_routing_service.py --cov=app.services.priority_service --cov=app.services.routing_service --cov-report=term-missing

Name                                                Stmts   Miss  Cover
---------------------------------------------------------------------------------
app/repositories/__init__.py                            5      0   100%
app/repositories/attachment_repository.py              21      0   100%
app/repositories/audit_repository.py                   21      0   100%
app/repositories/ticket_repository.py                  28      0   100%
app/repositories/workflow_execution_repository.py      23      0   100%
---------------------------------------------------------------------------------
TOTAL                                                  98      0   100%

Current regression status:

203 passed
1 warning
0 failures

The warning originates from the BeautifulSoup/lxml dependency and does not affect application behavior.

A fresh application-wide `--cov=app` report should be captured during the dedicated testing and hardening phase before final submission.

---

## AI Evaluation Results

Baseline real-provider evaluation for:

```text
Prompt Version: ticket-analysis-v1
Model: llama-3.3-70b-versatile
Dataset Version: 1.0.0
Total Cases: 24
```

Results:

```text
Successful Analyses:            24
Failed Analyses:                 0

Structured Output Validity:    100.00%

Category Accuracy:              75.00%
Priority Accuracy:              66.67%
Sentiment Accuracy:             79.17%
Department Accuracy:            79.17%

Standard Case Accuracy:         41.67%
Priority-Sensitive Accuracy:   100.00%
Ambiguous Case Accuracy:        50.00%
Adversarial Case Accuracy:      50.00%

Average Confidence:              0.8208
Average Confidence (Correct):    0.8154
Average Confidence (Incorrect):  0.8273

High-Confidence Errors:         10
```

### Evaluation Findings

The baseline evaluation demonstrates:

* The AI pipeline produced schema-valid structured output for every evaluation case.
* Priority-sensitive cases achieved perfect all-label accuracy in the current dataset.
* Category and priority classification remain improvement areas.
* Ambiguous and adversarial cases expose classification limitations.
* Confidence scores are not yet well calibrated.
* Incorrect predictions received slightly higher average confidence than correct predictions.
* High-confidence errors demonstrate that confidence scores must not be used as the sole basis for automated business decisions.

These findings support the planned hybrid design:

```text
LLM Recommendation
        │
        ▼
Schema Validation
        │
        ▼
Normalization
        │
        ▼
Deterministic Priority Rules
        │
        ▼
Configurable Routing
        │
        ▼
Persisted Ticket Decision
```

The complete machine-readable evaluation report is stored in:

```text
docs/ai_evaluation_report.json
```

---

## Current Limitations

At the end of Hour 7:

* Priority assignment currently uses configured phrase-based deterministic business rules and does not yet support database-managed or administrator-editable rules.
* Priority-rule matching currently uses normalized substring matching rather than token-boundary, regex, or semantic rule evaluation.
* Priority decisions are not yet persisted in PostgreSQL.
* Routing currently uses static application configuration rather than database-managed or administrator-editable routing rules.
* Unsupported normalized categories are explicitly rejected, but no quarantine, dead-letter, or manual-review workflow is implemented yet.
* Priority and routing decisions are not yet integrated into the complete ticket-processing orchestration workflow.
* AI confidence scores are not calibrated.
* The baseline prompt produces high-confidence classification errors.
* Standard, ambiguous, and adversarial cases require future prompt or business-rule improvements.
* Only `ticket-analysis-v1` has been evaluated.
* Prompt-version comparison has not yet been performed.
* Ticket creation is not implemented.
* Automatic acknowledgement orchestration is not implemented.
* Inbox polling scheduler is not implemented.
* Duplicate email processing prevention is not implemented.
* Emails are not yet marked as processed by the complete workflow.
* Retry infrastructure is not yet integrated into IMAP, SMTP, database, or full workflow orchestration boundaries.
* Ticket REST APIs are not implemented.
* Manual agent review is not implemented.
* Ticket lifecycle transitions are not implemented.
* Support dashboard is not implemented.
* Automated IMAP transport unit tests are not yet implemented.
* Sensitive-data redaction filters are not yet implemented.
* Reply suggestions require agent review and are not automatically sent.
* Reply-suggestion quality does not yet have a dedicated evaluation framework.
* Suggested replies are not yet persisted in PostgreSQL.
* No agent approval/edit/reject workflow is implemented yet.
* Repository persistence operations are implemented, but they are not yet integrated into the complete ticket-processing orchestration workflow.
* Caller-owned transaction boundaries are established at the repository layer, but the end-to-end workflow transaction coordinator is not yet implemented.
* Workflow-execution Message-ID lookup is implemented as the persistence foundation for idempotency, but duplicate-email prevention is not yet integrated into the complete processing workflow.
* Ticket, attachment, and audit-log repositories are implemented, but ticket creation orchestration has not yet been connected to them.
* Tag persistence and internal-note persistence repositories are not yet implemented.
* Database integration tests against a real PostgreSQL test database are not yet implemented.

---

## Security Considerations

### Implemented

* Secrets stored in `.env`.
* `.env` excluded from Git.
* Google App Password authentication.
* IMAP over SSL.
* SMTP STARTTLS encryption.
* Attachment extension allowlisting.
* Maximum attachment size enforcement.
* Filename sanitization.
* Directory traversal protection.
* UUID-based stored filenames.
* Pydantic data validation.
* Runtime uploads excluded from Git.
* Non-destructive email fetching.
* Centralized application exception hierarchy.
* Infrastructure exception translation.
* Structured logging.
* No intentional credential logging.
* Per-message failure isolation.
* LLM prompt input boundaries.
* AI output schema validation.
* Prompt-injection mitigation instructions.
* LLM output trust boundaries.
* Selective retry of transient LLM provider failures.
* Groq SDK automatic retries disabled.
* Application-owned retry policy.
* Reproducible labeled AI evaluation.
* Adversarial evaluation cases.
* Unicode NFKC normalization before downstream business processing.
* Deterministic normalization of AI-generated textual values.
* Canonical classification normalization.
* Preservation of unknown classifications for downstream observability.
* Deterministic tag normalization and deduplication.
* Immutable normalized ticket-analysis contracts.
* Preservation of original AI classifications in normalization metadata.
* Separation of AI-recommended priority from final business priority.
* Customer-facing AI-generated replies are not automatically sent.
* Suggested replies remain subject to human review.
* Customer email content and normalized ticket context are treated as untrusted prompt inputs.
* Reply-suggestion prompts must preserve prompt-injection defenses and explicit data boundaries.
* Deterministic priority escalation rules.
* Prevention of lower-priority rule downgrades.
* Explicit priority configuration validation.
* Explicit routing configuration validation.
* Explicit rejection of unsupported routing categories.
* Immutable priority and routing decision processing.
* SQLAlchemy-based persistence abstraction.
* Repository-level SQLAlchemy exception translation.
* Repository-level integrity-error translation.
* Explicit caller-owned transaction boundaries.
* Prevention of implicit repository commits.
* Unique Message-ID persistence support for future idempotent workflow processing.
* Alembic-managed database schema evolution.

### Planned

* Database transaction boundaries.
* Parameterized persistence through SQLAlchemy.
* Restricted ticket status transitions.
* Idempotent email processing.
* Duplicate ticket prevention.
* Retry integration at IMAP/SMTP/database orchestration boundaries.
* Sensitive-data redaction filters.
* API input validation.
* API error response sanitization.
* Attachment MIME signature validation.
* Database connection pooling.

---

## Design Decisions

### Why a Modular Monolith?

The project uses a modular monolith rather than premature microservices.

This provides:

* Clear service boundaries.
* Lower deployment complexity.
* Easier local development.
* Straightforward debugging.
* Strong transactional capabilities.
* Independent testing of modules.
* A future migration path toward distributed services if scale requires it.

### Why PostgreSQL?

PostgreSQL provides:

* Strong relational consistency.
* Foreign-key constraints.
* Transaction support.
* Indexing.
* Production-oriented concurrency.
* Reliable structured persistence.
* Compatibility with SQLAlchemy and Alembic.

### Why Groq?

Groq is used as the LLM inference provider because it provides fast inference and supports instruction-tuned models suitable for classification, summarization, sentiment analysis, priority recommendation, and structured ticket extraction.

The AI integration is isolated behind a service boundary to reduce provider coupling.

### Why IMAP and SMTP?

IMAP and SMTP provide direct code-driven email integration without requiring paid workflow automation services.

IMAP is used for receiving customer support requests.

SMTP provides the reusable outbound transport foundation for acknowledgement emails.

### Why `BODY.PEEK[]`?

SupportIQ AI retrieves messages without automatically marking them as read.

This prevents messages from being silently lost if downstream processing fails.

The final workflow will update email state only after reaching the defined success boundary.

### Why a Centralized Exception Hierarchy?

A centralized exception hierarchy prevents transport-library exceptions from leaking throughout the application.

This improves:

* Maintainability.
* Retry classification.
* API error mapping.
* Testing.
* Observability.

### Why Generic Retry Infrastructure?

External dependencies such as email servers, LLM providers, and databases can fail transiently.

A reusable retry executor prevents duplicated retry implementations and allows retry policy to remain consistent across infrastructure boundaries.

### Why Structured JSON Logging?

Machine-readable logs are easier to search, aggregate, analyze, and integrate with future observability platforms.

Structured event fields also improve failure diagnosis during demonstrations and evaluation.

### Why Pydantic Schemas?

Pydantic models establish validated contracts between application layers.

They improve:

* Type safety.
* Maintainability.
* Input validation.
* Testability.
* API compatibility.
* Error visibility.

### Why Separate Attachment Processing?

Attachment handling is isolated from IMAP transport and MIME parsing.

This allows attachment validation and storage to be tested independently and replaced later with object storage if required.

### Why Is SMTP Implemented Before Automatic Acknowledgements?

SMTP is infrastructure.

Automatic acknowledgements belong to the end-to-end ticket-processing workflow.

Separating transport from business orchestration prevents outbound email delivery from becoming tightly coupled to ticket creation logic.

### Why a Provider-Independent LLM Boundary?

The application workflow depends on an abstract `LLMService` contract rather than directly depending on the Groq SDK.

This reduces infrastructure coupling and allows the provider implementation to be replaced without redesigning downstream ticket-processing logic.

### Why Version Prompts?

Prompt changes can alter classification accuracy, priority recommendations, confidence scores, and downstream workflow behavior.

Explicit prompt versions provide:

* Reproducibility.
* Regression comparison.
* Evaluation traceability.
* Safer prompt evolution.
* Clear documentation of the exact prompt used during demonstration and evaluation.

### Why Treat LLM Output as Untrusted Data?

Large Language Models may produce malformed JSON, missing fields, unexpected fields, invalid confidence values, or responses that violate application expectations.

SupportIQ AI therefore validates all model output before allowing it to enter downstream business logic or persistence layers.

### Why Retry Only Transient LLM Failures?

Retrying permanent failures wastes API quota, increases latency, and can amplify operational failures.

SupportIQ AI retries only failures that may succeed on a subsequent attempt:

* Timeouts.
* Rate limits.
* Connection failures.
* Provider-side HTTP 5xx failures.

Authentication errors, invalid requests, malformed responses, and schema-invalid responses fail immediately.

### Why Disable Groq SDK Retries?

The application already owns retry policy.

Disabling SDK retries prevents nested retry behavior and ensures:

* Predictable retry counts.
* Centralized backoff policy.
* Consistent structured logging.
* Typed retry exhaustion behavior.
* Easier deterministic testing.

### Why Structured JSON Logging?

Machine-readable logs improve event correlation, automated processing, debugging, and future observability integration.

### Why Pydantic Schemas?

Pydantic models establish validated contracts between application layers and improve type safety, maintainability, testing, and failure visibility.

### Why Separate Attachment Processing?

Attachment validation and storage are independent security-sensitive responsibilities and should not be coupled to IMAP transport.

### Why a Provider-Independent LLM Boundary?

Application workflow logic depends on `LLMService`, allowing provider implementations to change without redesigning downstream ticket-processing logic.

### Why Version Prompts?

Prompt changes can alter classification accuracy, priority recommendations, confidence scores, and downstream workflow behavior.

Versioning provides reproducibility, regression comparison, evaluation traceability, and safer prompt evolution.

### Why Treat LLM Output as Untrusted Data?

LLMs may produce malformed JSON, missing fields, unexpected fields, or invalid values.

All output must pass extraction and strict schema validation before entering downstream business logic.

### Why Maintain a Labeled Evaluation Dataset?

Prompt quality cannot be demonstrated through a small number of manually selected examples.

A labeled evaluation dataset provides:

* Reproducibility.
* Classification measurement.
* Priority accuracy measurement.
* Edge-case coverage.
* Prompt regression detection.
* Prompt-version comparison.
* Evidence for engineering decisions.

### Why Measure Confidence Errors?

A confidence score is useful only if its behavior is understood.

The Hour 5 evaluation showed that incorrect predictions can receive high confidence. Confidence is therefore treated as advisory metadata rather than authoritative business logic.

### Why Keep Prompt Documentation Separate from Executable Prompts?

Executable prompts belong in version-controlled application modules.

Submission documentation belongs in `docs/prompts.md`.

This separation prevents README duplication while preserving:

* Exact runtime prompt traceability.
* Human-readable prompt documentation.
* Evaluation evidence.
* Prompt evolution history.

### Why Add a Normalization Layer After Schema Validation?

Schema validation and normalization solve different problems.

Schema validation verifies that AI output has the required structure and data types.

Normalization converts structurally valid but inconsistent values into deterministic application representations.

The processing boundary is therefore:

```text
Raw AI Output
      │
      ▼
JSON Extraction
      │
      ▼
Schema Validation
      │
      ▼
Deterministic Normalization
      │
      ▼
Business Rules
```

This prevents provider-specific formatting variation from leaking into priority assignment, routing, persistence, and analytics.

### Why Preserve Unknown Classification Values?

Silently mapping unsupported classifications to fallback values can hide prompt regressions and provider behavior changes.

SupportIQ AI preserves unknown values in normalized textual form so downstream services can explicitly reject, route, monitor, or handle them.

### Why Normalize Tags Before Persistence?

LLM-generated tags may differ in casing, whitespace, punctuation, or separator style.

Without normalization:

```text
Payment API
payment-api
PAYMENT_API
```

could be persisted as three separate tags.

Normalization produces a stable representation:

```text
payment-api
```

This improves filtering, analytics, persistence consistency, and duplicate prevention.

### Why Preserve First-Seen Tag Order?

Using an unordered set directly would make normalized output ordering nondeterministic.

SupportIQ AI uses a set for membership checks and a sequence for output construction.

This provides efficient duplicate detection while preserving deterministic output.

### Why Use Immutable Normalized Contracts?

Normalized analysis represents the trusted output of a deterministic processing boundary.

Immutability prevents downstream services from accidentally changing classifications, tags, confidence values, or normalization metadata.

Any later business decision should produce a new domain object rather than mutate normalized AI analysis.

### Why Separate AI-Recommended Priority from Final Priority?

The Hour 5 evaluation demonstrated that AI priority predictions are imperfect and confidence scores can be overconfident.

The normalized contract therefore stores:

```text
ai_recommended_priority
```

The final ticket priority will be produced by deterministic business rules.

This prevents the LLM recommendation from becoming an authoritative business decision.

### Why Add AI-Generated Reply Suggestions as a Bonus Feature?

The technical assignment explicitly identifies AI-generated support-agent reply suggestions as an optional bonus capability.

The feature extends the existing AI architecture without disrupting the core ticket-processing roadmap.

It demonstrates that the provider-independent LLM boundary can support multiple AI capabilities rather than only ticket analysis.

### Why Extend `LLMService` Instead of Calling Groq Directly?

Reply generation is an application AI capability, while Groq is infrastructure.

The dependency direction remains:

```text
ReplySuggestionService
        │
        ▼
LLMService
        │
        ▼
GroqLLMService
        │
        ▼
Groq API
```

This preserves provider independence and keeps the application workflow testable without network access.

### Why Use a Separate Versioned Reply-Suggestion Prompt?

Ticket analysis and reply generation solve different tasks.

Ticket analysis requires:

```text
Structured JSON Output
Classification Vocabularies
Confidence Scores
Strict Schema Validation
```

Reply generation requires:

```text
Natural-Language Output
Customer Context
Normalized Ticket Context
Tone Constraints
Groundedness Constraints
Concise Actionable Communication
```

Separating the prompts avoids mixing unrelated responsibilities and allows each capability to evolve independently.

### Why Does Reply Generation Use Plain Text Instead of JSON Response Format?

The output contract contains one customer-facing text value.

Forcing the provider to generate JSON adds unnecessary formatting complexity and creates additional failure modes.

The provider therefore generates plain text, which is wrapped in and validated through `ReplySuggestionResponse`.

### Why Use Normalized Ticket Analysis as Reply Context?

Raw model classifications may contain inconsistent formatting, aliases, duplicate tags, or unstable representations.

The reply-suggestion service consumes:

```text
NormalizedTicketAnalysis
```

so the second AI capability receives deterministic application context.

This preserves the processing boundary:

```text
Untrusted Ticket-Analysis Output
        │
        ▼
Schema Validation
        │
        ▼
Deterministic Normalization
        │
        ▼
Trusted Application Context
        │
        ▼
Reply Suggestion Generation
```

### Why Preserve the Original Customer Email?

Normalization summarizes and canonicalizes ticket-analysis output but does not replace the original customer message.

The reply-generation model receives the original email context to avoid losing customer-specific details that may not appear in the normalized analysis.

### Why Normalize Suggested Replies?

Provider output may contain inconsistent leading, trailing, or repeated whitespace.

Deterministic normalization provides stable output for:

* Testing.
* Future persistence.
* API responses.
* Dashboard rendering.
* Agent review.

### Why Enforce a Maximum Reply Length?

LLMs can generate unnecessarily long customer responses.

A maximum reply-length policy:

* Prevents unexpectedly large outputs.
* Keeps agent review manageable.
* Establishes a deterministic application boundary.
* Prevents provider behavior from controlling downstream storage or UI constraints.

### Why Not Automatically Send AI-Generated Replies?

AI-generated customer communication should remain subject to human review.

The current capability generates a suggestion only.

Future workflow:

```text
Generate
   │
   ▼
Review
   │
   ├── Approve
   ├── Edit
   └── Reject
   │
   ▼
Send
```

This preserves agent control and avoids coupling AI generation directly to external customer communication.

### Why Use Deterministic Business Rules After AI Priority Recommendation?

AI priority recommendations are useful but are not authoritative business decisions.

The baseline AI evaluation demonstrated imperfect priority accuracy and high-confidence classification errors.

SupportIQ AI therefore applies deterministic business rules after normalization.

This produces:

AI Recommendation
        │
        ▼
Schema Validation
        │
        ▼
Normalization
        │
        ▼
Deterministic Priority Rules
        │
        ▼
Final Priority Decision

The deterministic layer can escalate priority when operationally important phrases are detected while preventing lower-priority rules from downgrading a higher AI recommendation.

### Why Evaluate Priority Rules from Highest to Lowest?

A ticket may match multiple business rules.

Evaluating rules in descending priority order ensures the most operationally significant matching rule is selected deterministically.

### Why Prevent Deterministic Rules from Downgrading AI Priority?

The current business-rule layer is designed as a safety-oriented escalation mechanism.

If the AI already recommends a higher priority than the matched deterministic rule, reducing that priority could suppress a potentially important support request.

The service therefore selects the higher priority between the AI recommendation and the highest matched business rule.

### Why Keep Routing Configuration Separate from Routing Logic?

Category-to-team mappings are business configuration rather than routing-service implementation details.

Separating the mappings allows:

* Independent configuration testing.
* Dependency injection.
* Future database-backed routing rules.
* Future administrator-managed routing configuration.
* Cleaner routing-service responsibilities.

### Why Reject Unsupported Categories Instead of Using a Default Team?

Silently routing unsupported categories to a default team can hide prompt regressions, normalization errors, and configuration gaps.

SupportIQ AI raises an explicit `UnmappedCategoryError` so unsupported classifications remain observable and can later enter a manual-review or failure-handling workflow.

### Why Use a Repository Layer?

Application workflow logic should not depend directly on SQLAlchemy query construction or persistence exceptions.

The repository layer provides:

* A stable persistence abstraction.
* Reduced ORM coupling.
* Centralized query behavior.
* Application-specific exception translation.
* Easier unit testing.
* Explicit transaction ownership.

### Why Do Repositories Not Commit Transactions?

A complete ticket-processing workflow may persist a ticket, attachments, tags, audit events, and workflow-execution state as one atomic operation.

If individual repositories commit independently, partial workflow state can become permanent before the complete workflow succeeds.

SupportIQ AI therefore uses caller-owned transaction boundaries:

```text
Workflow Service
      │
      ▼
Begin Transaction
      │
      ├── TicketRepository
      ├── AttachmentRepository
      ├── AuditRepository
      └── WorkflowExecutionRepository
      │
      ▼
Complete Workflow Successfully?
      │
      ├── Yes → Commit
      └── No  → Roll Back
```      
---

## Development Roadmap

### Hour 1 — Completed

Project setup, architecture, PostgreSQL schema, and configuration foundation.

### Hour 2 — Completed

Secure IMAP ingestion, MIME parsing, attachment processing, integration testing, automated unit tests, and coverage measurement.

### Hour 3 — Completed

* SMTP transport service.
* Outbound email schemas.
* Real SMTP integration verification.
* Centralized application exception hierarchy.
* IMAP exception refactoring.
* Structured JSON logging infrastructure.
* Generic retry utility.
* Exponential backoff.
* Jitter support.
* Retry exhaustion handling.
* Ingestion result schemas.
* Email ingestion orchestration service.
* Per-message failure isolation.
* Batch processing metrics.
* Unit tests.
* Full regression testing.
* Application-wide coverage measurement.
* Real IMAP regression verification.

### Hour 4 — Completed

* Groq Python SDK integration.
* Provider-independent `LLMService` boundary.
* Groq provider adapter.
* Centralized Groq configuration.
* Versioned prompt architecture.
* Prompt registry.
* Structured ticket-analysis request contract.
* Structured ticket-analysis response contract.
* JSON-only prompt constraints.
* Prompt-injection mitigation instructions.
* Robust JSON object extraction.
* AI response parsing.
* Pydantic AI response validation.
* LLM-specific exception hierarchy.
* Retryable and non-retryable failure classification.
* Selective LLM retry integration.
* Timeout handling.
* Rate-limit handling.
* Connection failure handling.
* HTTP 4xx/5xx differentiation.
* Authentication failure handling.
* Invalid completion structure handling.
* Malformed JSON handling.
* Schema-invalid response handling.
* Typed failure preservation after retry exhaustion.
* Groq provider unit tests.
* JSON extractor unit tests.
* AI schema contract unit tests.
* Focused test verification.
* Full regression testing.

### Hour 5 — Completed

* Environment configuration cleanup.
* Groq SDK retry disabling.
* Real Groq smoke testing.
* Real structured ticket analysis verification.
* Labeled AI evaluation dataset.
* Evaluation dataset schemas.
* Standard ticket cases.
* Priority-sensitive cases.
* Ambiguous cases.
* Adversarial cases.
* Evaluation runner.
* Per-label accuracy metrics.
* Structured-output validity measurement.
* Case-type all-label accuracy.
* Confidence statistics.
* High-confidence error detection.
* Evaluation schema tests.
* Evaluation metric tests.
* Real-provider evaluation execution.
* Baseline `ticket-analysis-v1` quality measurement.
* Persistent AI evaluation report generation.
* AI prompt deliverable documentation.
* 68-test full regression verification.

### Hour 6 — Completed

* Dedicated ticket-analysis normalization boundary.
* Reusable text-normalization utilities.
* Unicode NFKC normalization.
* Whitespace normalization.
* Optional-text normalization.
* Canonical category normalization.
* Category alias mappings.
* Canonical AI-priority normalization.
* Priority alias mappings.
* Canonical sentiment normalization.
* Sentiment alias mappings.
* Canonical department normalization.
* Department alias mappings.
* Unknown-label preservation.
* Tag slug normalization.
* Empty-tag removal.
* Duplicate-tag removal.
* Stable first-seen tag ordering.
* Confidence precision normalization.
* Defensive confidence clamping support.
* Immutable normalized ticket-analysis schema.
* Immutable normalization metadata.
* Original classification preservation.
* Normalization change flags.
* Tag-removal metadata.
* AI-recommended priority separation.
* 37 focused normalization tests.
* 105-test full regression verification.

### Hour 6.5 — Bonus Feature Completed

* AI-generated support-agent reply suggestions.
* Versioned `reply-suggestion-v1` prompt.
* Central prompt-registry integration.
* Prompt documentation.
* Provider-independent reply-generation contract.
* `LLMService.suggest_reply(...)` capability.
* Groq reply-generation implementation.
* Structured reply-suggestion request schema.
* Structured reply-suggestion response schema.
* Strict reply contract validation.
* Plain-text provider completion handling.
* Reply-suggestion service boundary.
* Original email and normalized-analysis context composition.
* Suggested-reply whitespace normalization.
* Maximum reply-length policy.
* Input immutability verification.
* Provider failure propagation.
* Selective retry integration for reply generation.
* Timeout and rate-limit handling.
* Connection failure handling.
* Authentication failure handling.
* HTTP 4xx/5xx differentiation.
* Mocked provider tests.
* Reply schema tests.
* Reply service tests.
* Real Groq reply-suggestion pipeline verification.
* Original Groq ticket-analysis regression verification.
* 43 focused Hour 6.5 tests.
* 137-test full regression verification.

### Hour 7 — Completed

* Deterministic priority assignment engine.
* Centralized priority-rule configuration.
* Critical, High, Medium, and Low business-rule collections.
* Priority escalation rules.
* AI recommendation and business-rule reconciliation.
* Prevention of deterministic priority downgrading.
* Highest-priority rule selection.
* Priority-decision traceability.
* Priority configuration validation.
* Configurable category-to-team routing.
* Routing-decision traceability.
* Routing configuration injection.
* Routing configuration validation.
* Explicit unsupported-category rejection.
* Immutable downstream decision processing.
* Priority-service unit tests.
* Routing-service unit tests.
* 36 focused Hour 7 tests.
* 97% focused Hour 7 service coverage.
* 173-test full regression verification.
* Zero automated test failures and zero regressions.

### Hours 8–9

* SQLAlchemy database models.
* Database sessions.
* Repository layer.
* Transaction boundaries.
* Ticket creation workflow.
* Attachment persistence.
* Tag persistence.
* Audit-log persistence.
* Idempotency implementation.
* Integration tests.

### Hours 10–11

* FastAPI REST API.
* Ticket listing.
* Ticket details.
* Ticket editing.
* Team reassignment.
* Priority updates.
* Internal notes.
* Ticket status transitions.
* Audit trail APIs.
* Validation and exception handling.

### Hours 12–13

* Agent dashboard.
* Ticket search.
* Ticket filters.
* Ticket details.
* Ticket editing.
* Status management.
* Internal notes.
* Audit-history presentation.
* UX improvements.

### Hour 14

* Sample customer support email dataset.
* Classification evaluation harness.
* Priority assignment evaluation.
* Failure scenarios.
* Demonstration dataset.

### Hour 15

* Unit tests.
* Integration tests.
* Failure injection.
* Retry testing.
* Security checks.
* Coverage improvements.
* Regression testing.

### Hour 16

* Final README.
* Database schema documentation.
* Architecture diagram.
* Workflow documentation.
* Sequence diagram.
* Assumptions.
* Prompt documentation.
* Submission artifacts.

### Hour 17

* End-to-end demonstration preparation.
* Screen recording.
* Demo verification.

### Hour 18

* Final regression testing.
* Repository cleanup.
* Secret scanning.
* Deliverable verification.
* Submission package preparation.

---

## Planned Deliverables

The completed repository will contain:

1. Equivalent exported workflow documentation.
2. Complete source code.
3. Reproducible PostgreSQL database schema.
4. AI prompts used for ticket analysis and classification.
5. Sample customer support emails.
6. Environment configuration template.
7. Complete setup instructions.
8. Workflow explanation.
9. Documented assumptions.
10. Architecture documentation.
11. Automated tests.
12. Test coverage results.
13. AI evaluation dataset and report.
14. Demo instructions.
15. A 5–10 minute end-to-end screen recording.

---

## Assumptions

* Gmail is used as the support inbox for demonstration purposes.
* Gmail IMAP access uses a Google App Password.
* Gmail SMTP is used for outbound email delivery.
* PostgreSQL runs locally during development and demonstration.
* Groq is used as the current LLM inference provider.
* The application owns LLM retry behavior; Groq SDK retries are disabled.
* AI output is untrusted and must pass JSON extraction and Pydantic validation.
* The current evaluated prompt is `ticket-analysis-v1`.
* Evaluated prompt versions are treated as immutable.
* New prompt behavior should create a new prompt version and be evaluated against the labeled dataset.
* AI confidence scores are advisory and are not authoritative business decisions.
* Priority assignment uses a hybrid approach combining AI recommendations with deterministic business rules.
* Deterministic business rules may escalate priority but do not downgrade higher AI-recommended priorities.
* Priority rules are currently configured as application-level phrase collections.
* Team routing uses configurable category-to-team mappings.
* Unsupported routing categories are rejected explicitly rather than silently assigned to a fallback team.
* Priority and routing decisions are not yet persisted by the complete workflow; repository infrastructure now exists, while end-to-end persistence orchestration is deferred to Hour 9.
* Repository methods participate in caller-owned transactions and do not commit independently.
* Email Message-ID values are persisted through workflow-execution records as the foundation for idempotent processing.
* Support agents will remain able to review and override automated decisions.
* Incoming attachments are untrusted input.
* Runtime customer data, attachments, credentials, and logs must not be committed to Git.
* Email Message-ID values will form part of the idempotency strategy.
* Retrieved emails will not be marked as processed until the complete downstream success boundary is reached.
* Retry behavior is applied selectively to transient failures.
* The modular monolith architecture provides production-style separation of concerns without unnecessary distributed-system complexity.
* AI-generated reply suggestions are drafts for support-agent review.
* Generated replies are not sent automatically.
* `ParsedEmail` and `NormalizedTicketAnalysis` are not mutated during reply generation.
* The application owns provider retry behavior; Groq SDK automatic retries are disabled.
* Reply-suggestion generation uses plain-text completion semantics rather than JSON response formatting.

---

## License

This project was developed for a technical hiring assignment and is intended for evaluation and demonstration purposes.
