# Evaluation Results

## Overview

SupportIQ-AI includes automated tests, integration tests, deterministic classification evaluation, AI-provider evaluation tooling, manual verification scripts, and coverage reporting.

The evaluation strategy verifies both software correctness and the behavior of the ticket-processing pipeline.

The primary evaluation areas are:

* Automated unit and service tests.
* API route tests.
* Repository and persistence tests.
* Integration workflow tests.
* Failure recovery and retry tests.
* Ticket lifecycle and audit tests.
* Classification evaluation.
* Priority evaluation.
* Routing evaluation.
* Live AI-provider evaluation.
* Code coverage measurement.
* Manual end-to-end verification.

The latest verified automated test run completed successfully with:

```text
452 passed
1 warning
```

The latest verified coverage run reported:

```text
Total statements: 2767
Missed statements: 300
Total coverage: 89%
```

The deterministic classification evaluation dataset contains:

```text
50 samples
```

The latest classification evaluation produced:

```text
Category Accuracy: 100.00%
Priority Accuracy: 94.00%
Routing Accuracy: 76.00%
```

---

## Evaluation Objectives

The SupportIQ-AI evaluation process is designed to answer the following questions:

1. Does the application behave correctly at the unit and service level?
2. Do repositories correctly persist and retrieve database entities?
3. Do ticket-processing components work together correctly?
4. Are transaction boundaries and rollback behavior correct?
5. Are ticket lifecycle transitions validated and audited?
6. Are workflow failures persisted and recoverable?
7. Does retry handling behave deterministically?
8. Does the classification evaluation framework detect category, priority, and routing mismatches?
9. Does the AI evaluation framework support repeatable dataset-based evaluation?
10. Is the codebase sufficiently exercised by automated tests?

---

## Automated Test Results

The complete automated test suite was executed using:

```powershell
python -m pytest -q
```

Latest verified result:

```text
452 passed, 1 warning in 3.32s
```

The warning was produced by the Beautiful Soup `lxml` HTML parser integration:

```text
DeprecationWarning:
The 'strip_cdata' option of HTMLParser() has never done anything
and will eventually be removed.
```

This warning originates from a third-party dependency and does not represent a SupportIQ-AI test failure.

All automated tests completed successfully.

---

## Test Coverage Results

Coverage was measured using:

```powershell
python -m pytest --cov=app --cov-report=term-missing -q
```

Latest verified result:

```text
452 passed
1 warning

TOTAL
2767 statements
300 missed statements
89% coverage
```

The overall coverage result demonstrates broad automated verification across the application.

Several critical modules achieved complete or near-complete coverage.

Examples include:

```text
dashboard_routes.py                         100%
failure_recovery_routes.py                  100%
manual_review_routes.py                     100%
monitoring_routes.py                         97%

constants.py                                100%
exceptions.py                                93%
retry.py                                     91%

classification_evaluation.py                 95%
metrics.py                                   100%

dead_letter_record.py                       100%
internal_note.py                            100%
ticket.py                                   100%
ticket_attachment.py                        100%
ticket_audit_log.py                         100%
workflow_execution.py                       100%

attachment_repository.py                    100%
audit_repository.py                         100%
dead_letter_repository.py                    95%
internal_note_repository.py                 100%
ticket_repository.py                         98%

acknowledgement_service.py                  100%
attachment_service.py                       100%
dashboard_service.py                        100%
failure_handling_service.py                 100%
failure_recovery_service.py                  92%
groq_llm_service.py                          98%
manual_review_service.py                     96%
monitoring_service.py                       100%
priority_service.py                          96%
reply_suggestion_service.py                  96%
routing_service.py                          100%
smtp_service.py                              94%
ticket_analysis_normalizer.py                98%
ticket_lifecycle_service.py                  91%
workflow_execution_service.py                93%
workflow_service.py                          89%
```

---

## Coverage Limitations

The overall coverage result is strong, but some modules have lower coverage.

The most significant examples are:

```text
app/evaluation/runner.py                       0%

app/services/imap_service.py                  21%

app/repositories/workflow_execution_repository.py
                                                46%

app/database/session.py                       62%

app/api/dependencies.py                       64%

app/services/email_ingestion_service.py       75%

app/services/ticket_service.py                80%
```

These lower-coverage areas should be interpreted according to their responsibilities.

### Evaluation Runner

`app/evaluation/runner.py` currently has no direct automated test coverage.

The project instead includes manual evaluation runners and dedicated tests for the underlying evaluation components.

Future work should add automated tests for command-line runner behavior and output generation.

### IMAP Service

The IMAP service depends heavily on external mailbox behavior and network interactions.

Current tests exercise selected behavior, but complete coverage would require additional protocol mocking and failure simulation.

Future evaluation should include:

* Authentication failures.
* Connection timeouts.
* Mailbox selection failures.
* Message fetch failures.
* Malformed email messages.
* Provider disconnections.
* Large mailbox behavior.
* Duplicate message delivery.

### Workflow Execution Repository

The workflow execution repository contains multiple persistence, monitoring, retry, and execution-lineage paths.

Additional repository tests should exercise:

* Concurrent execution claiming.
* Retry lineage queries.
* Monitoring aggregation.
* Execution-history filters.
* Failure-state transitions.
* Boundary conditions around retry counters.

---

## Integration Test Coverage

SupportIQ-AI contains dedicated integration tests under:

```text
tests/integration/
```

Current integration test modules include:

```text
test_acknowledgement_workflow.py

test_email_groq_database_workflow.py

test_email_ticket_workflow.py

test_failed_workflow_retry.py

test_ticket_lifecycle_audit_workflow.py

test_ticket_processing_workflow.py
```

These tests verify interactions across service, repository, schema, and persistence boundaries.

---

## Email-to-Ticket Workflow Evaluation

The email-to-ticket integration tests verify the persistence workflow from parsed email input to database-backed ticket creation.

The tests validate:

* Ticket creation from parsed email data.
* Normalized analysis data.
* Priority decisions.
* Routing decisions.
* Reply suggestions.
* Ticket persistence.
* Distinct ticket creation.
* Transaction rollback behavior.

The rollback integration test verifies that ticket records do not survive an explicit transaction rollback.

This provides evidence that transaction boundaries behave correctly during integration workflows.

---

## Email, Groq, and Database Workflow Evaluation

The Groq workflow integration test verifies interaction between:

```text
Email input

Groq LLM service abstraction

Ticket analysis

Database persistence
```

External AI-provider behavior is mocked for deterministic automated execution.

This allows the integration path to be tested without:

* Consuming provider credits.
* Requiring network access.
* Depending on provider availability.
* Introducing nondeterministic model responses.

---

## Ticket Lifecycle and Audit Evaluation

Ticket lifecycle integration tests verify:

* Valid ticket status transitions.
* Persistence of status changes.
* Creation of audit records.
* Rejection of invalid lifecycle transitions.
* Prevention of audit creation for rejected transitions.

The lifecycle model supports controlled transitions between:

```text
OPEN

IN_PROGRESS

WAITING_FOR_CUSTOMER

RESOLVED

CLOSED
```

Invalid state transitions raise the configured lifecycle exception instead of silently mutating ticket state.

Audit persistence provides traceability for successful lifecycle operations.

---

## Failure Recovery Evaluation

Failure recovery integration tests verify:

* Failed workflow persistence.
* Dead-letter record creation.
* Manual retry execution.
* Resolution of dead-letter records after successful retry.
* Reopening or preservation of failure state after unsuccessful retry.
* Retry execution lineage.

These tests demonstrate that workflow failures can be persisted and retried instead of being silently discarded.

---

## Acknowledgement Workflow Evaluation

Acknowledgement workflow tests verify the customer acknowledgement path.

Evaluation includes:

* Acknowledgement decision behavior.
* SMTP service integration boundaries.
* Ticket acknowledgement state.
* Duplicate acknowledgement prevention.
* Failure behavior.

External SMTP operations are mocked during automated testing to preserve deterministic execution.

---

## Deterministic Classification Evaluation

SupportIQ-AI contains a deterministic classification evaluation framework implemented in:

```text
app/evaluation/classification_evaluation.py
```

The evaluation runner is:

```text
tests/manual_run_classification_evaluation.py
```

The dataset is:

```text
sample_data/classification_evaluation_dataset.json
```

The dataset contains:

```text
50 samples
```

Each sample contains:

```text
id

subject

body

predicted_category

predicted_priority

confidence_score

expected_category

expected_priority

expected_route
```

The evaluation framework compares application decisions with expected labels.

---

## Classification Evaluation Command

The evaluation was executed using:

```powershell
python -m tests.manual_run_classification_evaluation
```

Latest verified output:

```text
============================================================
SupportIQ Classification Evaluation
============================================================
Dataset: SupportIQ Classification Evaluation Dataset
Samples: 50
Category Accuracy: 100.00%
Priority Accuracy: 94.00%
Routing Accuracy: 76.00%
============================================================
Results written to:
docs/evaluation_results.json
```

---

## Category Evaluation Results

Latest result:

```text
Category Accuracy: 100.00%
```

Category accuracy is calculated as:

```text
Correct category predictions
----------------------------
Total evaluated samples
```

A 100% category accuracy result means that all 50 evaluated samples produced the expected category result according to the deterministic evaluation dataset.

This result demonstrates complete agreement between the evaluated category outputs and the dataset labels.

It does not establish general real-world AI classification accuracy.

The result is limited to:

* The current evaluation dataset.
* The current category taxonomy.
* The current deterministic evaluation implementation.
* The current sample distribution.

---

## Priority Evaluation Results

Latest result:

```text
Priority Accuracy: 94.00%
```

Priority accuracy is calculated as:

```text
Correct final priority decisions
--------------------------------
Total evaluated samples
```

For a 50-sample dataset, 94% accuracy corresponds to:

```text
47 correct priority decisions

3 incorrect priority decisions
```

Priority evaluation exercises the application's final priority decision behavior.

The result may reflect:

* AI-recommended priority.
* Deterministic priority rules.
* Confidence handling.
* Escalation logic.
* Normalized analysis data.

The three mismatches should be reviewed to determine whether they represent:

* Incorrect expected labels.
* Missing deterministic rules.
* Ambiguous ticket descriptions.
* Priority-policy differences.
* Legitimate edge cases.

The evaluation result should therefore be used for targeted rule analysis rather than interpreted only as a single aggregate score.

---

## Routing Evaluation Results

Latest result:

```text
Routing Accuracy: 76.00%
```

Routing accuracy is calculated as:

```text
Correct assigned routes
-----------------------
Total evaluated samples
```

For a 50-sample dataset, 76% accuracy corresponds to:

```text
38 correct routing decisions

12 incorrect routing decisions
```

Routing is the weakest of the three current deterministic evaluation metrics.

The routing dataset includes categories such as:

```text
Account Access

Billing

Cancellation

Complaint

Feature Request

Product Inquiry

Refund

Sales

Technical Support
```

The configured routing table supports all categories currently present in the classification evaluation dataset.

The 76% routing result indicates that configuration completeness alone does not guarantee agreement with expected routes.

The mismatches should be inspected individually.

Possible causes include:

* Dataset expected routes differing from configured routing policy.
* Category aliases mapping to different team names.
* Legacy labels in the evaluation dataset.
* Routing policy changes made after dataset creation.
* Expected-route values requiring normalization.

---

## Routing Configuration Validation

The routing configuration and dataset were compared using:

```powershell
python -c "import json; from app.config.routing_rules import CATEGORY_TEAM_ROUTES; d=json.load(open('sample_data/classification_evaluation_dataset.json', encoding='utf-8')); cats=set(x['predicted_category'] for x in d['samples']); print('Configured:', sorted(CATEGORY_TEAM_ROUTES)); print('Dataset:', sorted(cats)); print('Unsupported:', sorted(cats-set(CATEGORY_TEAM_ROUTES)))"
```

Latest verified result:

```text
Unsupported: []
```

This confirms that every predicted category in the classification evaluation dataset has a configured routing rule.

---

## Dataset Structure Validation

Both evaluation datasets were validated as syntactically valid JSON.

Commands:

```powershell
python -m json.tool sample_data\ai_evaluation_dataset.json > nul

python -m json.tool sample_data\classification_evaluation_dataset.json > nul
```

Both commands completed successfully.

The classification evaluation dataset was also checked for required fields.

Command:

```powershell
python -c "import json; p='sample_data/classification_evaluation_dataset.json'; d=json.load(open(p, encoding='utf-8')); required={'id','subject','body','predicted_category','predicted_priority','confidence_score','expected_category','expected_priority','expected_route'}; bad=[(i, sorted(required-set(x))) for i,x in enumerate(d['samples']) if required-set(x)]; print('Samples:', len(d['samples'])); print('Invalid samples:', bad)"
```

Latest verified result:

```text
Samples: 50

Invalid samples: []
```

---

## AI Evaluation Framework

SupportIQ-AI also includes an AI-provider evaluation framework.

Relevant files include:

```text
app/evaluation/runner.py

app/evaluation/metrics.py

tests/manual_run_ai_evaluation.py

sample_data/ai_evaluation_dataset.json

docs/ai_evaluation_report.json
```

The AI evaluation path is distinct from deterministic classification evaluation.

It may invoke the configured live AI provider and therefore depends on:

* Valid provider credentials.
* Network connectivity.
* Provider availability.
* Provider rate limits.
* Model behavior.
* Retry configuration.

---

## Live AI Evaluation Execution

The live AI evaluation runner can be started using:

```powershell
python -m tests.manual_run_ai_evaluation
```

During the latest observed execution, repeated messages were produced:

```text
Retry scheduled after operation failure.
```

This demonstrates that retry handling was activated during provider failures.

However, because a complete successful live-provider evaluation result was not captured, no final live AI accuracy metric is claimed in this document.

The deterministic classification evaluation remains the reproducible evaluation evidence for the current deliverable.

---

## Why Deterministic and Live Evaluations Are Separated

Deterministic evaluation and live-provider evaluation serve different purposes.

### Deterministic Evaluation

Advantages:

* Repeatable.
* Fast.
* No external credentials required.
* No provider cost.
* No network dependency.
* Suitable for local verification.
* Suitable for continuous integration.

Limitations:

* Uses stored predicted values.
* Does not measure current live-model output quality.
* Does not capture provider nondeterminism.
* Does not capture provider latency.

### Live AI Evaluation

Advantages:

* Exercises the real AI integration.
* Measures current provider behavior.
* Exposes prompt and model quality issues.
* Measures live latency and provider failures.

Limitations:

* Requires credentials.
* Requires network connectivity.
* May consume provider quota.
* Can be rate limited.
* Can be nondeterministic.
* May fail because of provider outages.

Both evaluation approaches are useful and should remain separate.

---

## Failure Scenario Evaluation

SupportIQ-AI tests multiple failure scenarios.

Examples include:

```text
Missing evaluation dataset

Invalid JSON dataset

Missing required sample fields

Duplicate sample identifiers

Invalid ticket lifecycle transitions

Workflow execution failures

Retry failures

Dead-letter persistence

Manual retry failures

Transaction rollback

SMTP failures

LLM failures

Malformed LLM output

Normalization failures

Unmapped routing categories

Repository failures
```

These tests are important because production support systems must preserve workflow state and diagnostic information when failures occur.

---

## Retry Evaluation

Retry behavior is tested at the core retry utility and workflow levels.

The retry implementation verifies:

* Retryable failures.
* Retry limits.
* Delay calculation.
* Backoff behavior.
* Exhausted retry handling.
* Workflow failure persistence.

The live AI evaluation attempt also demonstrated retry activation during provider failures.

---

## Persistence and Rollback Evaluation

Database-backed integration tests verify:

* Entity persistence.
* Repository behavior.
* Ticket creation.
* Attachment persistence boundaries.
* Audit persistence.
* Workflow execution persistence.
* Dead-letter persistence.
* Transaction rollback.

Rollback tests provide evidence that uncommitted workflow data can be discarded correctly.

---

## Evaluation Metrics Interpretation

Aggregate metrics should not be interpreted without considering dataset size and evaluation design.

Current deterministic metrics are:

```text
Samples: 50

Category Accuracy: 100%

Priority Accuracy: 94%

Routing Accuracy: 76%
```

Interpretation:

### Category Classification

The category result is excellent for the current dataset.

Additional samples are required before claiming broad production classification performance.

### Priority Decision

Priority evaluation is strong but has three mismatches.

These mismatches should be reviewed individually to determine whether rule improvements or dataset corrections are appropriate.

### Routing Decision

Routing evaluation has twelve mismatches and represents the largest current evaluation gap.

Routing rules, expected team labels, category aliases, and dataset consistency should be reviewed before production deployment.

### Software Correctness

The automated test suite reports:

```text
452 passing tests
```

with:

```text
89% overall code coverage
```

This provides strong software verification evidence for the current project scope.

---

## Known Evaluation Limitations

The current evaluation framework has several limitations.

These include:

* The deterministic classification dataset contains only 50 samples.
* Dataset samples may not represent real production ticket distributions.
* Category accuracy is measured against stored dataset predictions.
* Deterministic evaluation does not measure current live AI output quality.
* Live AI evaluation depends on external provider availability.
* A complete successful live AI evaluation result was not captured during the latest run.
* Priority evaluation contains three mismatches.
* Routing evaluation contains twelve mismatches.
* Some external-service code paths require additional protocol-level testing.
* IMAP service coverage is low compared with most application services.
* Evaluation runner command behavior lacks direct automated test coverage.
* No load-testing results are included.
* No production latency benchmarks are included.
* No AI token-cost evaluation is included.
* No statistical confidence intervals are calculated.
* No adversarial prompt-injection benchmark is currently included.
* No production drift monitoring is implemented.

---

## Recommended Future Evaluation Improvements

Future evaluation work should include:

1. Expand deterministic datasets to hundreds or thousands of samples.
2. Use anonymized production-like ticket distributions.
3. Add per-category precision, recall, and F1-score.
4. Add priority confusion matrices.
5. Add routing confusion matrices.
6. Review all priority mismatches.
7. Review all routing mismatches.
8. Add dataset versioning.
9. Add prompt-version tracking to AI evaluation reports.
10. Add model-version tracking.
11. Record provider latency.
12. Record token usage and estimated AI cost.
13. Add automated tests for the evaluation runner.
14. Increase IMAP service test coverage.
15. Add provider timeout and rate-limit simulations.
16. Add prompt-injection evaluation samples.
17. Add malformed attachment evaluation samples.
18. Add load tests.
19. Add database performance benchmarks.
20. Add production drift monitoring when real operational data becomes available.

---

## Reproduction Commands

Run the complete automated test suite:

```powershell
python -m pytest -q
```

Run tests with coverage:

```powershell
python -m pytest --cov=app --cov-report=term-missing -q
```

Validate the AI evaluation dataset:

```powershell
python -m json.tool sample_data\ai_evaluation_dataset.json > nul
```

Validate the classification evaluation dataset:

```powershell
python -m json.tool sample_data\classification_evaluation_dataset.json > nul
```

Run deterministic classification evaluation:

```powershell
python -m tests.manual_run_classification_evaluation
```

Run live AI-provider evaluation:

```powershell
python -m tests.manual_run_ai_evaluation
```

The live AI-provider evaluation should only be executed when valid provider credentials, network connectivity, provider quota, and sufficient execution time are available.

---

## Evaluation Evidence Summary

Current verified evidence:

```text
Automated tests:
452 passed

Warnings:
1 third-party deprecation warning

Overall code coverage:
89%

Classification evaluation dataset:
50 samples

Category accuracy:
100%

Priority accuracy:
94%

Routing accuracy:
76%

Unsupported dataset routing categories:
0

Invalid classification dataset samples:
0

Live AI evaluation:
Runner available
Retry behavior observed
No complete successful final result currently claimed
```

---

## Conclusion

SupportIQ-AI has comprehensive automated verification for the current project scope.

The project has:

* 452 passing automated tests.
* 89% total code coverage.
* Unit, service, route, repository, and integration testing.
* Ticket lifecycle and audit verification.
* Failure recovery and dead-letter verification.
* Transaction rollback testing.
* Deterministic classification evaluation.
* Priority evaluation.
* Routing evaluation.
* Live AI-provider evaluation tooling.
* Dataset validation commands.
* Reproducible evaluation commands.

The deterministic classification evaluation produced 100% category accuracy, 94% priority accuracy, and 76% routing accuracy across 50 samples.

The results demonstrate strong category agreement and priority behavior for the current dataset while identifying routing as the primary evaluation area requiring further refinement.

The automated test and coverage results provide strong software correctness evidence, while the evaluation limitations define clear future work before large-scale production deployment.
