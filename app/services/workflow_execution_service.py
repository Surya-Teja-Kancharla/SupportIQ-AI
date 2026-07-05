import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.constants import (
    LogEvent,
    WorkflowExecutionStatus,
    WorkflowStage,
)
from app.core.logging import get_logger, log_event
from app.models.workflow_execution import WorkflowExecution
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)


logger = get_logger(__name__)


class WorkflowExecutionService:
    """Coordinates workflow execution telemetry mutations."""

    def __init__(
        self,
        repository: WorkflowExecutionRepository,
        *,
        session: Session | None = None,
    ) -> None:
        self._repository = repository
        self._session = session

    def start_execution(
        self,
        *,
        message_id: str,
        stage: WorkflowStage = WorkflowStage.EMAIL_FETCHED,
    ) -> WorkflowExecution:
        started_at = datetime.now(timezone.utc)

        execution = WorkflowExecution(
            execution_id=str(uuid4()),
            message_id=message_id,
            ticket_id=None,
            started_at=started_at,
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

        self._repository.add(execution)

        log_event(
            logger,
            logging.INFO,
            LogEvent.WORKFLOW_EXECUTION_STARTED,
            "Workflow execution tracking started.",
            execution_id=execution.execution_id,
            message_id=message_id,
            current_stage=execution.current_stage,
        )

        return execution

    def advance_stage(
        self,
        execution: WorkflowExecution,
        *,
        stage: WorkflowStage,
    ) -> WorkflowExecution:
        self._repository.mark_stage(
            execution,
            stage=stage,
        )

        log_event(
            logger,
            logging.INFO,
            LogEvent.WORKFLOW_STAGE_ADVANCED,
            "Workflow execution stage advanced.",
            execution_id=execution.execution_id,
            message_id=execution.message_id,
            current_stage=execution.current_stage,
        )

        return execution

    def record_retry(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        self._repository.increment_retry_count(execution)

        log_event(
            logger,
            logging.WARNING,
            LogEvent.WORKFLOW_RETRY_RECORDED,
            "Workflow execution retry recorded.",
            execution_id=execution.execution_id,
            message_id=execution.message_id,
            retry_count=execution.retry_count,
        )

        return execution

    def attach_ticket(
        self,
        execution: WorkflowExecution,
        *,
        ticket_id: int,
    ) -> WorkflowExecution:
        execution.ticket_id = ticket_id

        self._repository.mark_stage(
            execution,
            stage=WorkflowStage.TICKET_CREATED,
        )

        return execution

    def complete_execution(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        completed_at = datetime.now(timezone.utc)

        duration_ms = self.calculate_duration_ms(
            execution.started_at,
            completed_at,
        )

        self._repository.mark_success(
            execution,
            completed_at=completed_at,
            duration_ms=duration_ms,
        )

        log_event(
            logger,
            logging.INFO,
            LogEvent.WORKFLOW_EXECUTION_SUCCEEDED,
            "Workflow execution completed successfully.",
            execution_id=execution.execution_id,
            message_id=execution.message_id,
            ticket_id=execution.ticket_id,
            duration_ms=duration_ms,
        )

        return execution

    def fail_execution(
        self,
        execution: WorkflowExecution,
        *,
        error: Exception,
    ) -> WorkflowExecution:
        completed_at = datetime.now(timezone.utc)

        duration_ms = self.calculate_duration_ms(
            execution.started_at,
            completed_at,
        )

        self._repository.mark_failure(
            execution,
            completed_at=completed_at,
            duration_ms=duration_ms,
            error_type=type(error).__name__,
            error_message=str(error),
        )

        log_event(
            logger,
            logging.ERROR,
            LogEvent.WORKFLOW_EXECUTION_FAILED,
            "Workflow execution failed.",
            execution_id=execution.execution_id,
            message_id=execution.message_id,
            ticket_id=execution.ticket_id,
            current_stage=execution.current_stage,
            error_type=execution.error_type,
            duration_ms=duration_ms,
        )

        return execution

    def get_execution(
        self,
        execution_id: str,
    ) -> WorkflowExecution | None:
        return self._repository.get_by_execution_id(
            execution_id
        )


    def get_by_message_id(
        self,
        message_id: str,
    ) -> WorkflowExecution | None:
        return self._repository.get_by_message_id(
            message_id
        )

    @staticmethod
    def calculate_duration_ms(
        started_at: datetime,
        completed_at: datetime,
    ) -> int:
        elapsed = completed_at - started_at

        return max(
            0,
            int(elapsed.total_seconds() * 1000),
        )
