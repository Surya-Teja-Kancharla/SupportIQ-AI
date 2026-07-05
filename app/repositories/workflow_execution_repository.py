from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

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
