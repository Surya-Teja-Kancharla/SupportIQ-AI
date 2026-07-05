from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.core.constants import AuditAction
from app.core.exceptions import InvalidTicketTransitionError
from app.models.ticket import Ticket
from app.models.ticket_audit_log import TicketAuditLog
from app.repositories.audit_repository import AuditRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.ticket_lifecycle_service import (
    TicketLifecycleService,
)


def create_ticket(
    db_session,
    unique_suffix: str,
) -> Ticket:
    ticket = Ticket(
        ticket_number=f"SUP-H16-L-{unique_suffix[:12]}",
        customer_name="Lifecycle Customer",
        company="Example Corp",
        sender_email="customer@example.com",
        subject="Account access issue",
        body="I cannot access my account.",
        summary="Customer cannot access account.",
        description="Account access failure.",
        category="Account Access",
        priority="High",
        sentiment="Negative",
        product="Customer Portal",
        suggested_department="Customer Success",
        assigned_team="Customer Success",
        confidence_score=0.95,
        status="OPEN",
        received_at=datetime.now(timezone.utc),
        priority_reason="AI recommendation retained.",
        suggested_reply="We are investigating the issue.",
    )

    db_session.add(ticket)
    db_session.flush()

    return ticket


def build_service(db_session) -> TicketLifecycleService:
    return TicketLifecycleService(
        ticket_repository=TicketRepository(db_session),
        audit_repository=AuditRepository(db_session),
    )


def test_ticket_lifecycle_transition_persists_audit(
    db_session,
    unique_suffix,
):
    ticket = create_ticket(
        db_session,
        unique_suffix,
    )

    service = build_service(db_session)

    result = service.transition(
        db_session,
        ticket_id=ticket.id,
        target_status="IN_PROGRESS",
        performed_by="hour16-admin",
    )

    db_session.flush()
    db_session.refresh(ticket)

    assert result.id == ticket.id
    assert result.status == "IN_PROGRESS"
    assert ticket.status == "IN_PROGRESS"

    audit_logs = list(
        db_session.scalars(
            select(TicketAuditLog).where(
                TicketAuditLog.ticket_id == ticket.id
            )
        )
    )

    assert len(audit_logs) == 1

    audit = audit_logs[0]

    assert audit.ticket_id == ticket.id
    assert audit.action == AuditAction.STATUS_CHANGED
    assert audit.old_value == "OPEN"
    assert audit.new_value == "IN_PROGRESS"
    assert audit.performed_by == "hour16-admin"
    assert audit.created_at is not None


def test_invalid_lifecycle_transition_creates_no_audit(
    db_session,
    unique_suffix,
):
    ticket = create_ticket(
        db_session,
        unique_suffix,
    )

    service = build_service(db_session)

    with pytest.raises(InvalidTicketTransitionError):
        service.transition(
            db_session,
            ticket_id=ticket.id,
            target_status="RESOLVED",
            performed_by="hour16-admin",
        )

    db_session.flush()
    db_session.refresh(ticket)

    assert ticket.status == "OPEN"

    audit_logs = list(
        db_session.scalars(
            select(TicketAuditLog).where(
                TicketAuditLog.ticket_id == ticket.id
            )
        )
    )

    assert audit_logs == []
