from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)
from app.schemas.monitoring_schema import (
    DatabaseHealthResponse,
    TicketPriorityMetric,
    TicketStatusMetric,
    WorkflowExecutionListResponse,
    WorkflowExecutionResponse,
    WorkflowMetricsResponse,
)


class MonitoringService:
    """Provides operational health, metrics, and execution queries."""

    def __init__(
        self,
        session: Session,
        workflow_execution_repository: (
            WorkflowExecutionRepository | None
        ) = None,
    ) -> None:
        self._session = session
        self._workflow_execution_repository = (
            workflow_execution_repository
            or WorkflowExecutionRepository(session)
        )

    def check_database_health(
        self,
    ) -> DatabaseHealthResponse:
        try:
            self._session.execute(text("SELECT 1"))

            return DatabaseHealthResponse(
                status="healthy",
                database="reachable",
            )

        except SQLAlchemyError:
            return DatabaseHealthResponse(
                status="unhealthy",
                database="unreachable",
            )

    def get_metrics(
        self,
    ) -> WorkflowMetricsResponse:
        successful_workflows = (
            self._workflow_execution_repository
            .count_successful_executions()
        )

        failed_workflows = (
            self._workflow_execution_repository
            .count_failed_executions()
        )

        average_processing_time_ms = (
            self._workflow_execution_repository
            .calculate_average_duration_ms()
        )

        return WorkflowMetricsResponse(
            successful_workflows=successful_workflows,
            failed_workflows=failed_workflows,
            average_processing_time_ms=(
                average_processing_time_ms
            ),
            tickets_by_priority=(
                self._get_ticket_priority_metrics()
            ),
            tickets_by_status=(
                self._get_ticket_status_metrics()
            ),
        )

    def list_workflow_executions(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> WorkflowExecutionListResponse:
        offset = (page - 1) * page_size

        executions = (
            self._workflow_execution_repository.list_executions(
                offset=offset,
                limit=page_size,
                status=status,
            )
        )

        total = (
            self._workflow_execution_repository.count_executions(
                status=status,
            )
        )

        return WorkflowExecutionListResponse(
            items=[
                WorkflowExecutionResponse.model_validate(
                    execution
                )
                for execution in executions
            ],
            page=page,
            page_size=page_size,
            total=total,
        )

    def get_workflow_execution(
        self,
        execution_id: str,
    ) -> WorkflowExecutionResponse | None:
        execution = (
            self._workflow_execution_repository
            .get_by_execution_id(execution_id)
        )

        if execution is None:
            return None

        return WorkflowExecutionResponse.model_validate(
            execution
        )

    def _get_ticket_priority_metrics(
        self,
    ) -> list[TicketPriorityMetric]:
        statement = (
            select(
                Ticket.priority,
                func.count(Ticket.id),
            )
            .group_by(Ticket.priority)
            .order_by(Ticket.priority)
        )

        rows = self._session.execute(statement).all()

        return [
            TicketPriorityMetric(
                priority=priority,
                count=int(count),
            )
            for priority, count in rows
        ]

    def _get_ticket_status_metrics(
        self,
    ) -> list[TicketStatusMetric]:
        statement = (
            select(
                Ticket.status,
                func.count(Ticket.id),
            )
            .group_by(Ticket.status)
            .order_by(Ticket.status)
        )

        rows = self._session.execute(statement).all()

        return [
            TicketStatusMetric(
                status=status,
                count=int(count),
            )
            for status, count in rows
        ]
