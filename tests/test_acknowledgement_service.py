from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.constants import AuditAction
from app.schemas.smtp_schema import EmailDeliveryResult
from app.services.acknowledgement_service import AcknowledgementService

from app.schemas.email_schema import ParsedEmail
from app.services.email_ingestion_service import EmailIngestionService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def ticket():
    return SimpleNamespace(
        id=15,
        ticket_number="SUP-2026-000015",
        sender_email="customer@example.com",
        subject="Unable to access account",
        summary="Customer cannot access their account.",
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
        message_id="<message-id@example.com>",
        error_message=None,
    )

    return service


@pytest.fixture
def service(
    ticket_repository,
    audit_repository,
    smtp_service,
):
    return AcknowledgementService(
        ticket_repository=ticket_repository,
        audit_repository=audit_repository,
        smtp_service=smtp_service,
    )


def test_send_acknowledgement_builds_required_email_content(
    service,
    db,
    smtp_service,
):
    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    body = outbound_email.plain_text_body

    assert "Ticket ID: SUP-2026-000015" in body
    assert (
        "Issue Summary: "
        "Customer cannot access their account."
        in body
    )
    assert "Status: OPEN" in body
    assert "Estimated Response Time: Within 4 hours" in body


def test_send_acknowledgement_uses_ticket_sender_as_recipient(
    service,
    db,
    smtp_service,
):
    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert str(outbound_email.recipient_email) == (
        "customer@example.com"
    )


def test_send_acknowledgement_uses_ticket_number_in_subject(
    service,
    db,
    smtp_service,
):
    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert outbound_email.subject == (
        "Support request received - SUP-2026-000015"
    )


def test_high_priority_uses_four_hour_response_time(
    service,
    db,
    smtp_service,
):
    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert (
        "Estimated Response Time: Within 4 hours"
        in outbound_email.plain_text_body
    )


@pytest.mark.parametrize(
    ("priority", "expected_response_time"),
    [
        ("CRITICAL", "Within 1 hour"),
        ("HIGH", "Within 4 hours"),
        ("MEDIUM", "Within 1 business day"),
        ("LOW", "Within 2 business days"),
        (None, "Within 1 business day"),
        ("UNKNOWN", "Within 1 business day"),
    ],
)
def test_priority_maps_to_estimated_response_time(
    service,
    db,
    ticket,
    smtp_service,
    priority,
    expected_response_time,
):
    ticket.priority = priority

    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert (
        f"Estimated Response Time: {expected_response_time}"
        in outbound_email.plain_text_body
    )


def test_successful_send_sets_acknowledgement_sent_at(
    service,
    db,
    ticket,
):
    before_send = datetime.now(timezone.utc)

    result = service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    after_send = datetime.now(timezone.utc)

    assert ticket.acknowledgement_sent_at is not None

    assert (
        before_send
        <= ticket.acknowledgement_sent_at
        <= after_send
    )

    assert result.sent is True
    assert result.already_sent is False


def test_successful_send_creates_acknowledgement_sent_audit_event(
    service,
    db,
    audit_repository,
):
    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=15,
        action=AuditAction.ACKNOWLEDGEMENT_SENT,
        old_value=None,
        new_value="customer@example.com",
        performed_by="system",
    )


def test_successful_send_commits_once(
    service,
    db,
    ticket,
):
    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(ticket)
    db.rollback.assert_not_called()


def test_successful_send_returns_expected_result(
    service,
    db,
):
    result = service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    assert result.ticket_id == 15
    assert result.sent is True
    assert result.already_sent is False


def test_already_sent_ticket_does_not_send_again(
    service,
    db,
    ticket,
    smtp_service,
):
    ticket.acknowledgement_sent_at = datetime.now(
        timezone.utc
    )

    result = service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    smtp_service.send_email.assert_not_called()

    assert result.ticket_id == 15
    assert result.sent is False
    assert result.already_sent is True


def test_already_sent_ticket_does_not_create_duplicate_audit_event(
    service,
    db,
    ticket,
    audit_repository,
):
    ticket.acknowledgement_sent_at = datetime.now(
        timezone.utc
    )

    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    audit_repository.create.assert_not_called()


def test_already_sent_ticket_does_not_commit(
    service,
    db,
    ticket,
):
    ticket.acknowledgement_sent_at = datetime.now(
        timezone.utc
    )

    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()


def test_missing_ticket_raises_error(
    service,
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
        service.send_acknowledgement(
            db,
            ticket_id=999,
        )

    smtp_service.send_email.assert_not_called()
    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_smtp_exception_does_not_set_acknowledgement_sent_at(
    service,
    db,
    ticket,
    smtp_service,
):
    smtp_service.send_email.side_effect = RuntimeError(
        "SMTP unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="SMTP unavailable",
    ):
        service.send_acknowledgement(
            db,
            ticket_id=15,
        )

    assert ticket.acknowledgement_sent_at is None


def test_smtp_exception_does_not_create_audit_event(
    service,
    db,
    smtp_service,
    audit_repository,
):
    smtp_service.send_email.side_effect = RuntimeError(
        "SMTP unavailable"
    )

    with pytest.raises(RuntimeError):
        service.send_acknowledgement(
            db,
            ticket_id=15,
        )

    audit_repository.create.assert_not_called()


def test_smtp_exception_does_not_commit(
    service,
    db,
    smtp_service,
):
    smtp_service.send_email.side_effect = RuntimeError(
        "SMTP unavailable"
    )

    with pytest.raises(RuntimeError):
        service.send_acknowledgement(
            db,
            ticket_id=15,
        )

    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()


def test_unsuccessful_delivery_result_does_not_persist_acknowledgement(
    service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    smtp_service.send_email.return_value = EmailDeliveryResult(
        success=False,
        recipient_email="customer@example.com",
        message_id=None,
        error_message="Delivery rejected",
    )

    with pytest.raises(
        RuntimeError,
        match="Delivery rejected",
    ):
        service.send_acknowledgement(
            db,
            ticket_id=15,
        )

    assert ticket.acknowledgement_sent_at is None

    audit_repository.create.assert_not_called()

    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()


def test_audit_failure_after_smtp_success_rolls_back(
    service,
    db,
    ticket,
    smtp_service,
    audit_repository,
):
    audit_repository.create.side_effect = RuntimeError(
        "Audit creation failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Audit creation failed",
    ):
        service.send_acknowledgement(
            db,
            ticket_id=15,
        )

    smtp_service.send_email.assert_called_once()

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_commit_failure_after_smtp_success_rolls_back(
    service,
    db,
    smtp_service,
):
    db.commit.side_effect = RuntimeError(
        "Database commit failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Database commit failed",
    ):
        service.send_acknowledgement(
            db,
            ticket_id=15,
        )

    smtp_service.send_email.assert_called_once()

    db.commit.assert_called_once()
    db.rollback.assert_called_once()


def test_refresh_failure_after_commit_calls_rollback(
    service,
    db,
    smtp_service,
):
    db.refresh.side_effect = RuntimeError(
        "Refresh failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Refresh failed",
    ):
        service.send_acknowledgement(
            db,
            ticket_id=15,
        )

    smtp_service.send_email.assert_called_once()

    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    db.rollback.assert_called_once()


def test_missing_summary_falls_back_to_subject(
    service,
    db,
    ticket,
    smtp_service,
):
    ticket.summary = None

    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert (
        "Issue Summary: Unable to access account"
        in outbound_email.plain_text_body
    )


def test_missing_status_falls_back_to_open(
    service,
    db,
    ticket,
    smtp_service,
):
    ticket.status = None

    service.send_acknowledgement(
        db,
        ticket_id=15,
    )

    outbound_email = (
        smtp_service.send_email.call_args.args[0]
    )

    assert "Status: OPEN" in outbound_email.plain_text_body

def test_email_ingestion_automatically_executes_acknowledgement_workflow():
    db = MagicMock()

    ticket = SimpleNamespace(
        id=501,
        ticket_number="SUP-2026-000501",
        sender_email="customer@example.com",
        subject="Unable to access customer portal",
        summary="Customer cannot access the customer portal.",
        priority="HIGH",
        status="OPEN",
        acknowledgement_sent_at=None,
    )

    ticket_repository = MagicMock()
    ticket_repository.get_by_id.return_value = ticket

    audit_repository = MagicMock()

    smtp_service = MagicMock()
    smtp_service.send_email.return_value = (
        EmailDeliveryResult(
            success=True,
            recipient_email="customer@example.com",
            message_id="<integration@example.com>",
            error_message=None,
        )
    )

    acknowledgement_service = AcknowledgementService(
        ticket_repository=ticket_repository,
        audit_repository=audit_repository,
        smtp_service=smtp_service,
    )

    workflow_service = MagicMock()
    workflow_service.process_email.return_value = (
        SimpleNamespace(
            ticket_id=501,
            ticket_number="SUP-2026-000501",
        )
    )

    imap_service = MagicMock()

    parsed_email = ParsedEmail(
        message_id="<hour13@example.com>",
        sender_name="Test Customer",
        sender_email="customer@example.com",
        subject="Unable to access customer portal",
        body="I cannot access the customer portal.",
        received_at=datetime.now(timezone.utc),
        attachments=[],
    )

    imap_service.fetch_unread_emails.return_value = [
        (b"501", parsed_email)
    ]

    ingestion_service = EmailIngestionService(
        imap_service=imap_service,
        workflow_service=workflow_service,
        acknowledgement_service=acknowledgement_service,
        db=db,
    )

    result = ingestion_service.ingest_unread_emails()

    assert result.total_messages == 1
    assert result.successful_messages == 1
    assert result.failed_messages == 0

    workflow_service.process_email.assert_called_once_with(
        parsed_email
    )

    ticket_repository.get_by_id.assert_called_once_with(
        db,
        501,
    )

    smtp_service.send_email.assert_called_once()

    outbound_email = smtp_service.send_email.call_args.args[0]

    assert str(outbound_email.recipient_email) == (
        "customer@example.com"
    )

    assert "Ticket ID: SUP-2026-000501" in (
        outbound_email.plain_text_body
    )

    assert (
        "Issue Summary: "
        "Customer cannot access the customer portal."
        in outbound_email.plain_text_body
    )

    assert "Status: OPEN" in (
        outbound_email.plain_text_body
    )

    assert (
        "Estimated Response Time: Within 4 hours"
        in outbound_email.plain_text_body
    )

    assert ticket.acknowledgement_sent_at is not None

    audit_repository.create.assert_called_once_with(
        db,
        ticket_id=501,
        action=AuditAction.ACKNOWLEDGEMENT_SENT,
        old_value=None,
        new_value="customer@example.com",
        performed_by="system",
    )

    db.commit.assert_called_once_with()
