# SupportIQ AI

**SupportIQ AI** is an AI-powered customer support ticket automation system designed to ingest customer support emails, analyze unstructured support requests, classify issues, assign priorities, route tickets to appropriate teams, persist ticket data, send customer acknowledgements, and maintain a complete support ticket lifecycle.

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

> **Current Development Status:** Hours 1–4 completed — project foundation, PostgreSQL schema, centralized configuration, secure IMAP email ingestion, MIME parsing, attachment validation/storage, email ingestion orchestration, SMTP transport, structured JSON logging, centralized application exceptions, reusable retry infrastructure, Groq API integration, provider-independent LLM service boundary, versioned prompt architecture, structured ticket-analysis contracts, robust JSON extraction, AI response validation, selective LLM retry integration, provider failure classification, and 58 passing automated tests.

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
* [SMTP Transport](#smtp-transport)
* [Exception Architecture](#exception-architecture)
* [Retry Infrastructure](#retry-infrastructure)
* [Structured Logging](#structured-logging)
* [Attachment Security](#attachment-security)
* [Configuration Management](#configuration-management)
* [Environment Variables](#environment-variables)
* [Installation and Setup](#installation-and-setup)
* [Running the IMAP Integration Test](#running-the-imap-integration-test)
* [Running the SMTP Integration Test](#running-the-smtp-integration-test)
* [Running Automated Tests](#running-automated-tests)
* [Test Coverage](#test-coverage)
* [Current Limitations](#current-limitations)
* [Security Considerations](#security-considerations)
* [Design Decisions](#design-decisions)
* [Development Roadmap](#development-roadmap)
* [Planned Deliverables](#planned-deliverables)
* [Assumptions](#assumptions)

---

## Project Objective

SupportIQ AI aims to automate the initial triage and management of customer support requests received through email.

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
11. Automatically acknowledge customer requests through email.
12. Allow support agents to review and modify AI-generated decisions.
13. Maintain a complete ticket lifecycle.
14. Record ticket changes in an audit trail.
15. Handle failures, retries, malformed AI responses, duplicate processing, and workflow edge cases.
16. Emit machine-readable operational logs for observability and debugging.

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

SupportIQ AI is intended to automate the initial support triage workflow while keeping human support agents in control of ticket review and resolution.

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
Category Normalization
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
SMTP Customer Acknowledgement
      │
      ▼
Manual Agent Review
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

### Automated Testing Status

```text
58 tests passed
1 third-party dependency deprecation warning
0 test failures
0 regressions
```

Focused Hour 4 AI infrastructure test suite:

```text
22 tests passed in 0.31s
```

Full application regression suite:

```text
58 tests passed in 0.62s
```

The warning originates from the BeautifulSoup/lxml HTML parser dependency and does not affect application functionality.

A controlled real Groq API smoke test remains recommended as integration verification before the AI evaluation and prompt-quality work performed during Hour 5.

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

Automatic ticket acknowledgement is intentionally deferred until ticket IDs, AI-generated summaries, database persistence, and workflow transaction boundaries are implemented.

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

The hierarchy prevents infrastructure-specific exceptions from leaking across application boundaries.

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

Logs must not contain credentials, API keys, database passwords, or Google App Passwords.

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

These models establish validated contracts between application layers.

### Provider-Independent LLM Service Boundary

The application defines an abstract `LLMService` contract for support-ticket analysis.

The concrete Groq integration is implemented by `GroqLLMService`.

This design prevents the ticket-processing workflow from becoming directly coupled to the Groq SDK.

### Versioned Prompt Architecture

SupportIQ AI stores ticket-analysis prompts as versioned application artifacts.

The current prompt:

```text
ticket-analysis-v1
```

defines:

* Classification vocabularies.
* Output schema requirements.
* JSON-only response requirements.
* Null semantics.
* Confidence-score guidance.
* Hallucination-reduction instructions.
* Prompt-injection mitigation instructions.
* Explicit untrusted-data boundaries.

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

### Selective LLM Retry Integration

The generic retry infrastructure is now integrated into the Groq provider adapter.

Retryable failures include:

* Request timeouts.
* Rate-limit failures.
* Connection failures.
* HTTP 5xx provider failures.

Non-retryable failures include:

* Authentication failures.
* HTTP 4xx request failures.
* Empty model responses.
* Malformed JSON.
* Schema-invalid model responses.

This avoids wasting API quota and processing time retrying permanent failures.

---

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
* Provider-independent `LLMService` abstraction
* Versioned prompt registry
* Pydantic structured-response validation

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
        ├── REST API
        └── Agent Dashboard
        │
        ▼
Application / Orchestration Layer
        │
        ├── Email Ingestion Service
        ├── Ticket Processing Workflow
        └── Ticket Lifecycle Services
        │
        ▼
Domain Services
        │
        ├── Email Parsing
        ├── Attachment Processing
        ├── LLM Analysis
        ├── Validation
        ├── Priority Assignment
        ├── Routing
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

For example:

```text
Groq API
    │
    ▼
Groq Client
    │
    ▼
LLM Service Boundary
    │
    ▼
Ticket Analysis Workflow
```

The application depends on an `LLMService` abstraction rather than coupling the complete workflow directly to Groq.

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
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── retry.py
│   ├── database/
│   │   └── schema.sql
│   ├── models/
│   │   └── __init__.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   └── ticket_analysis_v1.py
│   ├── scheduler/
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── email_schema.py
│   │   ├── ingestion_schema.py
│   │   ├── smtp_schema.py
│   │   └── ticket_analysis_schema.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── attachment_service.py
│   │   ├── email_ingestion_service.py
│   │   ├── email_parser.py
│   │   ├── groq_llm_service.py
│   │   ├── imap_service.py
│   │   ├── llm_service.py
│   │   └── smtp_service.py
│   └── utils/
│       ├── __init__.py
│       └── json_extractor.py
├── docs/
├── folder_structure.txt
├── logs/
├── main.py
├── pytest.ini
├── requirements.txt
├── sample_data/
├── structure.py
├── tests/
│   ├── __init__.py
│   ├── manual_test_imap.py
│   ├── manual_test_smtp.py
│   ├── test_attachment_service.py
│   ├── test_email_ingestion_service.py
│   ├── test_email_parser.py
│   ├── test_groq_llm_service.py
│   ├── test_json_extractor.py
│   ├── test_retry.py
│   ├── test_smtp_service.py
│   └── test_ticket_analysis_schema.py
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

Ticket-analysis prompts are explicitly versioned.

Current version:

```text
ticket-analysis-v1
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

## Running the IMAP Integration Test

Send test support emails to the configured support inbox.

Recommended test cases:

1. Plain-text email.
2. HTML-formatted email.
3. Email containing an allowed attachment.

Run:

```bash
python -m tests.manual_test_imap
```

The integration test verifies:

* Real IMAP SSL connectivity.
* Gmail App Password authentication.
* Mailbox selection.
* Unread message detection.
* Non-destructive retrieval.
* MIME parsing.
* HTML fallback.
* Attachment processing.

The manual test does not mark retrieved emails as read.

---

## Running the SMTP Integration Test

Configure a valid recipient address in:

```text
tests/manual_test_smtp.py
```

Run:

```bash
python -m tests.manual_test_smtp
```

The integration test verifies:

* Real SMTP connectivity.
* STARTTLS negotiation.
* Gmail App Password authentication.
* Message construction.
* Plain-text content.
* HTML alternative content.
* Message-ID generation.
* Real message delivery.

A successful SMTP transaction alone does not prove final mailbox delivery. For manual verification, confirm that the message is received by the destination mailbox.

---

## Running Automated Tests

Run the complete automated test suite:

```bash
python -m pytest -v
```

Current result:

```text
58 passed
1 warning
```

Run the focused Hour 4 AI infrastructure tests:

```bash
python -m pytest \
    tests/test_json_extractor.py \
    tests/test_ticket_analysis_schema.py \
    tests/test_groq_llm_service.py \
    -v
```

Current result:

```text
22 passed
```

The focused Hour 4 suite verifies:

* Clean JSON extraction.
* JSON extraction from markdown code fences.
* JSON extraction from surrounding response text.
* Braces inside JSON string values.
* JSON array rejection.
* Empty-response rejection.
* Missing-JSON rejection.
* Valid ticket-analysis schema parsing.
* Required-field enforcement.
* Confidence-score bounds.
* Unexpected-field rejection.
* Valid Groq response handling.
* Malformed JSON handling.
* Schema-invalid AI output handling.
* Timeout retry behavior.
* Rate-limit retry behavior.
* Authentication failure behavior.
* Connection failure retry behavior.
* Empty completion handling.
* Invalid completion structure handling.
* HTTP 5xx retry behavior.
* HTTP 4xx immediate-failure behavior.

All Hour 4 AI-infrastructure tests run against a mocked Groq client. No automated test in the current suite makes a real network call to Groq; the only real-provider verification to date is the manual smoke test recommended below.

---

## Test Coverage

Generate application-wide coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing -v
```

Coverage as of the Hour 3 measurement (pending an updated Hour 4 run):

```text
Name                                      Stmts   Miss  Cover
----------------------------------------------------------------
app/config/settings.py                       32      0   100%
app/core/constants.py                        36      0   100%
app/core/exceptions.py                       41      0   100%
app/core/logging.py                          49     28    43%
app/core/retry.py                            54      5    91%
app/schemas/email_schema.py                  16      0   100%
app/schemas/ingestion_schema.py              29      3    90%
app/schemas/smtp_schema.py                   12      0   100%
app/services/attachment_service.py           25      0   100%
app/services/email_ingestion_service.py      63     14    78%
app/services/email_parser.py                 78     13    83%
app/services/imap_service.py                 78     62    21%
app/services/smtp_service.py                 58      4    93%
----------------------------------------------------------------
TOTAL                                       571    129    77%
```

The lower coverage of `imap_service.py` is expected at the current stage because real IMAP integration is manually verified while transport-level unit tests using mocked IMAP connections have not yet been implemented.

A `--cov=app` run including the new Hour 4 modules (`llm_service.py`, `groq_llm_service.py`, `json_extractor.py`, `ticket_analysis_schema.py`, prompt registry and definitions) has not yet been captured in this document and should be regenerated before submission.

Coverage improvement is scheduled during the dedicated testing and hardening phase.

---

## Current Limitations

At the current development stage:

* Real Groq API smoke testing has not yet been completed.
* AI classification accuracy has not yet been evaluated against a labeled dataset.
* AI priority recommendation consistency has not yet been evaluated against expected labels.
* Prompt edge cases and ambiguous customer requests require evaluation.
* Prompt versions have not yet been benchmarked against each other.
* Category normalization is not implemented.
* Tag normalization is not implemented.
* Deterministic priority assignment is not implemented.
* Team routing is not implemented.
* SQLAlchemy persistence is not implemented.
* Repository layer is not implemented.
* Ticket creation is not implemented.
* Automatic acknowledgement sending is not implemented.
* Inbox polling scheduler is not implemented.
* Duplicate email processing prevention is not implemented.
* Emails are not yet marked as processed.
* Retry infrastructure is not yet integrated into IMAP, SMTP, database, or workflow orchestration boundaries.
* Ticket REST APIs are not implemented.
* Manual agent review is not implemented.
* Ticket lifecycle transitions are not implemented.
* Audit-log persistence is not implemented.
* Support dashboard is not implemented.
* Automated IMAP transport unit tests are not yet implemented.
* Sensitive-data redaction filters are not yet implemented.

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

### Hour 5 — Next

* Controlled real Groq API smoke test.
* Real support-ticket analysis verification.
* Labeled AI evaluation dataset.
* Classification accuracy measurement.
* Priority recommendation accuracy measurement.
* Sentiment accuracy measurement.
* Department recommendation accuracy measurement.
* Structured-output validity measurement.
* Prompt edge-case testing.
* Ambiguous-ticket testing.
* Prompt-injection resistance testing.
* Confidence-score behavior evaluation.
* Prompt quality refinement.
* Prompt version comparison if changes are required.
* AI evaluation report generation.
* AI prompt deliverable documentation.
* Final Hour 5 regression verification.

### Hours 6–7

* AI output validation.
* Category normalization.
* Tag normalization.
* Confidence handling.
* Deterministic priority assignment engine.
* Priority justification.
* Configurable routing engine.
* Unit tests.

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
13. Demo instructions.
14. A 5–10 minute end-to-end screen recording.

---

## Assumptions

* Gmail is used as the support inbox for demonstration purposes.
* Gmail IMAP access is authenticated using a Google App Password.
* Gmail SMTP is used for outbound email delivery.
* PostgreSQL runs locally during development and demonstration.
* Groq is used as the LLM inference provider.
* AI output will not be trusted directly and will pass through validation and normalization layers.
* Priority assignment will use a hybrid approach combining AI recommendations and deterministic business rules.
* Team routing will be configurable.
* Support agents will remain able to review and override AI-generated classifications.
* Incoming attachments are considered untrusted input.
* Runtime customer data, attachments, credentials, and logs must not be committed to Git.
* Email Message-ID values will form part of the idempotency strategy.
* Successfully retrieved emails will not be marked as processed until the complete downstream processing boundary succeeds.
* Retry behavior is applied selectively to transient failures rather than indiscriminately retrying all exceptions.
* The modular monolith architecture is intended to provide production-style separation of concerns without introducing unnecessary distributed-system complexity.
* Prompt version `ticket-analysis-v1` has not yet been validated against real Groq responses or a labeled evaluation set; its output quality is unverified as of Hour 4.

---

## License

This project was developed for a technical hiring assignment and is intended for evaluation and demonstration purposes.
