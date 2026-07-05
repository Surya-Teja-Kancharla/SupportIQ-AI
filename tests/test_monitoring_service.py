from datetime import datetime, timezone
from unittest.mock import MagicMock

from sqlalchemy.exc import OperationalError

from app.models.workflow_execution import WorkflowExecution
from app.services.monitoring_service import MonitoringService


def create_execution(
    *,
    execution_id: str = (
        "11111111-1111-4111-8111-111111111111"
    ),
    message_id: str = "<monitoring@example.com>",
    ticket_id: int | None = 101,
    status: str = "SUCCESS",
    current_stage: str = "WORKFLOW_COMPLETED",
    retry_count: int = 0,
    duration_ms: int | None = 250,
) -> WorkflowExecution:
    now = datetime.now(timezone.utc)

    return WorkflowExecution(
        execution_id=execution_id,
        message_id=message_id,
        ticket_id=ticket_id,
        started_at=now,
        completed_at=now,
        duration_ms=duration_ms,
        status=status,
        current_stage=current_stage,
        retry_count=retry_count,
        failure_stage=None,
        error_type=None,
        error_message=None,
        execution_metadata=None,
    )


def test_database_health_success():
    session = MagicMock()
    repository = MagicMock()

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.check_database_health()

    assert result.status == "healthy"
    assert result.database == "reachable"

    session.execute.assert_called_once()


def test_database_health_failure():
    session = MagicMock()
    repository = MagicMock()

    session.execute.side_effect = OperationalError(
        "SELECT 1",
        {},
        Exception("Database unavailable"),
    )

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.check_database_health()

    assert result.status == "unhealthy"
    assert result.database == "unreachable"


def test_workflow_metrics():
    session = MagicMock()
    repository = MagicMock()

    repository.count_successful_executions.return_value = 12
    repository.count_failed_executions.return_value = 3
    repository.calculate_average_duration_ms.return_value = 275.5

    session.execute.side_effect = [
        MagicMock(all=lambda: []),
        MagicMock(all=lambda: []),
    ]

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.get_metrics()

    assert result.successful_workflows == 12
    assert result.failed_workflows == 3
    assert result.average_processing_time_ms == 275.5


def test_priority_metrics():
    session = MagicMock()
    repository = MagicMock()

    repository.count_successful_executions.return_value = 0
    repository.count_failed_executions.return_value = 0
    repository.calculate_average_duration_ms.return_value = 0.0

    priority_result = MagicMock()
    priority_result.all.return_value = [
        ("CRITICAL", 2),
        ("HIGH", 5),
        ("LOW", 4),
        ("MEDIUM", 7),
    ]

    status_result = MagicMock()
    status_result.all.return_value = []

    session.execute.side_effect = [
        priority_result,
        status_result,
    ]

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.get_metrics()

    metrics = {
        item.priority: item.count
        for item in result.tickets_by_priority
    }

    assert metrics == {
        "CRITICAL": 2,
        "HIGH": 5,
        "LOW": 4,
        "MEDIUM": 7,
    }


def test_status_metrics():
    session = MagicMock()
    repository = MagicMock()

    repository.count_successful_executions.return_value = 0
    repository.count_failed_executions.return_value = 0
    repository.calculate_average_duration_ms.return_value = 0.0

    priority_result = MagicMock()
    priority_result.all.return_value = []

    status_result = MagicMock()
    status_result.all.return_value = [
        ("OPEN", 5),
        ("IN_PROGRESS", 4),
        ("RESOLVED", 8),
        ("CLOSED", 3),
    ]

    session.execute.side_effect = [
        priority_result,
        status_result,
    ]

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.get_metrics()

    metrics = {
        item.status: item.count
        for item in result.tickets_by_status
    }

    assert metrics == {
        "OPEN": 5,
        "IN_PROGRESS": 4,
        "RESOLVED": 8,
        "CLOSED": 3,
    }


def test_execution_pagination():
    session = MagicMock()
    repository = MagicMock()

    executions = [
        create_execution(
            execution_id=(
                "11111111-1111-4111-8111-111111111111"
            ),
        ),
        create_execution(
            execution_id=(
                "22222222-2222-4222-8222-222222222222"
            ),
            message_id="<second@example.com>",
            ticket_id=102,
        ),
    ]

    repository.list_executions.return_value = executions
    repository.count_executions.return_value = 12

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.list_workflow_executions(
        page=2,
        page_size=5,
    )

    repository.list_executions.assert_called_once_with(
        offset=5,
        limit=5,
        status=None,
    )

    repository.count_executions.assert_called_once_with(
        status=None,
    )

    assert result.page == 2
    assert result.page_size == 5
    assert result.total == 12
    assert len(result.items) == 2


def test_execution_filtering():
    session = MagicMock()
    repository = MagicMock()

    failed_execution = create_execution(
        status="FAILED",
        current_stage="AI_ANALYSIS_STARTED",
    )
    failed_execution.error_type = "RuntimeError"
    failed_execution.error_message = "AI provider unavailable"

    repository.list_executions.return_value = [
        failed_execution
    ]
    repository.count_executions.return_value = 1

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.list_workflow_executions(
        page=1,
        page_size=20,
        status="FAILED",
    )

    repository.list_executions.assert_called_once_with(
        offset=0,
        limit=20,
        status="FAILED",
    )

    repository.count_executions.assert_called_once_with(
        status="FAILED",
    )

    assert result.total == 1
    assert result.items[0].status == "FAILED"


def test_execution_detail_found():
    session = MagicMock()
    repository = MagicMock()

    execution = create_execution()

    repository.get_by_execution_id.return_value = execution

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.get_workflow_execution(
        execution.execution_id
    )

    assert result is not None
    assert result.execution_id == execution.execution_id
    assert result.message_id == execution.message_id

    repository.get_by_execution_id.assert_called_once_with(
        execution.execution_id
    )


def test_execution_detail_missing():
    session = MagicMock()
    repository = MagicMock()

    repository.get_by_execution_id.return_value = None

    service = MonitoringService(
        session,
        workflow_execution_repository=repository,
    )

    result = service.get_workflow_execution(
        "99999999-9999-4999-8999-999999999999"
    )

    assert result is None
