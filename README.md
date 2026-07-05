# SupportIQ AI

SupportIQ AI is an AI-powered customer support ticket automation system built for the Anthrasync AI Engineer Hiring Process – Round 3 Technical Assignment.

The system ingests customer support emails, analyzes unstructured requests with an LLM, validates and normalizes AI output, assigns deterministic priorities, routes tickets to support teams, persists workflow state, generates AI-assisted reply suggestions, sends customer acknowledgements, supports ticket lifecycle operations through REST APIs and an agent dashboard, records audit history, handles workflow failures and retries, and provides automated evaluation and test evidence.

The project is implemented as a modular monolith with explicit service, persistence, API, and infrastructure boundaries.

## Key Features

* Secure IMAP-based customer email ingestion.
* MIME parsing with plain-text and HTML support.
* Attachment validation, sanitization, size limits, and local storage.
* Provider-independent LLM service abstraction with Groq integration.
* Versioned prompts for ticket analysis and reply suggestions.
* Strict JSON extraction and Pydantic validation of AI output.
* Deterministic normalization of AI-generated ticket analysis.
* Hybrid priority assignment using AI recommendations and deterministic business rules.
* Configurable category-to-team routing.
* AI-generated reply suggestions for support-agent review.
* SQLAlchemy repository layer with caller-owned transaction boundaries.
* PostgreSQL persistence with Alembic-managed schema evolution.
* Message-ID-based idempotent workflow processing.
* Ticket, attachment, audit, internal-note, workflow-execution, and dead-letter persistence.
* End-to-end ticket-processing workflow orchestration.
* Customer acknowledgement delivery through SMTP.
* Ticket lifecycle management with validated status transitions.
* Internal notes and complete ticket audit history.
* FastAPI REST API for ticket operations.
* Agent dashboard for ticket listing, filtering, detail inspection, updates, notes, and audit history.
* Scheduled inbox polling with concurrency protection.
* Retry and failure-handling infrastructure with exponential backoff and dead-letter recovery.
* Structured JSON logging and operational monitoring endpoints.
* Deterministic classification evaluation.
* Real-provider AI evaluation support.
* Automated unit and integration tests.
* Architecture, workflow, database, security, scalability, evaluation, and demo documentation.

## System Workflow

```text
Customer Email
      |
      v
IMAP Ingestion
      |
      v
MIME Parsing and Attachment Validation
      |
      v
Message-ID Idempotency Check
      |
      v
LLM Ticket Analysis
      |
      v
JSON Extraction and Schema Validation
      |
      v
Deterministic Ticket Analysis Normalization
      |
      v
Priority Assignment
      |
      v
Category-to-Team Routing
      |
      v
AI Reply Suggestion Generation
      |
      v
Atomic Database Persistence
      |
      +--> Ticket
      +--> Attachments
      +--> Audit History
      +--> Workflow Execution
      |
      v
Customer Acknowledgement
      |
      v
Mark Email as Processed
      |
      v
Agent Dashboard and REST API
      |
      v
Lifecycle Updates, Internal Notes, and Audit History
```

Failures are handled through typed application exceptions, selective retries, workflow execution state, structured logging, and dead-letter recovery mechanisms.

## Architecture

SupportIQ AI uses a modular monolith architecture.

```text
External Systems
    |
    +-- Gmail IMAP
    +-- Gmail SMTP
    +-- Groq API
    |
    v
Application Interfaces
    |
    +-- FastAPI REST API
    +-- Agent Dashboard
    +-- Inbox Scheduler
    |
    v
Application and Workflow Services
    |
    +-- Email Ingestion
    +-- Ticket Processing Workflow
    +-- Reply Suggestions
    +-- Ticket Lifecycle
    +-- Failure Handling and Recovery
    |
    v
Domain Services
    |
    +-- Email Parsing
    +-- Attachment Processing
    +-- AI Analysis
    +-- AI Output Validation
    +-- Normalization
    +-- Priority Assignment
    +-- Routing
    |
    v
Repository Layer
    |
    v
SQLAlchemy
    |
    v
PostgreSQL
```

Cross-cutting infrastructure includes centralized configuration, typed exceptions, structured JSON logging, retry policies, monitoring, security controls, and automated testing.

Detailed architecture documentation is available in `docs/architecture.md`.

## Technology Stack

### Backend

* Python 3.12
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### Database

* PostgreSQL
* SQLAlchemy
* Alembic

### AI

* Groq API
* Groq Python SDK
* Llama 3.3 70B Versatile
* Provider-independent `LLMService`
* Versioned prompt registry
* Strict Pydantic AI contracts

### Email

* Gmail IMAP
* Gmail SMTP
* Python `imaplib`
* Python `smtplib`
* Python standard-library `email` package
* BeautifulSoup
* lxml

### Scheduling

* APScheduler

### Testing and Evaluation

* pytest
* pytest-cov
* `unittest.mock`
* Versioned AI evaluation dataset
* Deterministic classification evaluation dataset

## Project Structure

```text
SupportIQ-AI/
|
+-- app/
|   +-- api/
|   +-- config/
|   +-- core/
|   +-- database/
|   +-- evaluation/
|   +-- models/
|   +-- prompts/
|   +-- repositories/
|   +-- scheduler/
|   +-- schemas/
|   +-- services/
|   +-- static/
|   +-- templates/
|   +-- utils/
|
+-- alembic/
|   +-- versions/
|
+-- database/
|   +-- schema.sql
|
+-- docs/
|   +-- architecture.md
|   +-- workflow.md
|   +-- database_schema.md
|   +-- error_handling.md
|   +-- security.md
|   +-- scalability.md
|   +-- evaluation_results.md
|   +-- evaluation_results.json
|   +-- demo_script.md
|   +-- demo_environment.md
|   +-- prompts.md
|   +-- ai_evaluation_report.json
|
+-- sample_data/
|   +-- ai_evaluation_dataset.json
|   +-- classification_evaluation_dataset.json
|
+-- tests/
|
+-- workflow/
|   +-- workflow_definition.json
|
+-- .env_example
+-- alembic.ini
+-- main.py
+-- pytest.ini
+-- requirements.txt
+-- README.md
```

Runtime secrets, logs, uploaded customer data, virtual environments, caches, and local test artifacts are excluded from version control.

## Core Processing Pipeline

### 1. Email Ingestion

The application connects to the configured support mailbox through IMAP over SSL and retrieves unread emails non-destructively using `BODY.PEEK[]`.

Messages are parsed into validated application contracts containing sender information, subject, body, timestamps, Message-ID values, and attachment metadata.

Each message is processed independently so one malformed email does not terminate the entire ingestion batch.

### 2. Attachment Processing

Attachments are treated as untrusted input.

The application performs:

* filename sanitization;
* directory traversal prevention;
* extension allowlisting;
* maximum-size enforcement;
* collision-resistant stored filename generation;
* structured attachment metadata creation.

### 3. AI Ticket Analysis

The application exposes AI capabilities through a provider-independent `LLMService`.

The Groq adapter performs ticket analysis using a versioned prompt and returns structured output containing:

* customer information;
* issue summary;
* detailed description;
* category;
* AI-recommended priority;
* sentiment;
* product or service;
* suggested department;
* tags;
* confidence score.

Provider output is treated as untrusted data and must pass JSON extraction and strict Pydantic validation.

### 4. Ticket Analysis Normalization

Validated AI output passes through a deterministic normalization boundary.

Normalization includes:

* Unicode NFKC normalization;
* whitespace normalization;
* classification canonicalization;
* tag normalization and deduplication;
* confidence precision normalization;
* normalization metadata generation.

The normalized ticket-analysis contract is immutable.

### 5. Priority Assignment

Final priority is determined through a hybrid approach.

```text
AI Recommendation
        |
        v
Deterministic Business Rules
        |
        v
Highest Applicable Priority
        |
        v
Final Priority Decision
```

Business rules may escalate an AI recommendation but do not downgrade a higher AI-recommended priority.

### 6. Ticket Routing

Canonical ticket categories are mapped to configured support teams.

Unsupported categories are rejected explicitly instead of being silently routed to a fallback team.

### 7. AI Reply Suggestions

SupportIQ AI generates contextual reply drafts for support agents.

Reply generation uses the original customer email and normalized ticket-analysis context.

Generated replies are validated, normalized, length-limited, and stored for human review.

AI-generated replies are not automatically sent as final customer responses.

### 8. Persistence and Idempotency

SQLAlchemy repositories isolate workflow logic from persistence implementation.

The workflow coordinates persistence of:

* tickets;
* attachments;
* audit history;
* workflow execution state;
* internal notes;
* dead-letter records.

Repositories participate in caller-owned transactions and do not commit independently.

Message-ID-based workflow execution records prevent duplicate processing of the same customer email.

### 9. Customer Acknowledgement

After successful ticket persistence, the workflow sends a customer acknowledgement through SMTP.

The email is marked as processed only after the defined workflow success boundary is reached.

### 10. Ticket Lifecycle Management

Support agents can manage tickets through REST APIs and the dashboard.

Supported operations include:

* ticket listing and filtering;
* ticket detail inspection;
* category updates;
* priority updates;
* team reassignment;
* status transitions;
* internal notes;
* audit-history inspection.

Lifecycle changes are persisted and recorded in the audit trail.

### 11. Failure Handling and Recovery

SupportIQ AI includes explicit failure-handling infrastructure.

Capabilities include:

* application-specific exception hierarchy;
* transient-failure classification;
* exponential-backoff retry policies;
* retry exhaustion handling;
* workflow execution state tracking;
* failed workflow recording;
* dead-letter persistence;
* controlled recovery and replay;
* structured failure logs.

The current design provides application-level reliability mechanisms without claiming distributed exactly-once processing.

### 12. Scheduling and Concurrency Protection

The inbox scheduler periodically triggers ingestion.

Concurrency protection prevents overlapping polling executions within a single application process.

The current scheduler architecture is appropriate for a single active scheduler process. Distributed scheduling and cross-process locking remain future scalability improvements.

### 13. Observability

The application emits structured JSON logs containing event names and contextual metadata.

Logging destinations include:

```text
Console
logs/supportiq.log
logs/errors.log
```

Monitoring endpoints provide operational visibility into application health and workflow state.

Sensitive credentials must not be written to logs.

## Configuration

Application configuration is centralized in:

```text
app/config/settings.py
```

Create `.env` from `.env_example` and configure the required values.

Example configuration:

```env
GROQ_API_KEY=your_groq_api_key
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

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd SupportIQ-AI
```

### 2. Create the Virtual Environment

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

Verify dependency consistency:

```bash
python -m pip check
```

### 5. Configure Environment Variables

Copy `.env_example` to `.env` and configure the database, email, and AI-provider settings.

### 6. Create the PostgreSQL Database

```sql
CREATE DATABASE "supportiq-ai";
```

### 7. Apply Database Migrations

```bash
alembic upgrade head
```

Verify the migration state:

```bash
alembic current
alembic heads
```

### 8. Start the Application

```bash
python main.py
```

## API and Dashboard

After startup, use the configured local application address to access the dashboard and REST API.

The application provides ticket-management capabilities for:

* listing and filtering tickets;
* viewing ticket details;
* updating ticket fields;
* changing priority and team assignment;
* lifecycle status transitions;
* internal notes;
* audit-history inspection.

Refer to the implemented FastAPI routes and dashboard interface for the exact available endpoints and operations.

## Testing

Run the complete automated test suite:

```bash
python -m pytest -q
```

Latest verified result:

```text
452 passed
1 warning
```

The known warning is a third-party BeautifulSoup/lxml deprecation warning and does not currently cause test failures.

Generate application coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing -q
```

Latest verified total application coverage:

```text
89%
```

Automated tests cover application services, persistence, workflow orchestration, APIs, dashboard behavior, lifecycle operations, scheduler behavior, failure handling, recovery, evaluation logic, and integration boundaries.

## Evaluation

SupportIQ AI contains two complementary evaluation paths.

### Real-Provider AI Evaluation

```bash
python -m tests.manual_run_ai_evaluation
```

This evaluates the versioned ticket-analysis prompt against the labeled AI evaluation dataset.

Because it invokes the external AI provider, results can be affected by network availability, provider latency, rate limits, and model nondeterminism.

### Deterministic Classification Evaluation

```bash
python -m tests.manual_run_classification_evaluation
```

Latest verified classification evaluation:

```text
Samples: 50
Category Accuracy: 100.00%
Priority Accuracy: 94.00%
Routing Accuracy: 76.00%
```

Evaluation results are documented in:

```text
docs/evaluation_results.md
docs/evaluation_results.json
docs/ai_evaluation_report.json
```

Evaluation metrics are evidence for the current datasets and evaluation methodology. They should not be interpreted as production guarantees.

## Security

Implemented security controls include:

* environment-based secret management;
* exclusion of `.env` from version control;
* IMAP over SSL;
* SMTP STARTTLS;
* Google App Password authentication;
* attachment filename sanitization;
* directory traversal protection;
* extension allowlisting;
* attachment size limits;
* strict application input contracts;
* strict AI output validation;
* prompt-injection mitigation instructions;
* deterministic normalization before business processing;
* explicit unsupported-category rejection;
* application-owned retry policy;
* typed exception translation;
* caller-owned database transactions;
* Message-ID-based idempotency;
* customer-facing AI replies requiring human review;
* structured logging with credential-safety requirements.

Detailed security analysis is available in `docs/security.md`.

## Scalability

The current implementation is a modular monolith designed for local execution and technical evaluation.

Current scalability characteristics include:

* stateless REST request handling where practical;
* relational persistence through PostgreSQL;
* SQLAlchemy connection pooling;
* indexed ticket queries;
* configurable scheduler polling;
* idempotent Message-ID processing;
* bounded provider retries;
* modular service boundaries.

Known scaling constraints include:

* single-process scheduler concurrency protection;
* local filesystem attachment storage;
* synchronous workflow execution;
* external AI, IMAP, and SMTP provider limits;
* relational database contention under higher write concurrency;
* absence of a distributed queue.

The documented scaling path includes queue-backed asynchronous processing, distributed scheduler coordination, object storage, stronger distributed idempotency controls, database tuning, provider-aware rate limiting, and centralized observability.

Detailed scalability analysis is available in `docs/scalability.md`.

## Evaluation and Quality Evidence

Latest verified project evidence:

```text
Automated tests:
452 passed

Known warnings:
1 third-party BeautifulSoup/lxml deprecation warning

Total application coverage:
89%

Classification evaluation dataset:
50 samples

Category accuracy:
100.00%

Priority accuracy:
94.00%

Routing accuracy:
76.00%

Unsupported classification routing categories:
None
```

These values should only be changed after rerunning and verifying the corresponding commands.

## Documentation

Detailed project documentation is available under `docs/`.

| Document                     | Purpose                                                            |
| ---------------------------- | ------------------------------------------------------------------ |
| `docs/architecture.md`       | System architecture and component boundaries                       |
| `docs/workflow.md`           | End-to-end workflow and processing behavior                        |
| `docs/database_schema.md`    | Database entities, relationships, and schema design                |
| `docs/error_handling.md`     | Exception hierarchy, retry behavior, and failure recovery          |
| `docs/security.md`           | Security controls, threat boundaries, and limitations              |
| `docs/scalability.md`        | Current scalability characteristics and evolution path             |
| `docs/evaluation_results.md` | AI, classification, priority, routing, test, and coverage evidence |
| `docs/demo_script.md`        | Timed 7-minute demonstration script                                |
| `docs/demo_environment.md`   | Deterministic demo preparation and recovery procedure              |
| `docs/prompts.md`            | Prompt architecture, versions, contracts, and evaluation context   |

Additional deliverables:

```text
database/schema.sql
workflow/workflow_definition.json
app/prompts/ticket_analysis_prompt.txt
app/prompts/reply_suggestion_prompt.txt
sample_data/ai_evaluation_dataset.json
sample_data/classification_evaluation_dataset.json
```

## Known Limitations

* The current scheduler concurrency guard is process-local and does not provide distributed locking.
* Workflow execution is synchronous and does not use a distributed task queue.
* Attachments are stored on the local filesystem rather than object storage.
* External AI, IMAP, and SMTP integrations remain subject to provider availability and rate limits.
* AI confidence scores are advisory and are not calibrated probabilities.
* Real-provider AI evaluation is nondeterministic and depends on external provider availability.
* Classification evaluation uses a limited labeled dataset and does not establish production-level model quality.
* Routing accuracy on the current deterministic evaluation dataset is 76%, leaving measurable room for routing-rule and dataset improvement.
* AI-generated replies require human review and are not automatically sent as final responses.
* Sensitive-data redaction is not a complete data-loss-prevention system.
* The application has not been validated through production-scale load, soak, or chaos testing.
* Distributed exactly-once processing is not claimed.
* Queue-backed workflow execution, distributed scheduling, object storage, and centralized production observability remain future scalability improvements.

## Design Decisions

### Modular Monolith

A modular monolith provides explicit service boundaries, strong transactional coordination, straightforward local development, and lower operational complexity than premature microservices.

### Provider-Independent AI Boundary

Application services depend on `LLMService` instead of directly depending on the Groq SDK, reducing provider coupling and improving testability.

### AI Output as Untrusted Data

All AI output passes through extraction, schema validation, and deterministic normalization before entering business logic or persistence.

### Hybrid Priority Assignment

AI recommendations provide contextual classification, while deterministic business rules provide traceable operational safeguards.

### Human Review of AI Replies

AI-generated customer replies remain drafts for support-agent review rather than being automatically delivered as final responses.

### Caller-Owned Transactions

Repositories do not commit independently. Workflow services own transaction boundaries so related persistence operations can succeed or roll back together.

### Message-ID-Based Idempotency

Email Message-ID values provide a stable identity for duplicate-processing prevention and workflow execution tracking.

### Application-Owned Retry Policy

Provider SDK automatic retries are disabled where applicable so retry counts, backoff, logging, and failure classification remain controlled by the application.

## Assumptions

* Gmail is used for demonstration IMAP and SMTP integration.
* PostgreSQL is available during local execution and demonstration.
* Groq is the configured AI provider.
* AI output is untrusted and must pass validation and normalization.
* AI confidence scores are advisory.
* Priority assignment combines AI recommendations with deterministic business rules.
* Business rules may escalate priority but do not downgrade a higher AI recommendation.
* Unsupported routing categories fail explicitly.
* AI-generated replies require human review.
* Runtime customer data, attachments, credentials, and logs must not be committed to version control.
* External provider availability is not required for the deterministic primary demo path.
* The modular monolith is the implemented deployment architecture; distributed components described in scalability documentation are future evolution paths.

## Demo

The recommended demonstration is a deterministic 7-minute walkthrough covering:

1. application startup and dashboard;
2. email ingestion and AI analysis;
3. normalization, priority assignment, and routing;
4. persistence and customer acknowledgement;
5. ticket lifecycle operations and audit history;
6. failure handling and recovery;
7. evaluation and automated test evidence;
8. architecture summary.

Use:

```text
docs/demo_script.md
docs/demo_environment.md
```

to prepare and execute the demonstration.

## Project Status

SupportIQ AI is feature-complete for the technical-assignment scope through Hour 17.

Completed areas include:

* end-to-end customer support ticket automation;
* AI-assisted ticket analysis;
* deterministic normalization;
* priority assignment and routing;
* persistence and idempotency;
* acknowledgement delivery;
* lifecycle management;
* REST APIs;
* agent dashboard;
* scheduler execution;
* failure handling and recovery;
* structured logging and monitoring;
* AI-generated reply suggestions;
* automated testing and coverage measurement;
* AI and deterministic classification evaluation;
* architecture, workflow, database, security, scalability, evaluation, and demo documentation.

The remaining work is final regression verification, repository cleanup, secret scanning, deliverable auditing, and submission preparation.

## License

This project was developed for a technical hiring assignment and is intended for evaluation and demonstration purposes.
