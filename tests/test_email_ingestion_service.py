from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.core.constants import ProcessingStatus
from app.schemas.email_schema import ParsedEmail
from app.services.email_ingestion_service import (
    EmailIngestionService,
)


def create_valid_email(
    message_id: str = "<test@example.com>",
    body: str = "Application crashes during upload.",
) -> ParsedEmail:

    return ParsedEmail(
        message_id=message_id,
        sender_name="Test Customer",
        sender_email="customer@example.com",
        subject="Application crash",
        body=body,
        received_at=datetime.now(timezone.utc),
        attachments=[],
    )


def test_ingestion_processes_valid_email():
    mock_imap = MagicMock()

    mock_imap.fetch_unread_emails.return_value = [
        (
            b"1",
            create_valid_email(),
        )
    ]

    service = EmailIngestionService(mock_imap)

    result = service.ingest_unread_emails()

    assert result.total_messages == 1
    assert result.successful_messages == 1
    assert result.failed_messages == 0
    assert result.results[0].status == ProcessingStatus.SUCCESS

    mock_imap.connect.assert_called_once()
    mock_imap.disconnect.assert_called_once()


def test_ingestion_rejects_email_without_message_id():
    mock_imap = MagicMock()

    mock_imap.fetch_unread_emails.return_value = [
        (
            b"2",
            create_valid_email(message_id=""),
        )
    ]

    service = EmailIngestionService(mock_imap)

    result = service.ingest_unread_emails()

    assert result.total_messages == 1
    assert result.successful_messages == 0
    assert result.failed_messages == 1
    assert result.results[0].status == ProcessingStatus.FAILED


def test_ingestion_rejects_empty_body():
    mock_imap = MagicMock()

    mock_imap.fetch_unread_emails.return_value = [
        (
            b"3",
            create_valid_email(body=""),
        )
    ]

    service = EmailIngestionService(mock_imap)

    result = service.ingest_unread_emails()

    assert result.failed_messages == 1
    assert result.results[0].failures


def test_ingestion_handles_multiple_emails_independently():
    mock_imap = MagicMock()

    mock_imap.fetch_unread_emails.return_value = [
        (
            b"1",
            create_valid_email(
                message_id="<one@example.com>"
            ),
        ),
        (
            b"2",
            create_valid_email(
                message_id="",
            ),
        ),
        (
            b"3",
            create_valid_email(
                message_id="<three@example.com>"
            ),
        ),
    ]

    service = EmailIngestionService(mock_imap)

    result = service.ingest_unread_emails()

    assert result.total_messages == 3
    assert result.successful_messages == 2
    assert result.failed_messages == 1


def test_ingestion_disconnects_when_fetch_raises():
    mock_imap = MagicMock()

    mock_imap.fetch_unread_emails.side_effect = RuntimeError(
        "unexpected failure"
    )

    service = EmailIngestionService(mock_imap)

    try:
        service.ingest_unread_emails()
    except RuntimeError:
        pass

    mock_imap.disconnect.assert_called_once()
