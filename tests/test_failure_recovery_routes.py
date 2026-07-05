from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_db
from app.schemas.failure_recovery_schema import WorkflowRetryResponse
from main import app


@pytest.fixture
def db_session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(
    db_session: MagicMock,
) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def build_retry_response() -> WorkflowRetryResponse:
    return WorkflowRetryResponse(
        original_execution_id=10,
        retry_execution_id=11,
        attempt_number=2,
        status="SUCCESS",
    )


def test_retry_workflow_execution_success(
    client: TestClient,
    db_session: MagicMock,
) -> None:
    response_model = build_retry_response()

    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.return_value = response_model

        response = client.post(
            "/workflow-executions/"
            "failed-execution-id/retry"
        )

    assert response.status_code == 200

    assert response.json() == {
        "original_execution_id": 10,
        "retry_execution_id": 11,
        "attempt_number": 2,
        "status": "SUCCESS",
    }

    service_class.assert_called_once_with(db_session)

    service.retry_execution.assert_called_once_with(
        "failed-execution-id"
    )


def test_retry_workflow_execution_returns_404(
    client: TestClient,
) -> None:
    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.side_effect = LookupError(
            "Workflow execution not found."
        )

        response = client.post(
            "/workflow-executions/"
            "unknown-execution-id/retry"
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Workflow execution not found.",
    }


def test_retry_workflow_execution_returns_404_when_dead_letter_missing(
    client: TestClient,
) -> None:
    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.side_effect = LookupError(
            "Dead-letter record not found."
        )

        response = client.post(
            "/workflow-executions/"
            "failed-execution-id/retry"
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Dead-letter record not found.",
    }


def test_retry_workflow_execution_returns_409_for_non_failed_execution(
    client: TestClient,
) -> None:
    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.side_effect = ValueError(
            "Workflow execution is not FAILED."
        )

        response = client.post(
            "/workflow-executions/"
            "successful-execution-id/retry"
        )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "Workflow execution is not FAILED.",
    }


def test_retry_workflow_execution_returns_409_when_already_recovered(
    client: TestClient,
) -> None:
    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.side_effect = ValueError(
            "Workflow execution has already been recovered."
        )

        response = client.post(
            "/workflow-executions/"
            "failed-execution-id/retry"
        )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Workflow execution has already been recovered."
        ),
    }


def test_retry_workflow_execution_returns_409_when_retry_in_progress(
    client: TestClient,
) -> None:
    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.side_effect = ValueError(
            "Workflow execution retry is already in progress."
        )

        response = client.post(
            "/workflow-executions/"
            "failed-execution-id/retry"
        )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Workflow execution retry is already in progress."
        ),
    }


def test_retry_workflow_execution_returns_500(
    client: TestClient,
) -> None:
    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.side_effect = RuntimeError(
            "database unavailable"
        )

        response = client.post(
            "/workflow-executions/"
            "failed-execution-id/retry"
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Retry execution failed.",
    }

    assert "database unavailable" not in response.text


def test_retry_route_does_not_expose_internal_exception_message(
    client: TestClient,
) -> None:
    sensitive_message = (
        "api_key=secret-value database unavailable"
    )

    with patch(
        "app.api.failure_recovery_routes."
        "FailureRecoveryService"
    ) as service_class:
        service = service_class.return_value

        service.retry_execution.side_effect = RuntimeError(
            sensitive_message
        )

        response = client.post(
            "/workflow-executions/"
            "failed-execution-id/retry"
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Retry execution failed.",
    }

    assert sensitive_message not in response.text
