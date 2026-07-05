from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import (
    WorkflowExecutionStatus,
    WorkflowStage,
)
from app.core.exceptions import (
    DuplicateWorkflowExecutionError,
    RepositoryError,
)
from app.models.workflow_execution import WorkflowExecution


class WorkflowExecutionRepository:
    """Persistence operations for workflow executions."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        try:
            self._session.add(execution)
            self._session.flush()

            return execution

        except IntegrityError as exc:
            raise DuplicateWorkflowExecutionError(
                "A workflow execution already exists "
                "for this message."
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution persistence failed."
            ) from exc

    def get_by_execution_id(
        self,
        execution_id: str,
    ) -> WorkflowExecution | None:
        try:
            statement = select(WorkflowExecution).where(
                WorkflowExecution.execution_id == execution_id
            )

            return self._session.scalar(statement)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution lookup failed."
            ) from exc

    def get_by_message_id(
        self,
        message_id: str,
    ) -> WorkflowExecution | None:
        try:
            statement = (
                select(WorkflowExecution)
                .where(
                    WorkflowExecution.message_id == message_id
                )
                .order_by(
                    WorkflowExecution.attempt_number.desc(),
                    WorkflowExecution.id.desc(),
                )
                .limit(1)
            )

            return self._session.scalar(statement)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution lookup failed."
            ) from exc

    def get_by_ticket_id(
        self,
        ticket_id: int,
    ) -> WorkflowExecution | None:
        try:
            statement = (
                select(WorkflowExecution)
                .where(
                    WorkflowExecution.ticket_id == ticket_id
                )
                .order_by(
                    WorkflowExecution.attempt_number.desc(),
                    WorkflowExecution.id.desc(),
                )
                .limit(1)
            )

            return self._session.scalar(statement)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution lookup failed."
            ) from exc

    def list_executions(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        status: str | None = None,
    ) -> list[WorkflowExecution]:
        try:
            statement = select(WorkflowExecution)

            if status is not None:
                statement = statement.where(
                    WorkflowExecution.status == status
                )

            statement = (
                statement
                .order_by(
                    WorkflowExecution.started_at.desc(),
                    WorkflowExecution.id.desc(),
                )
                .offset(offset)
                .limit(limit)
            )

            return list(
                self._session.scalars(statement).all()
            )

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution listing failed."
            ) from exc

    def count_executions(
        self,
        *,
        status: str | None = None,
    ) -> int:
        try:
            statement = select(
                func.count(WorkflowExecution.id)
            )

            if status is not None:
                statement = statement.where(
                    WorkflowExecution.status == status
                )

            return int(
                self._session.scalar(statement) or 0
            )

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution count failed."
            ) from exc

    def count_successful_executions(self) -> int:
        return self.count_executions(
            status=WorkflowExecutionStatus.SUCCESS,
        )

    def count_failed_executions(self) -> int:
        return self.count_executions(
            status=WorkflowExecutionStatus.FAILED,
        )

    def calculate_average_duration_ms(self) -> float:
        try:
            statement = select(
                func.avg(WorkflowExecution.duration_ms)
            ).where(
                WorkflowExecution.duration_ms.is_not(None)
            )

            value = self._session.scalar(statement)

            return float(value or 0.0)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution duration aggregation failed."
            ) from exc

    def mark_stage(
        self,
        execution: WorkflowExecution,
        *,
        stage: str,
    ) -> WorkflowExecution:
        execution.current_stage = stage

        self._flush_mutation()

        return execution

    def mark_success(
        self,
        execution: WorkflowExecution,
        *,
        completed_at,
        duration_ms: int,
    ) -> WorkflowExecution:
        execution.status = WorkflowExecutionStatus.SUCCESS
        execution.current_stage = (
            WorkflowStage.WORKFLOW_COMPLETED
        )
        execution.completed_at = completed_at
        execution.duration_ms = duration_ms

        execution.failure_stage = None
        execution.error_type = None
        execution.error_message = None
        execution.retry_exhausted = False
        execution.failed_at = None

        self._flush_mutation()

        return execution

    def mark_failure(
        self,
        execution: WorkflowExecution,
        *,
        completed_at,
        duration_ms: int,
        error_type: str,
        error_message: str,
    ) -> WorkflowExecution:
        execution.status = WorkflowExecutionStatus.FAILED
        execution.completed_at = completed_at
        execution.duration_ms = duration_ms
        execution.failure_stage = execution.current_stage
        execution.error_type = error_type
        execution.error_message = error_message
        execution.failed_at = completed_at

        self._flush_mutation()

        return execution

    def mark_failed(
        self,
        execution: WorkflowExecution,
        *,
        failed_stage: str,
        exception_type: str,
        sanitized_error_message: str,
        retry_count: int,
        retry_exhausted: bool,
    ) -> WorkflowExecution:
        failed_at = datetime.now(timezone.utc)

        duration_ms = max(
            0,
            int(
                (
                    failed_at - execution.started_at
                ).total_seconds()
                * 1000
            ),
        )

        execution.status = WorkflowExecutionStatus.FAILED
        execution.current_stage = failed_stage
        execution.failure_stage = failed_stage

        execution.error_type = exception_type
        execution.error_message = sanitized_error_message

        execution.retry_count = retry_count
        execution.retry_exhausted = retry_exhausted

        execution.failed_at = failed_at
        execution.completed_at = failed_at
        execution.duration_ms = duration_ms

        self._flush_mutation()

        return execution

    def create_retry_execution(
        self,
        *,
        original_execution: WorkflowExecution,
    ) -> WorkflowExecution:
        retry_execution = WorkflowExecution(
            execution_id=str(uuid4()),
            message_id=original_execution.message_id,
            ticket_id=original_execution.ticket_id,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            duration_ms=None,
            status=WorkflowExecutionStatus.RUNNING,
            current_stage=WorkflowStage.EMAIL_FETCHED,
            retry_count=0,
            failure_stage=None,
            error_type=None,
            error_message=None,
            retry_exhausted=False,
            failed_at=None,
            parent_execution_id=original_execution.id,
            attempt_number=(
                original_execution.attempt_number + 1
            ),
            execution_metadata=None,
        )

        try:
            self._session.add(retry_execution)
            self._session.flush()

            return retry_execution

        except IntegrityError as exc:
            raise DuplicateWorkflowExecutionError(
                "Unable to create retry workflow execution."
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Retry workflow-execution persistence failed."
            ) from exc

    def increment_retry_count(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        execution.retry_count += 1

        self._flush_mutation()

        return execution

    def _flush_mutation(self) -> None:
        try:
            self._session.flush()

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Workflow-execution update failed."
            ) from exc
