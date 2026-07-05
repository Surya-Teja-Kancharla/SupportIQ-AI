from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.manual_review_service import ManualReviewService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def ticket():
    return SimpleNamespace(
        id=1,
        subject="Unable to login",
        body="I cannot access my account.",
        category="Authentication",
        priority="MEDIUM",
        sentiment="NEGATIVE",
        assigned_team="Technical Support",
        status="OPEN",
        suggested_reply="Original suggested reply.",
    )


@pytest.fixture
def ticket_repository(ticket):
    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    return repository


@pytest.fixture
def audit_repository():
    return MagicMock()


@pytest.fixture
def internal_note_repository():
    return MagicMock()


@pytest.fixture
def reply_suggestion_service():
    return MagicMock()


@pytest.fixture
def service(
    ticket_repository,
    audit_repository,
    internal_note_repository,
    reply_suggestion_service,
):
    return ManualReviewService(
        ticket_repository=ticket_repository,
        audit_repository=audit_repository,
        internal_note_repository=internal_note_repository,
        reply_suggestion_service=reply_suggestion_service,
    )


def test_update_category_creates_audit_record(
    service,
    db,
    ticket,
    audit_repository,
):
    result = service.update_category(
        db,
        ticket_id=1,
        category="Account Access",
        performed_by="support-agent",
    )

    assert result is ticket
    assert ticket.category == "Account Access"

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        action="CATEGORY_CHANGED",
        old_value="Authentication",
        new_value="Account Access",
        performed_by="support-agent",
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)
    db.rollback.assert_not_called()


def test_update_priority_creates_audit_record(
    service,
    db,
    ticket,
    audit_repository,
):
    result = service.update_priority(
        db,
        ticket_id=1,
        priority="HIGH",
        performed_by="support-agent",
    )

    assert result is ticket
    assert ticket.priority == "HIGH"

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        action="PRIORITY_CHANGED",
        old_value="MEDIUM",
        new_value="HIGH",
        performed_by="support-agent",
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)


def test_reassign_team_creates_audit_record(
    service,
    db,
    ticket,
    audit_repository,
):
    result = service.reassign_team(
        db,
        ticket_id=1,
        assigned_team="Billing Support",
        performed_by="support-agent",
    )

    assert result is ticket
    assert ticket.assigned_team == "Billing Support"

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        action="TEAM_REASSIGNED",
        old_value="Technical Support",
        new_value="Billing Support",
        performed_by="support-agent",
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)


def test_update_status_creates_audit_record(
    service,
    db,
    ticket,
    audit_repository,
):
    result = service.update_status(
        db,
        ticket_id=1,
        status="IN_PROGRESS",
        performed_by="support-agent",
    )

    assert result is ticket
    assert ticket.status == "IN_PROGRESS"

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        action="STATUS_CHANGED",
        old_value="OPEN",
        new_value="IN_PROGRESS",
        performed_by="support-agent",
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)


def test_edit_suggested_reply_creates_audit_record(
    service,
    db,
    ticket,
    audit_repository,
):
    result = service.edit_suggested_reply(
        db,
        ticket_id=1,
        suggested_reply="Edited reply from the support agent.",
        performed_by="support-agent",
    )

    assert result is ticket
    assert ticket.suggested_reply == (
        "Edited reply from the support agent."
    )

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        action="SUGGESTED_REPLY_EDITED",
        old_value="Original suggested reply.",
        new_value="Edited reply from the support agent.",
        performed_by="support-agent",
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)


def test_add_internal_note_creates_note_and_audit_record(
    service,
    db,
    ticket,
    internal_note_repository,
    audit_repository,
):
    internal_note = SimpleNamespace(
        id=10,
        ticket_id=1,
        note="Waiting for customer confirmation.",
        created_by="support-agent",
    )

    internal_note_repository.create.return_value = internal_note

    result = service.add_internal_note(
        db,
        ticket_id=1,
        note="Waiting for customer confirmation.",
        created_by="support-agent",
    )

    assert result is internal_note

    internal_note_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        note="Waiting for customer confirmation.",
        created_by="support-agent",
    )

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        action="INTERNAL_NOTE_ADDED",
        old_value=None,
        new_value="Waiting for customer confirmation.",
        performed_by="support-agent",
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(internal_note)
    db.rollback.assert_not_called()


def test_regenerate_suggested_reply_updates_ticket_and_creates_audit_record(
    service,
    db,
    ticket,
    reply_suggestion_service,
    audit_repository,
):
    reply_suggestion_service.generate.return_value = SimpleNamespace(
        suggested_reply="New AI-generated suggested reply."
    )

    result = service.regenerate_suggested_reply(
        db,
        ticket_id=1,
        performed_by="support-agent",
    )

    assert result is ticket

    assert (
        ticket.suggested_reply
        == "New AI-generated suggested reply."
    )

    reply_suggestion_service.generate.assert_called_once_with(
        subject="Unable to login",
        body="I cannot access my account.",
        category="Authentication",
        priority="MEDIUM",
        sentiment="NEGATIVE",
        assigned_team="Technical Support",
    )

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=1,
        action="SUGGESTED_REPLY_REGENERATED",
        old_value="Original suggested reply.",
        new_value="New AI-generated suggested reply.",
        performed_by="support-agent",
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)


def test_missing_ticket_raises_error(
    service,
    db,
    ticket_repository,
    audit_repository,
):
    ticket_repository.get_by_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Ticket 999 not found",
    ):
        service.update_priority(
            db,
            ticket_id=999,
            priority="HIGH",
            performed_by="support-agent",
        )

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_failed_audit_creation_rolls_back_ticket_mutation(
    service,
    db,
    ticket,
    audit_repository,
):
    audit_repository.create.side_effect = RuntimeError(
        "Audit creation failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Audit creation failed",
    ):
        service.update_priority(
            db,
            ticket_id=1,
            priority="HIGH",
            performed_by="support-agent",
        )

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_same_value_does_not_create_duplicate_audit_record(
    service,
    db,
    ticket,
    audit_repository,
):
    result = service.update_priority(
        db,
        ticket_id=1,
        priority="MEDIUM",
        performed_by="support-agent",
    )

    assert result is ticket

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()


def test_internal_note_failure_rolls_back(
    service,
    db,
    internal_note_repository,
    audit_repository,
):
    internal_note_repository.create.side_effect = RuntimeError(
        "Internal note creation failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Internal note creation failed",
    ):
        service.add_internal_note(
            db,
            ticket_id=1,
            note="Failed note",
            created_by="support-agent",
        )

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_reply_regeneration_failure_rolls_back(
    service,
    db,
    reply_suggestion_service,
    audit_repository,
):
    reply_suggestion_service.generate.side_effect = RuntimeError(
        "LLM request failed"
    )

    with pytest.raises(
        RuntimeError,
        match="LLM request failed",
    ):
        service.regenerate_suggested_reply(
            db,
            ticket_id=1,
            performed_by="support-agent",
        )

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()
    db.rollback.assert_called_once()
