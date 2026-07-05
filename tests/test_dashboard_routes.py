from datetime import datetime, timezone
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dashboard_routes import router
from app.api.dependencies import get_dashboard_service
from app.schemas.dashboard_schema import (
    TicketDetailView,
    TicketListItem,
    TicketListResult,
    WorkflowExecutionView,
)


NOW = datetime.now(timezone.utc)


def build_app(service: Mock) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_dashboard_service] = lambda: service
    app.include_router(router)
    return app


def build_list_result() -> TicketListResult:
    return TicketListResult(
        tickets=(
            TicketListItem(
                id=101,
                ticket_number="SUP-20260705-DASH001",
                email_subject="Production outage",
                category="Technical Support",
                priority="Critical",
                status="open",
                assigned_team="Technical Support",
                confidence_score=0.97,
                received_at=NOW,
            ),
        ),
        total=1,
        limit=50,
        offset=0,
    )


def build_detail_result() -> TicketDetailView:
    return TicketDetailView(
        id=101,
        ticket_number="SUP-20260705-DASH001",
        customer_name="Customer",
        company="Example Corp",
        sender_email="customer@example.com",
        email_subject="Production outage",
        original_email_body="Production service unavailable.",
        issue_summary="Production outage",
        detailed_description="Production service unavailable.",
        category="Technical Support",
        priority="Critical",
        sentiment="Negative",
        product_or_service="Production Service",
        suggested_department="Technical Support",
        assigned_team="Technical Support",
        confidence_score=0.97,
        status="open",
        received_at=NOW,
        created_at=NOW,
        updated_at=NOW,
        priority_reason=(
            "Matched production outage rule for Critical priority"
        ),
        suggested_reply="We are investigating the outage.",
        attachments=(),
        audit_events=(),
        workflow_execution=WorkflowExecutionView(
            status="completed",
            failure_stage=None,
            error_type=None,
            error_message=None,
            started_at=NOW,
            completed_at=NOW,
        ),
    )


def test_ticket_list_route_returns_html():
    service = Mock()
    service.list_tickets.return_value = build_list_result()

    client = TestClient(build_app(service))

    response = client.get("/dashboard/tickets")

    assert response.status_code == 200
    assert "SupportIQ Agent Dashboard" in response.text
    assert "SUP-20260705-DASH001" in response.text


def test_ticket_list_route_forwards_filters():
    service = Mock()
    service.list_tickets.return_value = TicketListResult(
        tickets=(),
        total=0,
        limit=25,
        offset=10,
    )

    client = TestClient(build_app(service))

    response = client.get(
        "/dashboard/tickets",
        params={
            "status": "open",
            "priority": "Critical",
            "category": "Technical Support",
            "assigned_team": "Technical Support",
            "limit": 25,
            "offset": 10,
        },
    )

    assert response.status_code == 200

    filters = service.list_tickets.call_args.args[0]

    assert filters.status == "open"
    assert filters.priority == "Critical"
    assert filters.category == "Technical Support"
    assert filters.assigned_team == "Technical Support"
    assert filters.limit == 25
    assert filters.offset == 10


def test_ticket_detail_route_returns_html():
    service = Mock()
    service.get_ticket_detail.return_value = build_detail_result()

    client = TestClient(build_app(service))

    response = client.get("/dashboard/tickets/101")

    assert response.status_code == 200
    assert "SUP-20260705-DASH001" in response.text
    assert "AI Decision Context" in response.text
    assert "We are investigating the outage." in response.text
    assert "Workflow Monitoring" in response.text


def test_ticket_detail_route_returns_404():
    service = Mock()
    service.get_ticket_detail.return_value = None

    client = TestClient(build_app(service))

    response = client.get("/dashboard/tickets/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found."
    }


def test_ticket_list_route_rejects_invalid_pagination():
    service = Mock()

    client = TestClient(build_app(service))

    response = client.get(
        "/dashboard/tickets",
        params={"limit": 0},
    )

    assert response.status_code == 422
    service.list_tickets.assert_not_called()
