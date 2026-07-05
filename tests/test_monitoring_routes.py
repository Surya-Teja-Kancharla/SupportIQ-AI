from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.monitoring_routes import (
    get_monitoring_service,
    router,
)
from app.schemas.monitoring_schema import (
    DatabaseHealthResponse,
    WorkflowExecutionListResponse,
    WorkflowExecutionResponse,
    WorkflowMetricsResponse,
)


@pytest.fixture
def mock_monitoring_service():
    return MagicMock()


@pytest.fixture
def app(mock_monitoring_service):
    test_app = FastAPI()

    test_app.include_router(router)

    test_app.dependency_overrides[
        get_monitoring_service
    ] = lambda: mock_monitoring_service

    yield test_app

    test_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app)


def create_execution_response(
    *,
    execution_id: str = (
        "11111111-1111-4111-8111-111111111111"
    ),
    status: str = "SUCCESS",
) -> WorkflowExecutionResponse:
    now = datetime.now(timezone.utc)

    return WorkflowExecutionResponse(
        execution_id=execution_id,
        message_id="<route-test@example.com>",
        ticket_id=101,
        started_at=now,
        completed_at=now,
        duration_ms=250,
        status=status,
        current_stage="WORKFLOW_COMPLETED",
        retry_count=0,
        error_type=None,
        error_message=None,
    )


def test_get_health_returns_200(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_get_database_health_returns_200(
    client,
    mock_monitoring_service,
):
    mock_monitoring_service.check_database_health.return_value = (
        DatabaseHealthResponse(
            status="healthy",
            database="reachable",
        )
    )

    response = client.get("/health/database")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "database": "reachable",
    }


def test_get_database_health_returns_503(
    client,
    mock_monitoring_service,
):
    mock_monitoring_service.check_database_health.return_value = (
        DatabaseHealthResponse(
            status="unhealthy",
            database="unreachable",
        )
    )

    response = client.get("/health/database")

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Database is unavailable.",
    }


def test_get_metrics_returns_200(
    client,
    mock_monitoring_service,
):
    mock_monitoring_service.get_metrics.return_value = (
        WorkflowMetricsResponse(
            successful_workflows=10,
            failed_workflows=2,
            average_processing_time_ms=325.5,
            tickets_by_priority=[],
            tickets_by_status=[],
        )
    )

    response = client.get("/metrics")

    assert response.status_code == 200

    body = response.json()

    assert body["successful_workflows"] == 10
    assert body["failed_workflows"] == 2
    assert body["average_processing_time_ms"] == 325.5


def test_list_workflow_executions_returns_200(
    client,
    mock_monitoring_service,
):
    execution = create_execution_response()

    mock_monitoring_service.list_workflow_executions.return_value = (
        WorkflowExecutionListResponse(
            items=[execution],
            page=1,
            page_size=20,
            total=1,
        )
    )

    response = client.get("/workflow-executions")

    assert response.status_code == 200

    body = response.json()

    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_pagination_parameters_are_forwarded(
    client,
    mock_monitoring_service,
):
    mock_monitoring_service.list_workflow_executions.return_value = (
        WorkflowExecutionListResponse(
            items=[],
            page=3,
            page_size=10,
            total=0,
        )
    )

    response = client.get(
        "/workflow-executions?page=3&page_size=10"
    )

    assert response.status_code == 200

    mock_monitoring_service.list_workflow_executions.assert_called_once_with(
        page=3,
        page_size=10,
        status=None,
    )


def test_status_filter_is_forwarded(
    client,
    mock_monitoring_service,
):
    mock_monitoring_service.list_workflow_executions.return_value = (
        WorkflowExecutionListResponse(
            items=[],
            page=1,
            page_size=20,
            total=0,
        )
    )

    response = client.get(
        "/workflow-executions?status=FAILED"
    )

    assert response.status_code == 200

    mock_monitoring_service.list_workflow_executions.assert_called_once_with(
        page=1,
        page_size=20,
        status="FAILED",
    )


def test_invalid_status_returns_422(
    client,
    mock_monitoring_service,
):
    response = client.get(
        "/workflow-executions?status=INVALID"
    )

    assert response.status_code == 422

    mock_monitoring_service.list_workflow_executions.assert_not_called()


def test_invalid_page_returns_422(
    client,
    mock_monitoring_service,
):
    response = client.get(
        "/workflow-executions?page=0"
    )

    assert response.status_code == 422

    mock_monitoring_service.list_workflow_executions.assert_not_called()


def test_invalid_page_size_returns_422(
    client,
    mock_monitoring_service,
):
    response = client.get(
        "/workflow-executions?page_size=101"
    )

    assert response.status_code == 422

    mock_monitoring_service.list_workflow_executions.assert_not_called()


def test_execution_detail_returns_200(
    client,
    mock_monitoring_service,
):
    execution = create_execution_response()

    mock_monitoring_service.get_workflow_execution.return_value = (
        execution
    )

    response = client.get(
        f"/workflow-executions/{execution.execution_id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["execution_id"] == execution.execution_id
    assert body["status"] == "SUCCESS"

    mock_monitoring_service.get_workflow_execution.assert_called_once_with(
        execution.execution_id
    )


def test_unknown_execution_returns_404(
    client,
    mock_monitoring_service,
):
    execution_id = (
        "99999999-9999-4999-8999-999999999999"
    )

    mock_monitoring_service.get_workflow_execution.return_value = None

    response = client.get(
        f"/workflow-executions/{execution_id}"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Workflow execution not found.",
    }

    mock_monitoring_service.get_workflow_execution.assert_called_once_with(
        execution_id
    )
