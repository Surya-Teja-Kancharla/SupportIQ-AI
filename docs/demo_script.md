# SupportIQ-AI — 7-Minute Demo Script

## Demo Objective

Demonstrate SupportIQ-AI as an AI-assisted customer-support ticket automation system that processes incoming support emails, analyzes and normalizes ticket information, applies deterministic priority and routing rules, persists ticket and workflow data, supports acknowledgement and reply workflows, enforces ticket lifecycle transitions, records audit history, recovers failed workflows, exposes dashboard and monitoring capabilities, and provides reproducible evaluation evidence.

## Target Duration

```text
7 minutes
```

## Demo Timeline

| Time      | Section                                                 |
| --------- | ------------------------------------------------------- |
| 0:00–0:30 | Introduction and problem statement                      |
| 0:30–1:15 | Architecture and workflow overview                      |
| 1:15–2:30 | Email ingestion and AI-assisted ticket processing       |
| 2:30–3:30 | Dashboard, ticket persistence, priority, and routing    |
| 3:30–4:25 | Acknowledgement, reply suggestion, lifecycle, and audit |
| 4:25–5:15 | Failure handling, dead-letter recovery, and monitoring  |
| 5:15–6:15 | Testing and evaluation evidence                         |
| 6:15–7:00 | Scalability, security, and conclusion                   |

---

# 0:00–0:30 — Introduction and Problem Statement

## Screen

Show:

```text
README.md
```

or the project title and feature summary.

## Presenter Script

“SupportIQ-AI is an AI-assisted customer-support ticket automation system.

The system processes incoming customer emails, extracts structured ticket information using an LLM, normalizes the AI output, applies deterministic priority and routing rules, persists the ticket and workflow state, generates reply suggestions for human review, sends acknowledgements when appropriate, tracks ticket lifecycle changes, records audit history, and supports failure recovery.

The project is designed around reliability, traceability, deterministic business rules, and safe AI integration.”

## Key Point

Emphasize:

```text
AI assists the workflow.

Deterministic application logic controls operational decisions.

Persistent workflow state and audit records provide traceability.
```

---

# 0:30–1:15 — Architecture and Workflow Overview

## Screen

Open:

```text
docs\architecture.md
```

Show the Architecture Diagram.

Then open:

```text
docs\workflow.md
```

Show the Workflow Diagram.

## Presenter Script

“The system follows a layered architecture.

Incoming emails are obtained through the IMAP integration and parsed into validated email data.

The AI service analyzes the email using a versioned ticket-analysis prompt.

The raw AI output is validated and normalized before entering the business workflow.

PriorityService applies deterministic priority rules, while RoutingService maps the ticket category to the configured support team.

The ticket, attachments, audit records, and workflow execution state are persisted through the repository layer.

Additional services handle acknowledgements, reply suggestions, lifecycle operations, monitoring, dashboards, and failure recovery.”

## Show

Point briefly to:

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
└── services/
```

## Transition

“Now I’ll demonstrate how an incoming support email moves through this workflow.”

---

# 1:15–2:30 — Email Ingestion and AI-Assisted Ticket Processing

## Screen

Show:

```text
app\services\email_ingestion_service.py
```

Then briefly show:

```text
app\services\groq_llm_service.py

app\services\ticket_analysis_normalizer.py

app\services\priority_service.py

app\services\routing_service.py

app\services\workflow_service.py
```

Do not scroll through entire files.

Show only the primary classes and methods.

## Presenter Script

“The workflow begins when an incoming customer email is discovered.

The email parser extracts the sender, subject, body, attachments, and message metadata.

The email ingestion service coordinates the processing flow and prevents the external integration logic from being mixed directly into the domain services.

The ticket-analysis prompt instructs the AI provider to return structured JSON using the supported category, priority, sentiment, department, tag, and confidence fields.

Because LLM output cannot be trusted directly, the result is validated using Pydantic schemas and passed through the ticket-analysis normalizer.

The normalizer standardizes classification values, tags, confidence scores, and normalization metadata.

After normalization, PriorityService applies deterministic business rules to produce the final priority decision.

RoutingService maps the normalized category to the configured support team.

WorkflowService coordinates the downstream processing and persistence operations.”

## Show Prompt Versioning

Open:

```text
app\prompts\registry.py
```

## Presenter Script

“The prompts are versioned through a prompt registry.

This makes prompt behavior explicit and allows prompt versions to be tracked and changed without embedding large prompt definitions throughout the service layer.”

## Key Point

Emphasize:

```text
Raw AI output is never directly trusted as application state.
```

---

# 2:30–3:30 — Dashboard, Persistence, Priority, and Routing

## Screen

Start the application if it is not already running.

```powershell
python main.py
```

Open the dashboard in the browser.

Show:

```text
Ticket list

Ticket details

Status

Priority

Category

Assigned team

AI-generated summary

Suggested reply

Monitoring or dashboard information available in the current UI
```

## Presenter Script

“After processing, the ticket is persisted in the relational database.

The ticket record contains the original customer email information together with the normalized analysis and final business decisions.

Here we can see the ticket category, final priority, assigned team, status, confidence score, AI-generated summary, and suggested reply.

Priority is not accepted blindly from the AI output.

The PriorityService can apply deterministic rules to override or preserve the AI recommendation.

Routing is also deterministic and uses explicit category-to-team configuration.

This separation makes the final operational decisions easier to test and audit.”

## Show

Briefly open:

```text
app\config\priority_rules.py

app\config\routing_rules.py
```

## Presenter Script

“The supported priority and routing rules are configuration-driven rather than hidden inside the AI prompt.”

---

# 3:30–4:25 — Acknowledgement, Reply Suggestion, Lifecycle, and Audit

## Screen

Show a ticket detail view.

Then show:

```text
app\services\acknowledgement_service.py

app\services\reply_suggestion_service.py

app\services\ticket_lifecycle_service.py
```

## Presenter Script

“SupportIQ-AI also supports customer communication workflows.

AcknowledgementService determines whether an acknowledgement should be sent and prevents duplicate acknowledgement behavior.

ReplySuggestionService generates a professional customer-support reply draft.

The generated reply is intended for human review and is not treated as an automatically approved response.

Tickets also follow controlled lifecycle transitions.”

## Show Lifecycle

```text
OPEN
  |
  v
IN_PROGRESS
  |
  +----------------------+
  |                      |
  v                      v
WAITING_FOR_CUSTOMER  RESOLVED
  |                      |
  +------> IN_PROGRESS   v
  |                   CLOSED
  v
RESOLVED
```

## Presenter Script

“Invalid lifecycle transitions are rejected.

Successful status transitions create audit records containing the previous value, new value, action, and performer.

This gives the system traceability for important ticket operations.”

## Show

```text
app\models\ticket_audit_log.py
```

or the relevant audit history in the database or UI.

## Key Point

Emphasize:

```text
Lifecycle changes are validated and audited.
```

---

# 4:25–5:15 — Failure Handling, Dead-Letter Recovery, and Monitoring

## Screen

Show:

```text
app\services\failure_handling_service.py

app\services\failure_recovery_service.py

app\models\dead_letter_record.py

app\api\failure_recovery_routes.py

app\api\monitoring_routes.py
```

If failure records are available in the demo database, show one.

## Presenter Script

“External providers and background workflows can fail, so SupportIQ-AI does not silently discard failed operations.

Retryable operations use bounded retry behavior.

When workflow processing cannot complete successfully, failure information can be persisted with workflow execution and dead-letter records.

The failure recovery service supports manual retry operations.

A successful retry resolves the failed record, while another failure preserves the failure state and retry lineage for further investigation.

Monitoring routes expose operational workflow information so failures can be identified and inspected.”

## Key Point

Emphasize:

```text
Failures are persisted, observable, and recoverable.
```

---

# 5:15–6:15 — Testing and Evaluation Evidence

## Screen

Open a terminal.

Run:

```powershell
python -m pytest -q
```

Expected verified result:

```text
452 passed
1 warning
```

Then show the latest coverage result from:

```text
docs\evaluation_results.md
```

or, if time permits, run:

```powershell
python -m pytest --cov=app --cov-report=term-missing -q
```

Expected verified result:

```text
452 passed

89% total coverage
```

Run:

```powershell
python -m tests.manual_run_classification_evaluation
```

Expected verified output:

```text
Samples: 50

Category Accuracy: 100.00%

Priority Accuracy: 94.00%

Routing Accuracy: 76.00%
```

## Presenter Script

“The project currently contains 452 passing automated tests with 89 percent total code coverage.

The test suite covers services, repositories, API routes, schemas, retries, workflow execution, ticket lifecycle behavior, audit persistence, failure recovery, and integration workflows.

The deterministic classification evaluation uses a 50-sample dataset.

The latest verified results are 100 percent category accuracy, 94 percent priority accuracy, and 76 percent routing accuracy.

The routing result identifies the main current evaluation gap and provides measurable evidence for future routing-policy improvements.

The project also includes a live AI evaluation runner, but live-provider metrics are kept separate because they depend on credentials, network connectivity, provider availability, rate limits, and nondeterministic model responses.”

## Key Point

Emphasize:

```text
452 passing tests

89% coverage

50 evaluation samples

100% category accuracy

94% priority accuracy

76% routing accuracy
```

---

# 6:15–7:00 — Scalability, Security, and Conclusion

## Screen

Open:

```text
docs\security.md

docs\scalability.md
```

Then return to:

```text
README.md
```

## Presenter Script

“Security controls include environment-based credential configuration, input validation, structured schemas, prompt-injection resistance instructions, safe attachment handling considerations, restricted logging of sensitive information, and human review of AI-generated reply suggestions.

The current architecture is suitable for a modular single-application deployment and provides a path toward horizontal scaling.

Future scaling can separate stateless API instances, scheduler execution, background workers, distributed queues, object storage, provider-specific concurrency controls, and centralized observability.

The main current scalability dependencies are the relational database, external AI-provider latency, email-provider limits, background processing throughput, and scheduler coordination.

In summary, SupportIQ-AI demonstrates a complete AI-assisted customer-support workflow with email ingestion, structured AI analysis, deterministic business decisions, persistence, acknowledgement and reply support, lifecycle validation, auditing, failure recovery, monitoring, dashboards, evaluation tooling, and comprehensive automated testing.”

## Final Statement

“SupportIQ-AI demonstrates how generative AI can be integrated into a customer-support workflow without making the AI model the sole authority for operational decisions.

The system combines AI-assisted analysis with deterministic business rules, persistent workflow state, auditability, failure recovery, and measurable evaluation evidence.”

---

# Pre-Demo Preparation

Before starting the presentation:

```text
1. Activate the Python virtual environment.

2. Verify environment variables are configured.

3. Verify the database is reachable.

4. Apply all Alembic migrations.

5. Verify sample data files.

6. Run the complete automated test suite.

7. Run the deterministic classification evaluation.

8. Start the application.

9. Open the dashboard.

10. Confirm at least one useful ticket exists in the demo database.

11. Confirm ticket detail information is visible.

12. Confirm lifecycle and audit data are available.

13. Confirm failure-recovery data is available if it will be demonstrated.

14. Open architecture.md in advance.

15. Open workflow.md in advance.

16. Open evaluation_results.md in advance.

17. Close terminals or editor tabs containing credentials.

18. Disable unnecessary notifications.

19. Increase terminal and editor font size for visibility.

20. Keep backup screenshots or captured terminal output available.
```

---

# Pre-Demo Commands

Activate the virtual environment if necessary:

```powershell
venv\Scripts\activate
```

Verify migration state:

```powershell
alembic current
```

Apply migrations:

```powershell
alembic upgrade head
```

Verify migration state again:

```powershell
alembic current
```

Validate evaluation datasets:

```powershell
python -m json.tool sample_data\ai_evaluation_dataset.json > nul

python -m json.tool sample_data\classification_evaluation_dataset.json > nul
```

Run the complete test suite:

```powershell
python -m pytest -q
```

Run deterministic classification evaluation:

```powershell
python -m tests.manual_run_classification_evaluation
```

Start the application:

```powershell
python main.py
```

---

# Demo Recovery Plan

## Application Does Not Start

Check:

```powershell
python --version

pip check

alembic current
```

Review:

```text
logs\errors.log

logs\supportiq.log
```

If necessary:

```powershell
alembic upgrade head
python main.py
```

---

## Database Is Unavailable

Do not spend presentation time debugging the database.

Show:

```text
docs\database_schema.md

docs\architecture.md

docs\workflow.md

previous verified test output
```

Explain the persistence architecture and continue with evaluation evidence.

---

## AI Provider Is Unavailable

Do not depend on a live AI-provider request during the main demonstration.

Use:

```text
Deterministic integration tests

Stored demo tickets

Classification evaluation

Prompt definitions

AI evaluation tooling
```

Explain that automated tests mock provider behavior to preserve deterministic execution.

---

## Email Provider Is Unavailable

Do not spend presentation time debugging IMAP or SMTP credentials.

Show:

```text
email ingestion service

email parser

SMTP service

acknowledgement workflow tests

email workflow integration tests
```

Continue with a stored demo ticket.

---

## Dashboard Is Unavailable

Show:

```text
API routes

service layer

database records

automated test results

evaluation results

architecture documentation
```

Continue the demonstration from the terminal and editor.

---

## Classification Evaluation Produces Unexpected Results

Use the latest verified results recorded in:

```text
docs\evaluation_results.md
```

Do not modify the dataset or application logic during the presentation.

---

# Files to Keep Open Before the Demo

Keep these files open in editor tabs:

```text
README.md

docs\architecture.md

docs\workflow.md

docs\evaluation_results.md

docs\security.md

docs\scalability.md

app\services\email_ingestion_service.py

app\services\ticket_analysis_normalizer.py

app\services\priority_service.py

app\services\routing_service.py

app\services\ticket_lifecycle_service.py

app\services\failure_recovery_service.py

app\prompts\registry.py
```

Keep these terminals ready:

```text
Terminal 1:
Application server

Terminal 2:
Automated tests

Terminal 3:
Classification evaluation and database verification
```

---

# Demo Rules

During the demonstration:

```text
Do not expose .env contents.

Do not expose API keys.

Do not expose email passwords.

Do not depend on a live AI-provider request.

Do not depend on live IMAP or SMTP availability.

Do not edit application code during the presentation.

Do not run migrations for the first time during the presentation.

Do not run destructive database commands.

Do not spend time scrolling through entire source files.

Do not claim live AI evaluation results that were not successfully captured.

Do not claim that future scalability components are already implemented.

Do not claim production readiness solely from test coverage.

Keep the demonstration focused on the end-to-end workflow and verified evidence.
```

---

# Final Demo Evidence

The demonstration should leave the audience with the following verified evidence:

```text
Complete modular customer-support automation backend

Email ingestion and parsing workflow

Versioned AI prompts

Structured AI ticket analysis

Pydantic validation and normalization

Deterministic priority decisions

Configuration-driven routing

Ticket and attachment persistence

Reply suggestions for human review

Acknowledgement workflow

Controlled ticket lifecycle transitions

Audit history

Workflow execution tracking

Retry handling

Dead-letter failure recovery

Dashboard and monitoring routes

452 passing automated tests

89% total code coverage

50-sample deterministic evaluation dataset

100% category accuracy

94% priority accuracy

76% routing accuracy

Documented security characteristics

Documented scalability path

Reproducible evaluation commands

Defined demo recovery procedures
```
