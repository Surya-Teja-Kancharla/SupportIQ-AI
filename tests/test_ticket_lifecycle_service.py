from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.constants import AuditAction, TicketStatus
from app.core.exceptions import InvalidTicketTransitionError
from app.services.ticket_lifecycle_service import TicketLifecycleService


@pytest.fixture
def db():
    return MagicMock()


def test_transition_allows_valid_status_change_and_records_audit(db):
    ticket = SimpleNamespace(id=7, status=TicketStatus.OPEN)
    ticket_repository = MagicMock()
    ticket_repository.get_by_id.return_value = ticket
    audit_repository = MagicMock()

    service = TicketLifecycleService(
        ticket_repository=ticket_repository,
        audit_repository=audit_repository,
    )

    result = service.transition(
        db,
        ticket_id=7,
        target_status=TicketStatus.IN_PROGRESS,
        performed_by="support-agent",
    )

    assert result is ticket
    assert ticket.status == TicketStatus.IN_PROGRESS
    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=7,
        action=AuditAction.STATUS_CHANGED,
        old_value=TicketStatus.OPEN,
        new_value=TicketStatus.IN_PROGRESS,
        performed_by="support-agent",
    )
    db.flush.assert_called_once()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_transition_rejects_invalid_status_change(db):
    ticket = SimpleNamespace(id=7, status=TicketStatus.OPEN)
    ticket_repository = MagicMock()
    ticket_repository.get_by_id.return_value = ticket
    audit_repository = MagicMock()

    service = TicketLifecycleService(
        ticket_repository=ticket_repository,
        audit_repository=audit_repository,
    )

    with pytest.raises(InvalidTicketTransitionError):
        service.transition(
            db,
            ticket_id=7,
            target_status=TicketStatus.RESOLVED,
            performed_by="support-agent",
        )

    audit_repository.create.assert_not_called()
    db.flush.assert_not_called()


def test_transition_raises_for_missing_ticket(db):
    ticket_repository = MagicMock()
    ticket_repository.get_by_id.return_value = None
    audit_repository = MagicMock()

    service = TicketLifecycleService(
        ticket_repository=ticket_repository,
        audit_repository=audit_repository,
    )

    with pytest.raises(ValueError, match="Ticket 42 not found"):
        service.transition(
            db,
            ticket_id=42,
            target_status=TicketStatus.IN_PROGRESS,
            performed_by="support-agent",
        )

    audit_repository.create.assert_not_called()
    db.flush.assert_not_called()
