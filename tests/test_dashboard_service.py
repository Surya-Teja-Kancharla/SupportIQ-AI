from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from app.schemas.dashboard_schema import TicketFilters
from app.services.dashboard_service import DashboardService


NOW = datetime.now(timezone.utc)


def build_ticket(
    *,
    ticket_id: int = 101,
    ticket_number: str = "SUP-20260705-DASH001",
):
    return SimpleNamespace(
        id=ticket_id,
        ticket_number=ticket_number,
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
        priority_reason=(
            "Matched 'production outage' business rule "
            "for Critical priority"
        ),
        suggested_reply="We are investigating the outage.",
        received_at=NOW,
        created_at=NOW,
        updated_at=NOW,
    )


def build_service():
    ticket_repository = Mock()
    attachment_repository = Mock()
    audit_repository = Mock()
    workflow_execution_repository = Mock()

    service = DashboardService(
        ticket_repository=ticket_repository,
        attachment_repository=attachment_repository,
        audit_repository=audit_repository,
        workflow_execution_repository=(
            workflow_execution_repository
        ),
    )

    return SimpleNamespace(
        service=service,
        ticket_repository=ticket_repository,
        attachment_repository=attachment_repository,
        audit_repository=audit_repository,
        workflow_execution_repository=(
            workflow_execution_repository
        ),
    )


def test_list_tickets_returns_dashboard_result():
    context = build_service()

    context.ticket_repository.list_tickets.return_value = [
        build_ticket()
    ]
    context.ticket_repository.count_tickets.return_value = 1

    result = context.service.list_tickets(TicketFilters())

    assert result.total == 1
    assert result.limit == 50
    assert result.offset == 0
    assert len(result.tickets) == 1
    assert result.tickets[0].ticket_number == (
        "SUP-20260705-DASH001"
    )


def test_list_tickets_forwards_all_filters():
    context = build_service()

    context.ticket_repository.list_tickets.return_value = []
    context.ticket_repository.count_tickets.return_value = 0

    filters = TicketFilters(
        status="open",
        priority="Critical",
        category="Technical Support",
        assigned_team="Technical Support",
        limit=25,
        offset=10,
    )

    context.service.list_tickets(filters)

    context.ticket_repository.list_tickets.assert_called_once_with(
        status="open",
        priority="Critical",
        category="Technical Support",
        assigned_team="Technical Support",
        limit=25,
        offset=10,
    )

    context.ticket_repository.count_tickets.assert_called_once_with(
        status="open",
        priority="Critical",
        category="Technical Support",
        assigned_team="Technical Support",
    )


def test_list_tickets_returns_empty_result():
    context = build_service()

    context.ticket_repository.list_tickets.return_value = []
    context.ticket_repository.count_tickets.return_value = 0

    result = context.service.list_tickets(TicketFilters())

    assert result.tickets == ()
    assert result.total == 0


def test_get_ticket_detail_returns_none_for_unknown_ticket():
    context = build_service()

    context.ticket_repository.get_by_id.return_value = None

    result = context.service.get_ticket_detail(999)

    assert result is None

    context.attachment_repository.list_by_ticket_id.assert_not_called()
    context.audit_repository.list_by_ticket_id.assert_not_called()
    (
        context.workflow_execution_repository
        .get_by_ticket_id.assert_not_called()
    )


def test_get_ticket_detail_returns_complete_dashboard_view():
    context = build_service()

    ticket = build_ticket()

    attachment = SimpleNamespace(
        id=1,
        original_filename="error.png",
        content_type="image/png",
        file_size=1024,
    )

    audit_event = SimpleNamespace(
        id=1,
        action="ticket_created",
        field_name=None,
        old_value=None,
        new_value=None,
        changed_by="system",
        created_at=NOW,
    )

    workflow_execution = SimpleNamespace(
        status="completed",
        failure_stage=None,
        error_type=None,
        error_message=None,
        started_at=NOW,
        completed_at=NOW,
    )

    context.ticket_repository.get_by_id.return_value = ticket
    context.attachment_repository.list_by_ticket_id.return_value = [
        attachment
    ]
    context.audit_repository.list_by_ticket_id.return_value = [
        audit_event
    ]
    (
        context.workflow_execution_repository
        .get_by_ticket_id.return_value
    ) = workflow_execution

    result = context.service.get_ticket_detail(101)

    assert result is not None
    assert result.ticket_number == "SUP-20260705-DASH001"
    assert result.confidence_score == 0.97
    assert result.priority_reason == (
        "Matched 'production outage' business rule "
        "for Critical priority"
    )
    assert result.suggested_reply == (
        "We are investigating the outage."
    )

    assert len(result.attachments) == 1
    assert result.attachments[0].original_filename == "error.png"

    assert len(result.audit_events) == 1
    assert result.audit_events[0].action == "ticket_created"

    assert result.workflow_execution is not None
    assert result.workflow_execution.status == "completed"


def test_get_ticket_detail_supports_missing_workflow_execution():
    context = build_service()

    context.ticket_repository.get_by_id.return_value = build_ticket()
    context.attachment_repository.list_by_ticket_id.return_value = []
    context.audit_repository.list_by_ticket_id.return_value = []
    (
        context.workflow_execution_repository
        .get_by_ticket_id.return_value
    ) = None

    result = context.service.get_ticket_detail(101)

    assert result is not None
    assert result.workflow_execution is None


def test_get_ticket_detail_requests_related_records_for_ticket():
    context = build_service()

    context.ticket_repository.get_by_id.return_value = build_ticket()
    context.attachment_repository.list_by_ticket_id.return_value = []
    context.audit_repository.list_by_ticket_id.return_value = []
    (
        context.workflow_execution_repository
        .get_by_ticket_id.return_value
    ) = None

    context.service.get_ticket_detail(101)

    context.ticket_repository.get_by_id.assert_called_once_with(101)

    context.attachment_repository.list_by_ticket_id.assert_called_once_with(
        101
    )

    context.audit_repository.list_by_ticket_id.assert_called_once_with(
        101
    )

    (
        context.workflow_execution_repository
        .get_by_ticket_id.assert_called_once_with(101)
    )
