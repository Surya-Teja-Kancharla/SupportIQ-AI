from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.constants import (
    DeadLetterStatus,
    WorkflowExecutionStatus,
)
from app.models.dead_letter_record import DeadLetterRecord
from app.models.workflow_execution import WorkflowExecution
from app.schemas.failure_recovery_schema import WorkflowRetryResponse
from app.services.failure_recovery_service import (
    FailureRecoveryService,
)


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def workflow_execution_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def dead_letter_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def workflow_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(
    session: MagicMock,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
    workflow_service: MagicMock,
) -> FailureRecoveryService:
    return FailureRecoveryService(
        session,
        workflow_execution_repository=(
            workflow_execution_repository
        ),
        dead_letter_repository=dead_letter_repository,
        workflow_service=workflow_service,
    )


def build_failed_execution() -> WorkflowExecution:
    return WorkflowExecution(
        id=10,
        execution_id="failed-execution-id",
        message_id="<customer-message@example.com>",
        ticket_id=20,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration_ms=100,
        status=WorkflowExecutionStatus.FAILED,
        current_stage="AI_ANALYSIS_STARTED",
        retry_count=3,
        failure_stage="AI_ANALYSIS_STARTED",
        error_type="LLMTimeoutError",
        error_message="The LLM provider request timed out.",
        retry_exhausted=True,
        failed_at=datetime.now(timezone.utc),
        parent_execution_id=None,
        attempt_number=1,
        execution_metadata={
            "email": {
                "message_id": (
                    "<customer-message@example.com>"
                ),
                "sender_email": "customer@example.com",
                "subject": "Unable to access account",
                "body": "I cannot access my account.",
                "received_at": (
                    datetime.now(timezone.utc).isoformat()
                ),
                "attachments": [],
            }
        },
    )


def build_retry_execution() -> WorkflowExecution:
    return WorkflowExecution(
        id=11,
        execution_id="retry-execution-id",
        message_id="<customer-message@example.com>",
        ticket_id=20,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        duration_ms=None,
        status=WorkflowExecutionStatus.RUNNING,
        current_stage="EMAIL_FETCHED",
        retry_count=0,
        failure_stage=None,
        error_type=None,
        error_message=None,
        retry_exhausted=False,
        failed_at=None,
        parent_execution_id=10,
        attempt_number=2,
        execution_metadata=None,
    )


def build_dead_letter_record() -> DeadLetterRecord:
    return DeadLetterRecord(
        id=100,
        workflow_execution_id=10,
        ticket_id=20,
        failed_stage="AI_ANALYSIS_STARTED",
        exception_type="LLMTimeoutError",
        sanitized_error_message=(
            "The LLM provider request timed out."
        ),
        retry_count=3,
        retry_exhausted=True,
        status=DeadLetterStatus.OPEN,
        manual_retry_count=0,
        last_retry_execution_id=None,
    )


def test_retry_execution_success(
    service: FailureRecoveryService,
    session: MagicMock,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
    workflow_service: MagicMock,
) -> None:
    original_execution = build_failed_execution()
    retry_execution = build_retry_execution()
    dead_letter = build_dead_letter_record()

    workflow_execution_repository.get_by_execution_id.return_value = (
        original_execution
    )

    dead_letter_repository.get_by_execution_id.return_value = (
        dead_letter
    )

    workflow_execution_repository.create_retry_execution.return_value = (
        retry_execution
    )

    workflow_service.process_email.return_value = SimpleNamespace(
        ticket_id=20,
        execution_id=retry_execution.execution_id,
    )

    result = service.retry_execution(
        original_execution.execution_id
    )

    assert isinstance(result, WorkflowRetryResponse)

    assert result.original_execution_id == original_execution.id
    assert result.retry_execution_id == retry_execution.id
    assert result.attempt_number == 2
    assert result.status == WorkflowExecutionStatus.SUCCESS

    workflow_execution_repository.get_by_execution_id.assert_called_once_with(
        original_execution.execution_id
    )

    dead_letter_repository.get_by_execution_id.assert_called_once_with(
        original_execution.id
    )

    dead_letter_repository.mark_retrying.assert_called_once_with(
        dead_letter
    )

    workflow_execution_repository.create_retry_execution.assert_called_once_with(
        original_execution=original_execution
    )

    workflow_service.process_email.assert_called_once()

    process_call = workflow_service.process_email.call_args

    assert (
        process_call.kwargs["workflow_execution"]
        is retry_execution
    )

    dead_letter_repository.mark_resolved.assert_called_once_with(
        dead_letter,
        retry_execution_id=retry_execution.id,
    )

    dead_letter_repository.mark_retry_failed.assert_not_called()

    session.commit.assert_called()


def test_retry_execution_raises_lookup_error_when_execution_missing(
    service: FailureRecoveryService,
    workflow_execution_repository: MagicMock,
) -> None:
    workflow_execution_repository.get_by_execution_id.return_value = None

    with pytest.raises(
        LookupError,
        match="Workflow execution not found.",
    ):
        service.retry_execution("unknown-execution-id")


def test_retry_execution_rejects_non_failed_execution(
    service: FailureRecoveryService,
    workflow_execution_repository: MagicMock,
) -> None:
    execution = build_failed_execution()
    execution.status = WorkflowExecutionStatus.SUCCESS

    workflow_execution_repository.get_by_execution_id.return_value = (
        execution
    )

    with pytest.raises(
        ValueError,
        match="Workflow execution is not FAILED.",
    ):
        service.retry_execution(execution.execution_id)


def test_retry_execution_raises_lookup_error_when_dead_letter_missing(
    service: FailureRecoveryService,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
) -> None:
    execution = build_failed_execution()

    workflow_execution_repository.get_by_execution_id.return_value = (
        execution
    )

    dead_letter_repository.get_by_execution_id.return_value = None

    with pytest.raises(
        LookupError,
        match="Dead-letter record not found.",
    ):
        service.retry_execution(execution.execution_id)


def test_retry_execution_rejects_resolved_dead_letter(
    service: FailureRecoveryService,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
) -> None:
    execution = build_failed_execution()
    dead_letter = build_dead_letter_record()

    dead_letter.status = DeadLetterStatus.RESOLVED

    workflow_execution_repository.get_by_execution_id.return_value = (
        execution
    )

    dead_letter_repository.get_by_execution_id.return_value = (
        dead_letter
    )

    with pytest.raises(
        ValueError,
        match="Workflow execution has already been recovered.",
    ):
        service.retry_execution(execution.execution_id)


def test_retry_execution_rejects_retrying_dead_letter(
    service: FailureRecoveryService,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
) -> None:
    execution = build_failed_execution()
    dead_letter = build_dead_letter_record()

    dead_letter.status = DeadLetterStatus.RETRYING

    workflow_execution_repository.get_by_execution_id.return_value = (
        execution
    )

    dead_letter_repository.get_by_execution_id.return_value = (
        dead_letter
    )

    with pytest.raises(
        ValueError,
        match="Workflow execution retry is already in progress.",
    ):
        service.retry_execution(execution.execution_id)


def test_retry_execution_fails_when_email_metadata_missing(
    service: FailureRecoveryService,
    session: MagicMock,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
) -> None:
    execution = build_failed_execution()
    dead_letter = build_dead_letter_record()

    execution.execution_metadata = None

    workflow_execution_repository.get_by_execution_id.return_value = (
        execution
    )

    dead_letter_repository.get_by_execution_id.return_value = (
        dead_letter
    )

    with pytest.raises(
        ValueError,
        match="Original workflow email metadata is unavailable.",
    ):
        service.retry_execution(execution.execution_id)

    session.rollback.assert_called_once()


def test_retry_execution_failure_reopens_dead_letter(
    service: FailureRecoveryService,
    session: MagicMock,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
    workflow_service: MagicMock,
) -> None:
    original_execution = build_failed_execution()
    retry_execution = build_retry_execution()
    dead_letter = build_dead_letter_record()

    workflow_execution_repository.get_by_execution_id.return_value = (
        original_execution
    )

    dead_letter_repository.get_by_execution_id.return_value = (
        dead_letter
    )

    workflow_execution_repository.create_retry_execution.return_value = (
        retry_execution
    )

    workflow_service.process_email.side_effect = RuntimeError(
        "retry workflow failed"
    )

    with pytest.raises(
        RuntimeError,
        match="retry workflow failed",
    ):
        service.retry_execution(
            original_execution.execution_id
        )

    dead_letter_repository.mark_retrying.assert_called_once_with(
        dead_letter
    )

    dead_letter_repository.mark_retry_failed.assert_called_once_with(
        dead_letter,
        retry_execution_id=retry_execution.id,
    )

    dead_letter_repository.mark_resolved.assert_not_called()

    session.commit.assert_called()


def test_retry_execution_preserves_retry_lineage(
    service: FailureRecoveryService,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
    workflow_service: MagicMock,
) -> None:
    original_execution = build_failed_execution()
    retry_execution = build_retry_execution()
    dead_letter = build_dead_letter_record()

    workflow_execution_repository.get_by_execution_id.return_value = (
        original_execution
    )

    dead_letter_repository.get_by_execution_id.return_value = (
        dead_letter
    )

    workflow_execution_repository.create_retry_execution.return_value = (
        retry_execution
    )

    workflow_service.process_email.return_value = SimpleNamespace(
        ticket_id=20,
        execution_id=retry_execution.execution_id,
    )

    service.retry_execution(
        original_execution.execution_id
    )

    assert retry_execution.parent_execution_id == (
        original_execution.id
    )

    assert retry_execution.attempt_number == (
        original_execution.attempt_number + 1
    )


def test_retry_execution_reconstructs_email_from_metadata(
    service: FailureRecoveryService,
    workflow_execution_repository: MagicMock,
    dead_letter_repository: MagicMock,
    workflow_service: MagicMock,
) -> None:
    original_execution = build_failed_execution()
    retry_execution = build_retry_execution()
    dead_letter = build_dead_letter_record()

    workflow_execution_repository.get_by_execution_id.return_value = (
        original_execution
    )

    dead_letter_repository.get_by_execution_id.return_value = (
        dead_letter
    )

    workflow_execution_repository.create_retry_execution.return_value = (
        retry_execution
    )

    workflow_service.process_email.return_value = SimpleNamespace(
        ticket_id=20,
        execution_id=retry_execution.execution_id,
    )

    service.retry_execution(
        original_execution.execution_id
    )

    process_call = workflow_service.process_email.call_args

    email = process_call.args[0]

    assert email.message_id == original_execution.message_id
    assert email.sender_email == "customer@example.com"
    assert email.subject == "Unable to access account"
    assert email.body == "I cannot access my account."