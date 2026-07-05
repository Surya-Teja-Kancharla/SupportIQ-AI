from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import WorkflowExecutionStatus
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
            statement = select(WorkflowExecution).where(
                WorkflowExecution.message_id == message_id
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
            statement = select(WorkflowExecution).where(
                WorkflowExecution.ticket_id == ticket_id
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
        execution.current_stage = "WORKFLOW_COMPLETED"
        execution.completed_at = completed_at
        execution.duration_ms = duration_ms
        execution.failure_stage = None
        execution.error_type = None
        execution.error_message = None

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

        self._flush_mutation()

        return execution

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
