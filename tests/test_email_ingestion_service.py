from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.core.constants import WorkflowStage
from app.schemas.email_schema import ParsedEmail
from app.services.email_ingestion_service import EmailIngestionService


def create_valid_email() -> ParsedEmail:
    return ParsedEmail(
        message_id="<hour13-ingestion@example.com>",
        sender_name="Test Customer",
        sender_email="customer@example.com",
        subject="Unable to access customer portal",
        body="I cannot access the customer portal.",
        received_at=datetime.now(timezone.utc),
        attachments=[],
    )

    
def create_automated_ingestion_service(
    mock_imap,
):
    mock_workflow = MagicMock()
    mock_acknowledgement = MagicMock()
    mock_db = MagicMock()

    mock_workflow.process_email.return_value = (
        SimpleNamespace(
            ticket_id=101,
            ticket_number="SUP-2026-000101",
        )
    )

    service = EmailIngestionService(
        imap_service=mock_imap,
        workflow_service=mock_workflow,
        acknowledgement_service=mock_acknowledgement,
        db=mock_db,
    )

    return (
        service,
        mock_workflow,
        mock_acknowledgement,
        mock_db,
    )


def test_successful_ingestion_sends_acknowledgement():
    mock_imap = MagicMock()

    email = create_valid_email()

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]

    (
        service,
        mock_workflow,
        mock_acknowledgement,
        mock_db,
    ) = create_automated_ingestion_service(mock_imap)

    result = service.ingest_unread_emails()

    assert result.successful_messages == 1

    mock_workflow.process_email.assert_called_once_with(email)

    mock_acknowledgement.send_acknowledgement.assert_called_once_with(
        mock_db,
        ticket_id=101,
    )


def test_ingestion_passes_created_ticket_id_to_acknowledgement_service():
    mock_imap = MagicMock()

    email = create_valid_email()

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]

    (
        service,
        mock_workflow,
        mock_acknowledgement,
        mock_db,
    ) = create_automated_ingestion_service(mock_imap)

    mock_workflow.process_email.return_value = (
        SimpleNamespace(
            ticket_id=987,
            ticket_number="SUP-2026-000987",
        )
    )

    service.ingest_unread_emails()

    mock_acknowledgement.send_acknowledgement.assert_called_once_with(
        mock_db,
        ticket_id=987,
    )


def test_acknowledgement_runs_after_workflow_success():
    mock_imap = MagicMock()

    email = create_valid_email()

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]

    call_order = []

    mock_workflow = MagicMock()
    mock_acknowledgement = MagicMock()
    mock_db = MagicMock()

    def process_email(_email):
        call_order.append("workflow")

        return SimpleNamespace(
            ticket_id=101,
            ticket_number="SUP-2026-000101",
        )

    def send_acknowledgement(
        _db,
        *,
        ticket_id,
    ):
        call_order.append("acknowledgement")

    mock_workflow.process_email.side_effect = process_email

    mock_acknowledgement.send_acknowledgement.side_effect = (
        send_acknowledgement
    )

    service = EmailIngestionService(
        imap_service=mock_imap,
        workflow_service=mock_workflow,
        acknowledgement_service=mock_acknowledgement,
        db=mock_db,
    )

    service.ingest_unread_emails()

    assert call_order == [
        "workflow",
        "acknowledgement",
    ]


def test_workflow_failure_does_not_send_acknowledgement():
    mock_imap = MagicMock()

    email = create_valid_email()

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]

    (
        service,
        mock_workflow,
        mock_acknowledgement,
        _mock_db,
    ) = create_automated_ingestion_service(mock_imap)

    mock_workflow.process_email.side_effect = RuntimeError(
        "Workflow failed"
    )

    result = service.ingest_unread_emails()

    assert result.successful_messages == 0
    assert result.failed_messages == 1

    mock_acknowledgement.send_acknowledgement.assert_not_called()


def test_acknowledgement_failure_does_not_fail_successful_ingestion():
    mock_imap = MagicMock()

    email = create_valid_email()

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]

    (
        service,
        mock_workflow,
        mock_acknowledgement,
        _mock_db,
    ) = create_automated_ingestion_service(mock_imap)

    mock_acknowledgement.send_acknowledgement.side_effect = (
        RuntimeError("SMTP unavailable")
    )

    result = service.ingest_unread_emails()

    assert result.successful_messages == 1
    assert result.failed_messages == 0

    mock_workflow.process_email.assert_called_once_with(email)

    mock_acknowledgement.send_acknowledgement.assert_called_once()


def test_missing_acknowledgement_service_preserves_workflow_success():
    mock_imap = MagicMock()
    mock_workflow = MagicMock()

    email = create_valid_email()

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]

    mock_workflow.process_email.return_value = (
        SimpleNamespace(
            ticket_id=101,
            ticket_number="SUP-2026-000101",
        )
    )

    service = EmailIngestionService(
        imap_service=mock_imap,
        workflow_service=mock_workflow,
    )

    result = service.ingest_unread_emails()

    assert result.successful_messages == 1
    assert result.failed_messages == 0

    mock_workflow.process_email.assert_called_once_with(email)


def test_missing_db_skips_acknowledgement_safely():
    mock_imap = MagicMock()
    mock_workflow = MagicMock()
    mock_acknowledgement = MagicMock()

    email = create_valid_email()

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]

    mock_workflow.process_email.return_value = (
        SimpleNamespace(
            ticket_id=101,
            ticket_number="SUP-2026-000101",
        )
    )

    service = EmailIngestionService(
        imap_service=mock_imap,
        workflow_service=mock_workflow,
        acknowledgement_service=mock_acknowledgement,
        db=None,
    )

    result = service.ingest_unread_emails()

    assert result.successful_messages == 1

    mock_acknowledgement.send_acknowledgement.assert_not_called()


def test_ingestion_delegates_workflow_execution_when_telemetry_is_injected():
    mock_imap = MagicMock()
    mock_workflow = MagicMock()
    mock_execution_service = MagicMock()
    mock_acknowledgement = MagicMock()
    mock_db = MagicMock()

    email = create_valid_email()
    workflow_execution = SimpleNamespace(
        execution_id="execution-123",
        message_id=email.message_id,
    )

    mock_imap.fetch_unread_emails.return_value = [
        (b"1", email)
    ]
    mock_workflow.process_email.return_value = SimpleNamespace(
        ticket_id=101,
        ticket_number="SUP-2026-000101",
        execution_id=workflow_execution.execution_id,
    )
    mock_execution_service.start_execution.return_value = (
        workflow_execution
    )

    service = EmailIngestionService(
        imap_service=mock_imap,
        workflow_service=mock_workflow,
        acknowledgement_service=mock_acknowledgement,
        db=mock_db,
        workflow_execution_service=mock_execution_service,
    )

    result = service.ingest_unread_emails()

    assert result.successful_messages == 1
    mock_workflow.process_email.assert_called_once_with(
        email,
        workflow_execution=workflow_execution,
    )
    mock_execution_service.start_execution.assert_called_once_with(
        message_id=email.message_id,
        stage=WorkflowStage.EMAIL_FETCHED,
    )
    mock_execution_service.advance_stage.assert_any_call(
        workflow_execution,
        stage=WorkflowStage.EMAIL_PARSED,
    )
