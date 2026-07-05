from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import UUID

from app.core.constants import (
    WorkflowExecutionStatus,
    WorkflowStage,
)
from app.models.workflow_execution import WorkflowExecution
from app.services.workflow_execution_service import (
    WorkflowExecutionService,
)


def create_execution(
    *,
    stage: WorkflowStage = WorkflowStage.EMAIL_FETCHED,
) -> WorkflowExecution:
    return WorkflowExecution(
        execution_id="11111111-1111-4111-8111-111111111111",
        message_id="<workflow-service-test@example.com>",
        ticket_id=None,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        duration_ms=None,
        status=WorkflowExecutionStatus.RUNNING,
        current_stage=stage,
        retry_count=0,
        failure_stage=None,
        error_type=None,
        error_message=None,
        execution_metadata=None,
    )


def test_start_execution_creates_uuid():
    repository = MagicMock()
    service = WorkflowExecutionService(repository)

    execution = service.start_execution(
        message_id="<start-uuid@example.com>",
    )

    UUID(execution.execution_id)

    repository.add.assert_called_once_with(execution)


def test_start_execution_uses_running_status():
    repository = MagicMock()
    service = WorkflowExecutionService(repository)

    execution = service.start_execution(
        message_id="<running-status@example.com>",
    )

    assert execution.status == WorkflowExecutionStatus.RUNNING


def test_start_execution_records_email_fetched_stage():
    repository = MagicMock()
    service = WorkflowExecutionService(repository)

    execution = service.start_execution(
        message_id="<email-fetched@example.com>",
    )

    assert execution.current_stage == WorkflowStage.EMAIL_FETCHED


def test_advance_stage_updates_stage():
    repository = MagicMock()

    execution = create_execution()

    def mark_stage(target, *, stage):
        target.current_stage = stage
        return target

    repository.mark_stage.side_effect = mark_stage

    service = WorkflowExecutionService(repository)

    result = service.advance_stage(
        execution,
        stage=WorkflowStage.EMAIL_PARSED,
    )

    assert result is execution
    assert execution.current_stage == WorkflowStage.EMAIL_PARSED

    repository.mark_stage.assert_called_once_with(
        execution,
        stage=WorkflowStage.EMAIL_PARSED,
    )


def test_record_retry_increments_retry_count():
    repository = MagicMock()

    execution = create_execution()

    def increment_retry_count(target):
        target.retry_count += 1
        return target

    repository.increment_retry_count.side_effect = (
        increment_retry_count
    )

    service = WorkflowExecutionService(repository)

    result = service.record_retry(execution)

    assert result is execution
    assert execution.retry_count == 1

    repository.increment_retry_count.assert_called_once_with(
        execution
    )


def test_attach_ticket_records_ticket_id_and_ticket_created_stage():
    repository = MagicMock()

    execution = create_execution()

    def mark_stage(target, *, stage):
        target.current_stage = stage
        return target

    repository.mark_stage.side_effect = mark_stage

    service = WorkflowExecutionService(repository)

    result = service.attach_ticket(
        execution,
        ticket_id=501,
    )

    assert result is execution
    assert execution.ticket_id == 501
    assert execution.current_stage == WorkflowStage.TICKET_CREATED

    repository.mark_stage.assert_called_once_with(
        execution,
        stage=WorkflowStage.TICKET_CREATED,
    )


def test_complete_execution_records_success():
    repository = MagicMock()

    execution = create_execution(
        stage=WorkflowStage.ACKNOWLEDGEMENT_SENT,
    )

    def mark_success(
        target,
        *,
        completed_at,
        duration_ms,
    ):
        target.status = WorkflowExecutionStatus.SUCCESS
        target.current_stage = WorkflowStage.WORKFLOW_COMPLETED
        target.completed_at = completed_at
        target.duration_ms = duration_ms
        return target

    repository.mark_success.side_effect = mark_success

    service = WorkflowExecutionService(repository)

    result = service.complete_execution(execution)

    assert result is execution
    assert execution.status == WorkflowExecutionStatus.SUCCESS

    repository.mark_success.assert_called_once()


def test_complete_execution_records_workflow_completed_stage():
    repository = MagicMock()

    execution = create_execution(
        stage=WorkflowStage.ACKNOWLEDGEMENT_SENT,
    )

    def mark_success(
        target,
        *,
        completed_at,
        duration_ms,
    ):
        target.status = WorkflowExecutionStatus.SUCCESS
        target.current_stage = WorkflowStage.WORKFLOW_COMPLETED
        target.completed_at = completed_at
        target.duration_ms = duration_ms
        return target

    repository.mark_success.side_effect = mark_success

    service = WorkflowExecutionService(repository)

    service.complete_execution(execution)

    assert execution.current_stage == WorkflowStage.WORKFLOW_COMPLETED


def test_complete_execution_calculates_duration():
    repository = MagicMock()

    started_at = datetime.now(timezone.utc) - timedelta(
        milliseconds=250
    )

    execution = create_execution(
        stage=WorkflowStage.ACKNOWLEDGEMENT_SENT,
    )
    execution.started_at = started_at

    captured_duration = None

    def mark_success(
        target,
        *,
        completed_at,
        duration_ms,
    ):
        nonlocal captured_duration

        captured_duration = duration_ms

        target.status = WorkflowExecutionStatus.SUCCESS
        target.current_stage = WorkflowStage.WORKFLOW_COMPLETED
        target.completed_at = completed_at
        target.duration_ms = duration_ms

        return target

    repository.mark_success.side_effect = mark_success

    service = WorkflowExecutionService(repository)

    service.complete_execution(execution)

    assert captured_duration is not None
    assert captured_duration >= 200
    assert execution.duration_ms == captured_duration


def test_fail_execution_records_failed_status():
    repository = MagicMock()

    execution = create_execution(
        stage=WorkflowStage.AI_ANALYSIS_STARTED,
    )

    def mark_failure(
        target,
        *,
        completed_at,
        duration_ms,
        error_type,
        error_message,
    ):
        target.status = WorkflowExecutionStatus.FAILED
        target.completed_at = completed_at
        target.duration_ms = duration_ms
        target.failure_stage = target.current_stage
        target.error_type = error_type
        target.error_message = error_message
        return target

    repository.mark_failure.side_effect = mark_failure

    service = WorkflowExecutionService(repository)

    result = service.fail_execution(
        execution,
        error=RuntimeError("AI provider unavailable"),
    )

    assert result is execution
    assert execution.status == WorkflowExecutionStatus.FAILED


def test_fail_execution_preserves_last_stage():
    repository = MagicMock()

    execution = create_execution(
        stage=WorkflowStage.PRIORITY_ASSIGNED,
    )

    def mark_failure(
        target,
        *,
        completed_at,
        duration_ms,
        error_type,
        error_message,
    ):
        target.status = WorkflowExecutionStatus.FAILED
        target.completed_at = completed_at
        target.duration_ms = duration_ms
        target.failure_stage = target.current_stage
        target.error_type = error_type
        target.error_message = error_message
        return target

    repository.mark_failure.side_effect = mark_failure

    service = WorkflowExecutionService(repository)

    service.fail_execution(
        execution,
        error=RuntimeError("Routing failed"),
    )

    assert execution.current_stage == WorkflowStage.PRIORITY_ASSIGNED
    assert execution.failure_stage == WorkflowStage.PRIORITY_ASSIGNED


def test_fail_execution_records_exception_class():
    repository = MagicMock()

    execution = create_execution(
        stage=WorkflowStage.AI_ANALYSIS_STARTED,
    )

    def mark_failure(
        target,
        *,
        completed_at,
        duration_ms,
        error_type,
        error_message,
    ):
        target.status = WorkflowExecutionStatus.FAILED
        target.completed_at = completed_at
        target.duration_ms = duration_ms
        target.failure_stage = target.current_stage
        target.error_type = error_type
        target.error_message = error_message
        return target

    repository.mark_failure.side_effect = mark_failure

    service = WorkflowExecutionService(repository)

    service.fail_execution(
        execution,
        error=ValueError("Invalid AI response"),
    )

    assert execution.error_type == "ValueError"


def test_fail_execution_records_exception_message():
    repository = MagicMock()

    execution = create_execution(
        stage=WorkflowStage.VALIDATION_COMPLETED,
    )

    def mark_failure(
        target,
        *,
        completed_at,
        duration_ms,
        error_type,
        error_message,
    ):
        target.status = WorkflowExecutionStatus.FAILED
        target.completed_at = completed_at
        target.duration_ms = duration_ms
        target.failure_stage = target.current_stage
        target.error_type = error_type
        target.error_message = error_message
        return target

    repository.mark_failure.side_effect = mark_failure

    service = WorkflowExecutionService(repository)

    service.fail_execution(
        execution,
        error=RuntimeError("Priority assignment failed"),
    )

    assert execution.error_message == "Priority assignment failed"


def test_calculate_duration_ms_cannot_be_negative():
    started_at = datetime.now(timezone.utc)

    completed_at = started_at - timedelta(seconds=1)

    duration_ms = WorkflowExecutionService.calculate_duration_ms(
        started_at,
        completed_at,
    )

    assert duration_ms == 0


def test_get_execution_returns_repository_result():
    repository = MagicMock()

    execution = create_execution()

    repository.get_by_execution_id.return_value = execution

    service = WorkflowExecutionService(repository)

    result = service.get_execution(
        execution.execution_id
    )

    assert result is execution

    repository.get_by_execution_id.assert_called_once_with(
        execution.execution_id
    )


def test_get_by_message_id_returns_repository_result():
    repository = MagicMock()

    execution = create_execution()

    repository.get_by_message_id.return_value = execution

    service = WorkflowExecutionService(repository)

    result = service.get_by_message_id(
        execution.message_id
    )

    assert result is execution

    repository.get_by_message_id.assert_called_once_with(
        execution.message_id
    )
