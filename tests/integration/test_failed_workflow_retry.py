from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from uuid import uuid4
from sqlalchemy import select

from app.core.constants import (
    DeadLetterStatus,
    WorkflowExecutionStatus,
    WorkflowStage,
)
from app.models.dead_letter_record import DeadLetterRecord
from app.models.workflow_execution import WorkflowExecution
from app.repositories.dead_letter_repository import (
    DeadLetterRepository,
)
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)
from app.services.failure_recovery_service import (
    FailureRecoveryService,
)


def build_email_metadata() -> dict:
    return {
        "email": {
            "message_id": "<hour16-retry@example.com>",
            "sender_name": "Retry Customer",
            "sender_email": "customer@example.com",
            "subject": "Unable to access account",
            "body": "I cannot access my account.",
            "received_at": (
                datetime.now(timezone.utc).isoformat()
            ),
            "attachments": [],
        }
    }


def create_failed_execution(
    db_session,
) -> WorkflowExecution:
    suffix = uuid4().hex[:12]

    now = datetime.now(timezone.utc)

    message_id = (
        f"<hour16-retry-{suffix}@example.com>"
    )

    execution = WorkflowExecution(
        execution_id=f"hour16-failed-{suffix}",
        message_id=message_id,
        ticket_id=None,
        started_at=now,
        completed_at=now,
        duration_ms=100,
        status=WorkflowExecutionStatus.FAILED,
        current_stage=WorkflowStage.AI_ANALYSIS_STARTED,
        retry_count=3,
        failure_stage=WorkflowStage.AI_ANALYSIS_STARTED,
        error_type="LLMTimeoutError",
        error_message="The LLM request timed out.",
        retry_exhausted=True,
        failed_at=now,
        parent_execution_id=None,
        attempt_number=1,
        execution_metadata={
            "email": {
                "message_id": message_id,
                "sender_name": "Retry Customer",
                "sender_email": "customer@example.com",
                "subject": "Unable to access account",
                "body": "I cannot access my account.",
                "received_at": now.isoformat(),
                "attachments": [],
            }
        },
    )

    db_session.add(execution)
    db_session.flush()

    return execution


def create_dead_letter(
    db_session,
    execution: WorkflowExecution,
) -> DeadLetterRecord:
    repository = DeadLetterRepository(db_session)

    record = repository.create(
        workflow_execution_id=execution.id,
        ticket_id=None,
        failed_stage=str(execution.failure_stage),
        exception_type="LLMTimeoutError",
        sanitized_error_message=(
            "The LLM request timed out."
        ),
        retry_count=3,
        retry_exhausted=True,
    )

    db_session.flush()

    return record


def test_failed_workflow_manual_retry_resolves_dead_letter(
    db_session,
):
    original_execution = create_failed_execution(db_session)

    dead_letter = create_dead_letter(
        db_session,
        original_execution,
    )

    workflow_service = MagicMock()

    workflow_execution_repository = (
        WorkflowExecutionRepository(db_session)
    )

    dead_letter_repository = (
        DeadLetterRepository(db_session)
    )

    service = FailureRecoveryService(
        db_session,
        workflow_execution_repository=(
            workflow_execution_repository
        ),
        dead_letter_repository=dead_letter_repository,
        workflow_service=workflow_service,
    )

    result = service.retry_execution(
        original_execution.execution_id
    )

    db_session.refresh(original_execution)
    db_session.refresh(dead_letter)

    retry_execution = db_session.scalar(
        select(WorkflowExecution).where(
            WorkflowExecution.id
            == result.retry_execution_id
        )
    )

    assert retry_execution is not None

    assert original_execution.status == (
        WorkflowExecutionStatus.FAILED
    )

    assert retry_execution.execution_id != (
        original_execution.execution_id
    )

    assert retry_execution.parent_execution_id == (
        original_execution.id
    )

    assert retry_execution.attempt_number == 2

    assert retry_execution.status == (
        WorkflowExecutionStatus.SUCCESS
    )

    assert dead_letter.status == (
        DeadLetterStatus.RESOLVED
    )

    assert dead_letter.manual_retry_count == 1

    assert dead_letter.last_retry_execution_id == (
        retry_execution.id
    )

    workflow_service.process_email.assert_called_once()

    process_call = workflow_service.process_email.call_args

    assert process_call.kwargs[
        "workflow_execution"
    ] is retry_execution


def test_failed_manual_retry_reopens_dead_letter(
    db_session,
):
    original_execution = create_failed_execution(db_session)

    dead_letter = create_dead_letter(
        db_session,
        original_execution,
    )

    workflow_service = MagicMock()

    workflow_service.process_email.side_effect = RuntimeError(
        "Retry workflow failed."
    )

    workflow_execution_repository = (
        WorkflowExecutionRepository(db_session)
    )

    dead_letter_repository = (
        DeadLetterRepository(db_session)
    )

    service = FailureRecoveryService(
        db_session,
        workflow_execution_repository=(
            workflow_execution_repository
        ),
        dead_letter_repository=dead_letter_repository,
        workflow_service=workflow_service,
    )

    with pytest.raises(
        RuntimeError,
        match="Retry workflow failed.",
    ):
        service.retry_execution(
            original_execution.execution_id
        )

    db_session.refresh(dead_letter)

    retry_execution = db_session.scalar(
        select(WorkflowExecution).where(
            WorkflowExecution.parent_execution_id
            == original_execution.id
        )
    )

    assert retry_execution is not None

    assert dead_letter.status == DeadLetterStatus.OPEN

    assert dead_letter.manual_retry_count == 1

    assert dead_letter.last_retry_execution_id == (
        retry_execution.id
    )
