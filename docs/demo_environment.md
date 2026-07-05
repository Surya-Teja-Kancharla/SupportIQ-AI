# SupportIQ-AI Demo Environment Preparation

## Purpose

This document defines the deterministic preparation, verification, startup, validation, and recovery procedure for demonstrating SupportIQ-AI.

The objective is to minimize live-demo risk by verifying the Python environment, configuration, database schema, migrations, evaluation datasets, automated tests, application startup, demo data, credential safety, and recovery resources before the presentation begins.

The primary demo path should not depend on live IMAP, SMTP, or AI-provider availability.

---

# 1. Demo Environment Requirements

The demo machine should provide:

```text
Windows development environment

Python 3.12-compatible runtime

Activated project virtual environment

Installed project dependencies

Configured environment variables

Reachable relational database

Current Alembic migrations

Valid evaluation datasets

Passing automated test suite

Prepared demo ticket data

Accessible dashboard

Available application logs
```

The presentation should be performed from the project root:

```text
SupportIQ-AI\
```

---

# 2. Pre-Demo Checklist

Complete this checklist before every demonstration.

```text
[ ] Project repository is available locally.

[ ] Correct Git branch is checked out.

[ ] Working tree status has been reviewed.

[ ] Python virtual environment is activated.

[ ] Python version is verified.

[ ] Required dependencies are installed.

[ ] Dependency consistency is verified.

[ ] .env exists locally.

[ ] .env is excluded from Git tracking.

[ ] Required environment variables are configured.

[ ] No credentials are visible in terminals or editor tabs.

[ ] Database server is reachable.

[ ] Alembic migration state is verified.

[ ] All pending migrations are applied.

[ ] Evaluation datasets contain valid JSON.

[ ] Classification dataset contains 50 samples.

[ ] Classification dataset contains no unsupported routing categories.

[ ] Complete automated test suite passes.

[ ] Coverage result has been verified.

[ ] Classification evaluation runs successfully.

[ ] Latest evaluation results are available.

[ ] Application starts successfully.

[ ] Dashboard is reachable.

[ ] At least one useful ticket exists for demonstration.

[ ] Ticket detail data is available.

[ ] Priority and routing information is available.

[ ] Suggested reply information is available.

[ ] Lifecycle and audit information is available.

[ ] Failure recovery evidence is available if demonstrated.

[ ] Architecture documentation is open.

[ ] Workflow documentation is open.

[ ] Evaluation documentation is open.

[ ] Backup verified terminal output or screenshots are available.

[ ] Desktop notifications are disabled.

[ ] Terminal and editor fonts are readable for the audience.
```

---

# 3. Verify Repository State

From the project root, run:

```powershell
git branch --show-current
git status --short
git log -5 --oneline
```

Confirm that:

```text
The intended branch is active.

No unexpected source-code modifications exist.

The latest Hour 17 documentation and deliverables are present.
```

Do not run destructive Git cleanup commands immediately before the demonstration.

If documentation changes are intentionally uncommitted, verify them individually before proceeding.

---

# 4. Activate the Virtual Environment

Run:

```powershell
venv\Scripts\activate
```

Verify:

```powershell
where python
python --version
python -m pip --version
```

The Python executable should resolve to the project virtual environment.

Expected project runtime:

```text
Python 3.12-compatible environment
```

---

# 5. Verify Installed Dependencies

Run:

```powershell
python -m pip check
```

Expected result:

```text
No broken requirements found.
```

Optionally inspect installed dependencies:

```powershell
python -m pip list
```

Do not upgrade dependencies immediately before the demonstration unless required to repair a verified environment problem.

Dependency upgrades can introduce untested behavior.

---

# 6. Verify Configuration

Confirm that the local environment file exists:

```powershell
if exist .env (echo .env exists) else (echo ERROR: .env missing)
```

Confirm that the environment example exists:

```powershell
if exist .env_example (echo .env_example exists) else (echo WARNING: .env_example missing)
```

Inspect application configuration definitions without printing secrets:

```powershell
type app\config\settings.py
```

Do not run:

```text
type .env
```

Do not display environment variables containing credentials.

Required configuration depends on the workflow being demonstrated and can include:

```text
Database connection configuration

AI-provider credentials

IMAP configuration

SMTP configuration

Application settings
```

The main deterministic demo path should continue to work without invoking live external providers.

---

# 7. Credential Safety Verification

Verify that `.env` is ignored:

```powershell
git check-ignore .env
```

Expected output:

```text
.env
```

Verify that `.env` is not tracked:

```powershell
git ls-files .env
```

Expected output:

```text
No output
```

Review repository changes:

```powershell
git status --short
```

Search tracked project files for common credential patterns:

```powershell
git grep -n -I -E "api[_-]?key|secret[_-]?key|password|access[_-]?token|private[_-]?key"
```

Review every result manually.

Matches in configuration variable names, documentation, schemas, tests, or placeholder values are not automatically credential leaks.

Do not print real credential values during verification.

Before presenting:

```text
Close .env editor tabs.

Clear terminals containing credential values.

Close database tools displaying connection passwords.

Close browser pages displaying provider API keys.

Disable command-history suggestions if they expose secrets.

Verify screenshots do not contain credentials.
```

---

# 8. Verify Database Connectivity

Use the application database configuration to verify connectivity without printing the database URL.

Run:

```powershell
python -c "from sqlalchemy import text; from app.database.session import SessionLocal; s=SessionLocal(); print('Database connection:', s.execute(text('SELECT 1')).scalar()); s.close()"
```

Expected output:

```text
Database connection: 1
```

If the command fails, do not proceed to migrations until database connectivity is restored.

---

# 9. Verify Alembic Migration State

Check the current migration:

```powershell
alembic current
```

Check available migration heads:

```powershell
alembic heads
```

Inspect migration history:

```powershell
alembic history
```

Apply all pending migrations:

```powershell
alembic upgrade head
```

Verify again:

```powershell
alembic current
alembic heads
```

The current revision should match the expected migration head.

Do not perform the first migration upgrade during the live presentation.

---

# 10. Verify Required Database Tables

Run:

```powershell
python -c "from sqlalchemy import inspect; from app.database.session import engine; print(*sorted(inspect(engine).get_table_names()), sep='\n')"
```

Verify the presence of the project tables required by the current schema, including:

```text
tickets

ticket_attachments

ticket_audit_logs

internal_notes

workflow_executions

dead_letter_records
```

The exact database table set should remain consistent with the SQLAlchemy models and Alembic migration history.

---

# 11. Validate Evaluation Dataset JSON

Run:

```powershell
python -m json.tool sample_data\ai_evaluation_dataset.json > nul

python -m json.tool sample_data\classification_evaluation_dataset.json > nul
```

Successful commands should produce no terminal output.

---

# 12. Verify Evaluation Dataset Metadata and Sample Counts

Run:

```powershell
python -c "import json; files=['sample_data/ai_evaluation_dataset.json','sample_data/classification_evaluation_dataset.json']; exec(\"for f in files:\n d=json.load(open(f, encoding='utf-8'))\n print(f, 'samples=', len(d['samples']) if isinstance(d, dict) and 'samples' in d else len(d))\")"
```

Verify the classification dataset independently:

```powershell
python -c "import json; d=json.load(open('sample_data/classification_evaluation_dataset.json', encoding='utf-8')); print('Dataset:', d.get('dataset_name')); print('Version:', d.get('version')); print('Samples:', len(d['samples']))"
```

Expected verified classification sample count:

```text
Samples: 50
```

---

# 13. Verify Classification Dataset Required Fields

Run:

```powershell
python -c "import json; p='sample_data/classification_evaluation_dataset.json'; d=json.load(open(p, encoding='utf-8')); required={'id','subject','body','predicted_category','predicted_priority','confidence_score','expected_category','expected_priority','expected_route'}; bad=[(i, sorted(required-set(x))) for i,x in enumerate(d['samples']) if required-set(x)]; print('Samples:', len(d['samples'])); print('Invalid samples:', bad)"
```

Expected result:

```text
Samples: 50

Invalid samples: []
```

---

# 14. Verify Duplicate Dataset IDs

Run:

```powershell
python -c "import json, collections; files=['sample_data/ai_evaluation_dataset.json','sample_data/classification_evaluation_dataset.json']; exec(\"for f in files:\n d=json.load(open(f, encoding='utf-8'))\n samples=d['samples'] if isinstance(d, dict) and 'samples' in d else d\n duplicates=[k for k,v in collections.Counter(x['id'] for x in samples).items() if v>1]\n print(f, 'duplicate_ids=', duplicates)\")"
```

Expected result:

```text
duplicate_ids= []
```

for both datasets.

---

# 15. Verify Classification Routing Coverage

Run:

```powershell
python -c "import json; from app.config.routing_rules import CATEGORY_TEAM_ROUTES; d=json.load(open('sample_data/classification_evaluation_dataset.json', encoding='utf-8')); cats=set(x['predicted_category'] for x in d['samples']); print('Configured:', sorted(CATEGORY_TEAM_ROUTES)); print('Dataset:', sorted(cats)); print('Unsupported:', sorted(cats-set(CATEGORY_TEAM_ROUTES)))"
```

Expected result:

```text
Unsupported: []
```

If unsupported categories exist, do not modify routing configuration during the presentation.

Investigate and resolve the mismatch before the demo.

---

# 16. Run the Complete Automated Test Suite

Run:

```powershell
python -m pytest -q
```

Latest verified result:

```text
452 passed

1 warning
```

The known warning is:

```text
BeautifulSoup/lxml DeprecationWarning related to strip_cdata.
```

The warning does not currently cause a test failure.

Do not proceed with the primary demo environment if tests unexpectedly fail.

Investigate the failure or use previously verified backup evidence.

---

# 17. Verify Test Coverage

Run:

```powershell
python -m pytest --cov=app --cov-report=term-missing -q
```

Latest verified result:

```text
452 passed

89% total coverage
```

Coverage is evidence of exercised implementation paths.

Coverage percentage alone does not establish production readiness.

---

# 18. Run Deterministic Classification Evaluation

Run:

```powershell
python -m tests.manual_run_classification_evaluation
```

Latest verified result:

```text
Samples: 50

Category Accuracy: 100.00%

Priority Accuracy: 94.00%

Routing Accuracy: 76.00%
```

The evaluation writes results to:

```text
docs\evaluation_results.json
```

Verify the output file:

```powershell
python -m json.tool docs\evaluation_results.json > nul
```

Do not modify the evaluation dataset immediately before or during the presentation.

---

# 19. Live AI Evaluation Policy

The live AI evaluation command is:

```powershell
python -m tests.manual_run_ai_evaluation
```

This command depends on:

```text
Valid AI-provider credentials

Network connectivity

Provider availability

Provider rate limits

Provider latency

Nondeterministic model responses
```

The live AI evaluation should not be required for the primary 7-minute demonstration.

If verified live results are available before the presentation, record them in the evaluation documentation.

If the provider is unavailable, continue using deterministic tests and evaluation evidence.

---

# 20. Verify Workflow Definition

Validate:

```powershell
python -m json.tool workflow\workflow_definition.json > nul
```

Inspect the deliverable:

```powershell
type workflow\workflow_definition.json
```

Confirm that the workflow definition reflects the implemented processing stages and failure paths.

---

# 21. Verify Prompt Deliverables

Confirm the prompt files exist:

```powershell
dir app\prompts\*.txt
```

Inspect:

```powershell
type app\prompts\ticket_analysis_prompt.txt

type app\prompts\reply_suggestion_prompt.txt
```

Verify that the deliverable prompt files are synchronized with the implemented versioned prompt definitions.

The source-of-truth runtime prompts are versioned through:

```text
app\prompts\ticket_analysis_v1.py

app\prompts\reply_suggestion_v1.py

app\prompts\registry.py
```

Do not modify prompts immediately before the presentation without rerunning relevant tests and evaluations.

---

# 22. Verify Database Schema Deliverable

Confirm:

```powershell
if exist database\schema.sql (echo database schema deliverable exists) else (echo ERROR: database\schema.sql missing)
```

Validate that the deliverable exists separately from:

```text
app\database\schema.sql
```

Compare the two files:

```powershell
fc /N app\database\schema.sql database\schema.sql
```

If the files intentionally serve different purposes, document the difference.

Otherwise, keep the final deliverable synchronized with the current implemented schema.

---

# 23. Verify Documentation Deliverables

Run:

```powershell
dir docs
```

Verify:

```text
architecture.md

workflow.md

database_schema.md

error_handling.md

security.md

scalability.md

evaluation_results.md

demo_script.md

demo_environment.md
```

Also verify:

```powershell
if exist workflow\workflow_definition.json (echo workflow definition exists) else (echo ERROR: workflow definition missing)

if exist database\schema.sql (echo database schema exists) else (echo ERROR: database schema missing)

if exist app\prompts\ticket_analysis_prompt.txt (echo ticket analysis prompt exists) else (echo ERROR: ticket analysis prompt missing)

if exist app\prompts\reply_suggestion_prompt.txt (echo reply suggestion prompt exists) else (echo ERROR: reply suggestion prompt missing)
```

---

# 24. Prepare Deterministic Demo Data

Before the presentation, verify that at least one suitable ticket exists.

The demo ticket should contain:

```text
Sender email

Subject

Email body

Issue summary

Detailed description

Category

Priority

Sentiment

Product or service

Suggested department

Assigned team

Confidence score

Suggested reply

Ticket status

Received timestamp
```

Prefer a stored ticket that also has:

```text
Audit history

Lifecycle changes

Acknowledgement evidence

Workflow execution history
```

If failure recovery is demonstrated, prepare a separate failure record or verified recovery example.

Do not depend on a new live customer email arriving during the presentation.

Do not depend on the AI provider generating a successful response during the presentation.

---

# 25. Verify Ticket Data Before Demo

Run:

```powershell
python -c "from app.database.session import SessionLocal; from app.models.ticket import Ticket; s=SessionLocal(); rows=s.query(Ticket).order_by(Ticket.id.desc()).limit(5).all(); print('Ticket count shown:', len(rows)); [print(x.id, x.ticket_number, x.category, x.priority, x.status) for x in rows]; s.close()"
```

Confirm that at least one useful ticket is available.

If no tickets exist, prepare deterministic demo data before the presentation.

---

# 26. Verify Audit Data

Run:

```powershell
python -c "from app.database.session import SessionLocal; from app.models.ticket_audit_log import TicketAuditLog; s=SessionLocal(); rows=s.query(TicketAuditLog).order_by(TicketAuditLog.id.desc()).limit(10).all(); print('Audit records shown:', len(rows)); [print(x.id, x.ticket_id, x.action, x.old_value, x.new_value, x.performed_by) for x in rows]; s.close()"
```

Confirm that audit history exists for the ticket or workflow operations intended for demonstration.

---

# 27. Verify Failure Recovery Evidence

Run:

```powershell
python -c "from app.database.session import SessionLocal; from app.models.dead_letter_record import DeadLetterRecord; s=SessionLocal(); rows=s.query(DeadLetterRecord).order_by(DeadLetterRecord.id.desc()).limit(10).all(); print('Dead-letter records shown:', len(rows)); [print(x.id, x.workflow_execution_id, x.status, x.retry_count) for x in rows]; s.close()"
```

If no failure records exist, do not create uncontrolled production-like failures immediately before the presentation.

Use integration-test evidence and the documented failure-recovery flow instead.

---

# 28. Start the Application

Use a dedicated terminal:

```powershell
python main.py
```

Keep the server terminal visible and free of unrelated commands.

Do not use the application-server terminal for tests or database maintenance.

---

# 29. Verify Application Startup

Confirm that:

```text
Application startup completes without an unhandled exception.

Database initialization succeeds.

Expected routes are registered.

Dashboard is reachable.

Ticket list loads.

Ticket detail data loads.

Logs do not show unexpected startup failures.
```

Review:

```powershell
type logs\errors.log
```

and, if necessary:

```powershell
type logs\supportiq.log
```

Do not expose sensitive information from logs during the presentation.

---

# 30. Prepare Demo Terminals

Use three terminals.

## Terminal 1 — Application Server

```powershell
venv\Scripts\activate
python main.py
```

## Terminal 2 — Tests

```powershell
venv\Scripts\activate
python -m pytest -q
```

Optional coverage command:

```powershell
python -m pytest --cov=app --cov-report=term-missing -q
```

## Terminal 3 — Evaluation and Verification

```powershell
venv\Scripts\activate
python -m tests.manual_run_classification_evaluation
```

Use this terminal for read-only database and migration verification commands.

---

# 31. Prepare Editor Tabs

Open before the presentation:

```text
README.md

docs\architecture.md

docs\workflow.md

docs\evaluation_results.md

docs\security.md

docs\scalability.md

docs\demo_script.md

app\services\email_ingestion_service.py

app\services\ticket_analysis_normalizer.py

app\services\priority_service.py

app\services\routing_service.py

app\services\ticket_lifecycle_service.py

app\services\failure_recovery_service.py

app\prompts\registry.py
```

Position each file near the section that will be shown.

Do not waste demo time searching for files.

---

# 32. Final Five-Minute Verification

Five minutes before presenting, run only lightweight checks.

```powershell
git status --short

alembic current

python -m json.tool workflow\workflow_definition.json > nul

python -m json.tool docs\evaluation_results.json > nul
```

Verify:

```text
Application server is running.

Dashboard is open.

Demo ticket is visible.

Ticket detail page loads.

Evaluation results are available.

Architecture diagram is open.

Workflow diagram is open.

No credential files are visible.

No sensitive terminal history is visible.

Desktop notifications are disabled.

Backup evidence is available.
```

Do not rerun dependency installation, migrations, the full coverage suite, or live-provider evaluations during the final five minutes unless necessary.

---

# 33. Demo Recovery Instructions

## Application Startup Failure

Check:

```powershell
python --version

python -m pip check

alembic current

type logs\errors.log
```

Attempt:

```powershell
alembic upgrade head

python main.py
```

If startup remains unavailable, continue using:

```text
Architecture documentation

Workflow documentation

Database documentation

Verified test evidence

Evaluation results

Stored screenshots
```

---

## Database Connectivity Failure

Run:

```powershell
python -c "from sqlalchemy import text; from app.database.session import SessionLocal; s=SessionLocal(); print(s.execute(text('SELECT 1')).scalar()); s.close()"
```

Verify:

```text
Database service status

Database configuration

Network availability

Migration state
```

Do not reset or recreate the database during the live presentation.

Use verified backup evidence if recovery would consume presentation time.

---

## Migration Mismatch

Run:

```powershell
alembic current

alembic heads

alembic history
```

If the database is behind:

```powershell
alembic upgrade head
```

Do not edit migration files during the presentation.

---

## Automated Test Failure

Rerun the specific failing test:

```powershell
python -m pytest path\to\test_file.py::test_name -v
```

If the failure is environmental and cannot be resolved quickly:

```text
Show the latest verified complete test output.

Show evaluation evidence.

Continue the functional demonstration.

Do not modify application logic during the presentation.
```

---

## AI Provider Failure

Do not repeatedly retry live requests.

Continue using:

```text
Stored tickets

Mocked AI integration tests

Versioned prompt definitions

Normalization tests

Deterministic classification evaluation

Documented AI evaluation methodology
```

---

## IMAP Failure

Continue using:

```text
Stored demo tickets

Email parser tests

Email ingestion service tests

Integration workflow tests
```

Do not expose mailbox credentials while troubleshooting.

---

## SMTP Failure

Continue using:

```text
Acknowledgement service tests

SMTP service tests

Stored acknowledgement timestamps

Audit evidence
```

Do not expose SMTP credentials.

---

## Dashboard Failure

Continue using:

```text
API route implementation

Service-layer implementation

Database records

Test results

Evaluation results

Architecture and workflow documentation
```

---

## Classification Evaluation Failure

Verify:

```powershell
python -m json.tool sample_data\classification_evaluation_dataset.json > nul

python -m pytest tests\test_classification_evaluation.py -v
```

Use the latest verified results recorded in:

```text
docs\evaluation_results.md
```

Do not edit evaluation data during the presentation.

---

# 34. Backup Evidence

Prepare backup evidence before the presentation.

Recommended evidence:

```text
Screenshot of dashboard ticket list

Screenshot of ticket detail page

Screenshot of audit history

Screenshot of monitoring information

Screenshot of failure recovery information

Complete pytest result

Coverage result

Classification evaluation output

Architecture diagram

Workflow diagram

ER diagram

Sequence diagram
```

Backup evidence should contain no credentials or sensitive customer data.

---

# 35. Demo Safety Rules

During the presentation:

```text
Do not display .env.

Do not display API keys.

Do not display database passwords.

Do not display email credentials.

Do not print the complete process environment.

Do not depend on live provider availability.

Do not depend on new incoming email.

Do not run destructive database commands.

Do not reset the database.

Do not edit Alembic migrations.

Do not modify evaluation datasets.

Do not modify business rules.

Do not change AI prompts.

Do not install or upgrade dependencies.

Do not debug unexpected infrastructure failures for several minutes.

Do not claim unverified evaluation results.

Do not claim planned scalability components are implemented.

Do not claim the application is production-ready solely because tests pass.
```

---

# 36. Deterministic Demo Strategy

The recommended demonstration strategy is:

```text
Use a pre-populated demo database.

Use previously processed tickets.

Use verified lifecycle and audit records.

Use deterministic automated tests.

Use deterministic classification evaluation.

Use stored evaluation evidence.

Use live dashboard navigation.

Use architecture and workflow documentation.

Treat live AI, IMAP, and SMTP operations as optional enhancements.
```

This approach demonstrates the implemented system while minimizing dependencies on external provider availability.

---

# 37. Final Readiness Criteria

The demo environment is READY when:

```text
The virtual environment is active.

Dependencies are consistent.

Credentials are configured but hidden.

The database is reachable.

The current Alembic revision is at head.

Required database tables exist.

Evaluation datasets are valid.

Classification routing coverage has no unsupported categories.

The complete test suite passes.

Coverage evidence is available.

Classification evaluation runs successfully.

The application starts successfully.

The dashboard is reachable.

A useful demo ticket exists.

Ticket details are available.

Audit evidence is available.

Failure recovery evidence or tests are available.

Documentation is complete.

Workflow definition is valid JSON.

Database schema deliverable exists.

Prompt deliverables exist and are populated.

Backup evidence is prepared.

The presenter has completed at least one timed rehearsal.
```

---

# 38. Latest Verified Project Evidence

At the time of Hour 17 documentation preparation:

```text
Automated tests:
452 passed

Warnings:
1 known BeautifulSoup/lxml deprecation warning

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

These values should only be updated after rerunning and verifying the corresponding commands.

---

# 39. Recommended Pre-Demo Command Order

Run the following sequence before the presentation:

```powershell
venv\Scripts\activate

git branch --show-current

git status --short

python --version

python -m pip check

git check-ignore .env

git ls-files .env

python -c "from sqlalchemy import text; from app.database.session import SessionLocal; s=SessionLocal(); print('Database connection:', s.execute(text('SELECT 1')).scalar()); s.close()"

alembic current

alembic heads

alembic upgrade head

alembic current

python -m json.tool workflow\workflow_definition.json > nul

python -m json.tool sample_data\ai_evaluation_dataset.json > nul

python -m json.tool sample_data\classification_evaluation_dataset.json > nul

python -m pytest -q

python -m pytest --cov=app --cov-report=term-missing -q

python -m tests.manual_run_classification_evaluation

python -m json.tool docs\evaluation_results.json > nul

python main.py
```

After startup:

```text
Open the dashboard.

Verify the demo ticket.

Verify ticket details.

Verify audit evidence.

Verify failure recovery evidence if used.

Open architecture.md.

Open workflow.md.

Open evaluation_results.md.

Start the timed rehearsal.
```

---

# Conclusion

SupportIQ-AI should be demonstrated using a deterministic, pre-verified environment.

The primary presentation path relies on the local application, relational database, stored demo data, automated tests, deterministic classification evaluation, documented architecture, and verified workflow evidence.

External AI, IMAP, and SMTP integrations should be treated as optional live enhancements rather than mandatory dependencies.

This preparation procedure reduces presentation risk while preserving evidence of the complete implemented customer-support automation workflow.
