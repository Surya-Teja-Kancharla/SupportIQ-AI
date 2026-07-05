# SupportIQ AI

**SupportIQ AI** is an AI-powered customer support ticket automation system designed to ingest customer support emails, analyze unstructured support requests, classify issues, assign priorities, route tickets to appropriate teams, and maintain a complete support ticket lifecycle.

The project is being developed as part of the **Anthrasync AI Engineer Hiring Process – Round 3 Technical Assignment (Task 4: AI Customer Support Ticket Automation)**.

The system is designed with a production-oriented, modular architecture emphasizing:

* Maintainability
* Separation of concerns
* Secure configuration management
* Reliable email ingestion
* Structured data validation
* Resilience and error handling
* Testability
* Scalability
* Auditability
* Security and data privacy

> **Current Development Status:** Hours 1–2 completed — project foundation, PostgreSQL database schema, centralized configuration, secure IMAP email ingestion, MIME email parsing, attachment validation/storage, manual integration testing, and automated unit testing.

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
* [Email Ingestion Architecture](#email-ingestion-architecture)
* [Attachment Security](#attachment-security)
* [Configuration Management](#configuration-management)
* [Environment Variables](#environment-variables)
* [Installation and Setup](#installation-and-setup)
* [Running the IMAP Integration Test](#running-the-imap-integration-test)
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
2. Extract sender metadata, email content, timestamps, and attachments.
3. Analyze support requests using a Large Language Model.
4. Generate structured ticket information.
5. Validate and normalize AI-generated output.
6. Classify customer issues.
7. Determine ticket priority using AI recommendations and deterministic business rules.
8. Route tickets to appropriate support teams.
9. Persist tickets and related data in PostgreSQL.
10. Automatically acknowledge customer requests through email.
11. Allow support agents to review and modify AI-generated decisions.
12. Maintain a complete ticket lifecycle.
13. Record ticket changes in an audit trail.
14. Handle failures, retries, malformed AI responses, duplicate processing, and other workflow edge cases.

---

## Business Scenario

Customer support teams may receive hundreds of support requests through email.

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
IMAP Inbox Monitor
      │
      ▼
Email Metadata Extraction
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
Customer Acknowledgement Email
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

* Product name selected: **SupportIQ AI**
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
* Configurable mailbox folder selection.
* Detection of unread emails using IMAP `UNSEEN`.
* Non-destructive email retrieval using `BODY.PEEK[]`.
* MIME header decoding.
* Sender name extraction.
* Sender email extraction.
* Subject extraction.
* Message-ID extraction.
* Email timestamp parsing.
* Plain-text email body extraction.
* HTML email body fallback and conversion to text.
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

### Automated Testing Status

```text
20 tests passed
1 dependency deprecation warning
87% total coverage across tested ingestion modules
```

Module coverage:

```text
attachment_service.py    100%
email_parser.py           83%
```

---

## Features Implemented

### Centralized Configuration

Application configuration is loaded from environment variables using `pydantic-settings`.

All services consume application settings through a centralized configuration module instead of accessing environment variables independently.

### Secure IMAP Connection

SupportIQ AI connects to Gmail using:

```text
IMAP over SSL
```

Authentication is performed using a Google App Password rather than the user's normal Google account password.

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

This prevents the application from automatically marking messages as read during retrieval.

Emails will be explicitly marked as processed only after the complete processing workflow succeeds.

### MIME Header Decoding

Encoded email headers are decoded safely.

This supports:

* Plain ASCII headers
* UTF-8 encoded headers
* MIME encoded-word headers
* International characters

### Email Body Extraction

The email parser supports:

* Plain-text messages
* HTML messages
* Multipart messages
* Plain-text preference when both plain text and HTML versions exist
* HTML-to-text fallback using BeautifulSoup

### Attachment Processing

Attachments are:

1. Detected from multipart messages.
2. Decoded.
3. Validated.
4. Sanitized.
5. Checked against the configured extension allowlist.
6. Checked against the configured maximum size.
7. Assigned collision-resistant filenames.
8. Stored under the configured runtime upload directory.
9. Returned as structured attachment metadata.

### Structured Data Models

Pydantic schemas are used to represent:

* Parsed emails
* Parsed attachments

These models establish validated contracts between application layers.

### Automated Testing

The implemented email ingestion components include automated tests covering:

* Directory traversal prevention.
* Unsafe filename replacement.
* Preservation of valid filename characters.
* Successful attachment storage.
* Rejection of unsupported attachment extensions.
* Rejection of filenames without extensions.
* Rejection of oversized attachments.
* Unique stored filename generation.
* Missing MIME header handling.
* UTF-8 MIME header decoding.
* Plain-text MIME headers.
* Plain-text email extraction.
* Plain-text preference over HTML.
* HTML-to-text fallback.
* Unsupported body handling.
* Valid email date parsing.
* Missing email date fallback.
* Malformed email date fallback.
* Required email metadata extraction.
* Missing subject fallback.

---

## Technology Stack

### Backend

* Python 3.12
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### AI Provider

Planned:

* Groq API
* Llama-based instruction model

### Database

* PostgreSQL
* SQLAlchemy
* Alembic

### Email Integration

* Python `imaplib`
* Python `email`
* SMTP integration planned for acknowledgement emails

### Email Parsing

* Python standard library email package
* BeautifulSoup
* lxml

### Scheduling

Planned:

* APScheduler

### Testing

* pytest
* pytest-cov

### Logging

Planned:

* Loguru
* Structured application logging

---

## Project Architecture

SupportIQ AI follows a layered architecture.

```text
API Layer
    │
    ▼
Application / Orchestration Layer
    │
    ▼
Domain Services
    │
    ├── Email Ingestion
    ├── LLM Analysis
    ├── Validation
    ├── Priority Assignment
    ├── Routing
    ├── Ticket Management
    └── Acknowledgement
    │
    ▼
Repository / Persistence Layer
    │
    ▼
PostgreSQL
```

The application is structured to minimize coupling between infrastructure providers and business logic.

For example:

```text
Groq API
    │
    ▼
LLM Service
    │
    ▼
Ticket Analysis Workflow
```

The rest of the application will depend on an LLM service abstraction rather than directly coupling business logic to a specific AI provider.

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
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/
│   ├── database/
│   │   ├── schema.sql
│   ├── models/
│   ├── prompts/
│   ├── scheduler/
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── email_schema.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── attachment_service.py
│   │   ├── email_parser.py
│   │   └── imap_service.py
│   └── utils/
├── docs/
├── folder_structure.txt
├── logs/
├── main.py
├── requirements.txt
├── sample_data/
├── structure.py
├── tests/
│   ├── __init__.py
│   ├── manual_test_imap.py
│   ├── test_attachment_service.py
│   └── test_email_parser.py
├── uploads/
│   ├── attachments/
│   └── emails/
└── workflow/
```

Runtime-generated attachments, logs, secrets, virtual environments, Python cache files, and other local artifacts are excluded from version control.

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

* Internal database ID
* Unique ticket number
* Customer name
* Company
* Sender email
* Email subject
* Original email body
* AI-generated issue summary
* Detailed description
* Category
* Priority
* Sentiment
* Product or service
* Suggested department
* Assigned team
* Confidence score
* Ticket status
* Received timestamp
* Updated timestamp

### `attachments`

Stores attachment metadata associated with tickets.

Relationship:

```text
Ticket 1 ──────── * Attachments
```

### `tags`

Stores normalized ticket tags.

Relationship:

```text
Ticket 1 ──────── * Tags
```

Tags are stored as individual records rather than comma-separated values.

### `audit_logs`

Stores historical ticket actions and changes.

Examples:

* Ticket created
* Category changed
* Priority changed
* Assigned team changed
* Status changed
* Ticket resolved
* Ticket closed

Relationship:

```text
Ticket 1 ──────── * Audit Logs
```

### `internal_notes`

Stores support-agent comments that are not visible to customers.

Relationship:

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

Foreign keys use cascading deletion for dependent ticket records.

Database indexes are defined for frequently queried fields such as:

* Ticket status
* Priority
* Category
* Sender email
* Received timestamp

---

## Email Ingestion Architecture

The implemented ingestion pipeline currently operates as follows:

```text
Gmail Support Inbox
        │
        ▼
IMAP4_SSL Connection
        │
        ▼
Authenticate with App Password
        │
        ▼
Select Configured Mailbox
        │
        ▼
Search UNSEEN Messages
        │
        ▼
Fetch using BODY.PEEK[]
        │
        ▼
Parse Raw MIME Message
        │
        ├── Decode Headers
        ├── Parse Sender
        ├── Parse Subject
        ├── Parse Message-ID
        ├── Parse Timestamp
        ├── Extract Body
        └── Process Attachments
        │
        ▼
Return Validated ParsedEmail Object
```

Emails are intentionally not marked as read during retrieval.

The final workflow will explicitly mark messages as processed only after the configured processing boundary succeeds.

---

## Attachment Security

Incoming email attachments are treated as untrusted input.

The current attachment-processing service implements several defensive controls.

### Filename Sanitization

Directory path components are removed.

Unsafe characters are replaced.

Example:

```text
../../customer screenshots/error image.png

↓

error_image.png
```

### Extension Allowlist

Only configured attachment extensions are accepted.

Default:

```text
pdf,png,jpg,jpeg,txt,docx
```

Examples:

```text
error.png       → accepted
invoice.pdf     → accepted
logs.txt        → accepted

malware.exe     → rejected
script.bat      → rejected
payload.cmd     → rejected
```

### Maximum Attachment Size

Attachments exceeding the configured size limit are rejected.

Default:

```text
10 MB
```

### Unique Stored Filenames

Accepted attachments are assigned UUID-based stored filenames to reduce collision risk.

Example:

```text
Error.png

↓

fffef70466d74063a395b69497e0ab07_Error.png
```

### Runtime Storage Exclusion

The runtime attachment directory is excluded from Git to prevent customer data and test artifacts from being accidentally committed.

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

MODEL_NAME=llama-3.3-70b-versatile

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

LLM_TIMEOUT_SECONDS=30

LLM_MAX_RETRIES=3
```

Never commit `.env`.

The repository contains `.env_example` with placeholders for required configuration.

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Surya-Teja-Kancharla/SupportIQ-AI
cd SupportIQ-AI
```

### 2. Create a Virtual Environment

Windows:

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

### 6. Create the Database Tables

Execute the SQL schema included in the repository.

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

Then configure the required credentials and local database connection.

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

Send one or more test support emails to the configured support inbox.

Recommended test cases:

1. Plain-text email.
2. HTML-formatted email.
3. Email containing an allowed attachment.

Run:

```bash
python -m tests.manual_test_imap
```

Example output:

```text
Connecting to support inbox...
Connected successfully.

Unread emails found: 3

IMAP ID: b'1'
Message-ID: <support-test@example.com>
From: Test Customer
Email: customer@example.com
Subject: Unable to login
Received: 2026-07-05 12:15:51+05:30

Body:
Hello Support,

I cannot login after resetting my password.

Attachments: 0
```

Attachment example:

```text
Attachments: 1

Error.png
→
uploads/attachments/<uuid>_Error.png
```

The manual integration test does not mark retrieved emails as read.

---

## Running Automated Tests

Run all automated tests:

```bash
python -m pytest -v
```

Run only the attachment and email parser tests:

```bash
python -m pytest tests/test_attachment_service.py tests/test_email_parser.py -v
```

---

## Test Coverage

Generate terminal coverage output:

```bash
python -m pytest \
    --cov=app.services.attachment_service \
    --cov=app.services.email_parser \
    --cov-report=term-missing \
    -v
```

Current result:

```text
20 tests passed

attachment_service.py    100%
email_parser.py           83%

TOTAL                     87%
```

The current warning generated during the HTML parsing test originates from a third-party BeautifulSoup/lxml dependency and does not affect application functionality.

---

## Current Limitations

At the current development stage:

* Groq API integration is not implemented.
* AI ticket analysis is not implemented.
* AI output validation is not implemented.
* Category normalization is not implemented.
* Deterministic priority assignment is not implemented.
* Team routing is not implemented.
* SQLAlchemy persistence is not implemented.
* Ticket creation is not implemented.
* SMTP acknowledgement sending is not implemented.
* Inbox polling scheduler is not implemented.
* Duplicate email processing prevention is not implemented.
* Emails are not yet marked as processed.
* Structured application logging is not implemented.
* Retry handling is not implemented.
* Ticket REST APIs are not implemented.
* Manual agent review is not implemented.
* Ticket lifecycle transitions are not implemented.
* Audit-log persistence is not implemented.
* Support dashboard is not implemented.

These components are scheduled for subsequent development phases.

---

## Security Considerations

Security controls implemented or planned include:

### Implemented

* Secrets stored in `.env`.
* `.env` excluded from Git.
* Google App Password authentication.
* IMAP over SSL.
* Attachment extension allowlisting.
* Maximum attachment size enforcement.
* Filename sanitization.
* Directory traversal protection.
* UUID-based stored filenames.
* Pydantic data validation.
* Runtime uploads excluded from Git.
* Non-destructive email fetching.

### Planned

* Database transaction boundaries.
* Parameterized persistence through SQLAlchemy.
* LLM prompt input boundaries.
* AI output schema validation.
* Restricted ticket status transitions.
* Idempotent email processing.
* Duplicate ticket prevention.
* Configurable retry policies.
* Exponential backoff.
* Structured logging.
* Sensitive-data redaction from logs.
* Centralized exception handling.
* API input validation.
* API error response sanitization.
* Attachment MIME validation.
* Database connection pooling.

---

## Design Decisions

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

Groq is planned as the LLM inference provider because it provides fast inference and supports instruction-tuned models suitable for classification, summarization, sentiment analysis, priority recommendation, and structured ticket extraction.

The AI integration will be isolated behind an LLM service layer to reduce coupling between business logic and a specific provider.

### Why IMAP and SMTP?

IMAP and SMTP provide direct code-driven email integration without requiring paid workflow automation services.

IMAP is used for receiving customer support requests.

SMTP will be used for sending acknowledgement emails.

### Why `BODY.PEEK[]`?

SupportIQ AI retrieves messages without automatically marking them as read.

This prevents messages from being silently lost if processing fails after retrieval.

The final orchestration workflow will explicitly update the email processing state only after reaching a defined success boundary.

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

---

## Development Roadmap

### Hour 1 — Completed

Project setup, architecture, PostgreSQL schema, configuration foundation.

### Hour 2 — Completed

Secure IMAP ingestion, MIME parsing, attachment processing, integration testing, automated unit tests, and coverage measurement.

### Hour 3 — Next

* SMTP transport service.
* Acknowledgement email foundation.
* Custom application exception hierarchy.
* Structured logging configuration.
* Retry utility with exponential backoff.
* Ingestion result schemas.
* Duplicate-processing groundwork.
* Email ingestion orchestration service.
* Unit tests.

### Hours 4–5

* Groq API client.
* Provider-independent LLM service.
* Prompt architecture.
* Structured ticket analysis.
* JSON extraction.
* AI response parsing.
* Retry handling.
* Timeout handling.
* AI failure classification.
* Unit tests.

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

* Gmail is used as the support inbox for the demonstration.
* Gmail IMAP access is authenticated using a Google App Password.
* SMTP will be used for acknowledgement emails.
* PostgreSQL runs locally during development and demonstration.
* Groq will be used as the LLM inference provider.
* AI output will not be trusted directly and will pass through validation and normalization layers.
* Priority assignment will use a hybrid approach combining AI recommendations and deterministic business rules.
* Team routing will be configurable.
* Support agents will remain able to review and override AI-generated classifications.
* Incoming attachments are considered untrusted input.
* Runtime customer data, attachments, credentials, and logs must not be committed to Git.
* Email `Message-ID` values will be used as part of the idempotency strategy.
* The final application will explicitly define the processing boundary at which successfully processed emails are marked as seen.

---

## License

This project was developed for a technical hiring assignment and is intended for evaluation and demonstration purposes.
