from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.constants import AuditAction
from app.schemas.smtp_schema import EmailDeliveryResult
from app.services.acknowledgement_service import AcknowledgementService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def ticket():
    return SimpleNamespace(
        id=101,
        ticket_number="SUP-2026-000101",
        sender_email="customer@example.com",
        subject="Unable to access customer portal",
        summary="Customer cannot access the customer portal.",
        priority="HIGH",
        status="OPEN",
        acknowledgement_sent_at=None,
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
def smtp_service():
    service = MagicMock()

    service.send_email.return_value = EmailDeliveryResult(
        success=True,
        recipient_email="customer@example.com",
        message_id="<ack-message@example.com>",
        error_message=None,
    )

    return service


@pytest.fixture
def acknowledgement_service(
    ticket_repository,
    audit_repository,
    smtp_service,
):
    return AcknowledgementService(
        ticket_repository=ticket_repository,
        audit_repository=audit_repository,
        smtp_service=smtp_service,
    )


def test_acknowledgement_workflow_sends_email_and_persists_state(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    result = acknowledgement_service.send_acknowledgement(
        db,
        ticket_id=ticket.id,
    )

    assert result.ticket_id == ticket.id
    assert result.sent is True
    assert result.already_sent is False

    ticket_repository_call = (
        acknowledgement_service
        .ticket_repository
        .get_by_id
    )

    ticket_repository_call.assert_called_once_with(
        db,
        ticket.id,
    )

    smtp_service.send_email.assert_called_once()

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert str(outbound_email.recipient_email) == (
        ticket.sender_email
    )

    assert outbound_email.subject == (
        "Support request received - "
        "SUP-2026-000101"
    )

    body = outbound_email.plain_text_body

    assert "Ticket ID: SUP-2026-000101" in body

    assert (
        "Issue Summary: "
        "Customer cannot access the customer portal."
        in body
    )

    assert "Status: OPEN" in body

    assert (
        "Estimated Response Time: Within 4 hours"
        in body
    )

    assert ticket.acknowledgement_sent_at is not None

    assert isinstance(
        ticket.acknowledgement_sent_at,
        datetime,
    )

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=ticket.id,
        action=AuditAction.ACKNOWLEDGEMENT_SENT,
        old_value=None,
        new_value=ticket.sender_email,
        performed_by="system",
    )

    db.commit.assert_called_once_with()

    db.refresh.assert_called_once_with(ticket)

    db.rollback.assert_not_called()


def test_duplicate_acknowledgement_attempt_does_not_send_second_email(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    first_result = (
        acknowledgement_service.send_acknowledgement(
            db,
            ticket_id=ticket.id,
        )
    )

    assert first_result.sent is True
    assert first_result.already_sent is False

    first_sent_at = ticket.acknowledgement_sent_at

    second_result = (
        acknowledgement_service.send_acknowledgement(
            db,
            ticket_id=ticket.id,
        )
    )

    assert second_result.sent is False
    assert second_result.already_sent is True

    assert ticket.acknowledgement_sent_at == first_sent_at

    assert smtp_service.send_email.call_count == 1

    assert audit_repository.create.call_count == 1

    assert db.commit.call_count == 1

    assert db.refresh.call_count == 1

    db.rollback.assert_not_called()


def test_acknowledgement_workflow_uses_priority_response_time_policy(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
):
    ticket.priority = "CRITICAL"

    acknowledgement_service.send_acknowledgement(
        db,
        ticket_id=ticket.id,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert (
        "Estimated Response Time: Within 1 hour"
        in outbound_email.plain_text_body
    )


def test_acknowledgement_workflow_smtp_failure_preserves_unsent_state(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    smtp_service.send_email.side_effect = RuntimeError(
        "SMTP delivery failed"
    )

    with pytest.raises(
        RuntimeError,
        match="SMTP delivery failed",
    ):
        acknowledgement_service.send_acknowledgement(
            db,
            ticket_id=ticket.id,
        )

    assert ticket.acknowledgement_sent_at is None

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()

    db.refresh.assert_not_called()

    db.rollback.assert_not_called()


def test_failed_acknowledgement_can_be_retried_later(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    smtp_service.send_email.side_effect = RuntimeError(
        "Temporary SMTP failure"
    )

    with pytest.raises(
        RuntimeError,
        match="Temporary SMTP failure",
    ):
        acknowledgement_service.send_acknowledgement(
            db,
            ticket_id=ticket.id,
        )

    assert ticket.acknowledgement_sent_at is None

    smtp_service.send_email.side_effect = None

    smtp_service.send_email.return_value = (
        EmailDeliveryResult(
            success=True,
            recipient_email=ticket.sender_email,
            message_id="<retry-success@example.com>",
            error_message=None,
        )
    )

    result = acknowledgement_service.send_acknowledgement(
        db,
        ticket_id=ticket.id,
    )

    assert result.sent is True
    assert result.already_sent is False

    assert ticket.acknowledgement_sent_at is not None

    assert smtp_service.send_email.call_count == 2

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=ticket.id,
        action=AuditAction.ACKNOWLEDGEMENT_SENT,
        old_value=None,
        new_value=ticket.sender_email,
        performed_by="system",
    )

    db.commit.assert_called_once_with()

    db.refresh.assert_called_once_with(ticket)


def test_audit_failure_after_smtp_success_rolls_back_transaction(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    audit_repository.create.side_effect = RuntimeError(
        "Audit persistence failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Audit persistence failed",
    ):
        acknowledgement_service.send_acknowledgement(
            db,
            ticket_id=ticket.id,
        )

    smtp_service.send_email.assert_called_once()

    db.commit.assert_not_called()

    db.rollback.assert_called_once_with()


def test_database_commit_failure_after_smtp_success_rolls_back(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
):
    db.commit.side_effect = RuntimeError(
        "Database commit failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Database commit failed",
    ):
        acknowledgement_service.send_acknowledgement(
            db,
            ticket_id=ticket.id,
        )

    smtp_service.send_email.assert_called_once()

    db.commit.assert_called_once_with()

    db.rollback.assert_called_once_with()


def test_already_sent_ticket_does_not_create_new_transaction(
    acknowledgement_service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    existing_sent_at = datetime(
        2026,
        7,
        5,
        12,
        30,
        tzinfo=timezone.utc,
    )

    ticket.acknowledgement_sent_at = existing_sent_at

    result = acknowledgement_service.send_acknowledgement(
        db,
        ticket_id=ticket.id,
    )

    assert result.sent is False
    assert result.already_sent is True

    assert ticket.acknowledgement_sent_at == existing_sent_at

    smtp_service.send_email.assert_not_called()

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()

    db.refresh.assert_not_called()

    db.rollback.assert_not_called()


def test_missing_ticket_stops_acknowledgement_workflow(
    acknowledgement_service,
    db,
    ticket_repository,
    smtp_service,
    audit_repository,
):
    ticket_repository.get_by_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Ticket 999 not found",
    ):
        acknowledgement_service.send_acknowledgement(
            db,
            ticket_id=999,
        )

    smtp_service.send_email.assert_not_called()

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()

    db.refresh.assert_not_called()

    db.rollback.assert_not_called()
