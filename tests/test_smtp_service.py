import smtplib
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import (
    SMTPAuthenticationError,
    SMTPConnectionError,
    SMTPSendError,
)
from app.schemas.smtp_schema import OutboundEmail
from app.services.smtp_service import SMTPService


@pytest.fixture
def outbound_email():
    return OutboundEmail(
        recipient_email="customer@example.com",
        subject="Support request received",
        plain_text_body="Your support request was received.",
        html_body="<p>Your support request was received.</p>",
    )


def test_build_message_contains_required_headers(
    outbound_email,
):
    service = SMTPService()

    message = service._build_message(outbound_email)

    assert message["From"] == service.email_address
    assert message["To"] == "customer@example.com"
    assert message["Subject"] == "Support request received"
    assert message["Message-ID"] is not None
    assert message.is_multipart()


@patch("app.services.smtp_service.smtplib.SMTP")
def test_send_email_succeeds(
    mock_smtp_class,
    outbound_email,
):
    smtp_connection = MagicMock()

    mock_smtp_class.return_value.__enter__.return_value = (
        smtp_connection
    )

    smtp_connection.send_message.return_value = {}

    service = SMTPService()

    result = service.send_email(outbound_email)

    assert result.success is True
    assert str(result.recipient_email) == "customer@example.com"
    assert result.message_id is not None

    smtp_connection.starttls.assert_called_once()
    smtp_connection.login.assert_called_once()
    smtp_connection.send_message.assert_called_once()


@patch("app.services.smtp_service.smtplib.SMTP")
def test_send_email_maps_authentication_error(
    mock_smtp_class,
    outbound_email,
):
    smtp_connection = MagicMock()

    mock_smtp_class.return_value.__enter__.return_value = (
        smtp_connection
    )

    smtp_connection.login.side_effect = (
        smtplib.SMTPAuthenticationError(
            535,
            b"authentication failed",
        )
    )

    service = SMTPService()

    with pytest.raises(SMTPAuthenticationError):
        service.send_email(outbound_email)


@patch("app.services.smtp_service.smtplib.SMTP")
def test_send_email_maps_connection_error(
    mock_smtp_class,
    outbound_email,
):
    mock_smtp_class.side_effect = OSError(
        "connection failed"
    )

    service = SMTPService()

    with pytest.raises(SMTPConnectionError):
        service.send_email(outbound_email)


@patch("app.services.smtp_service.smtplib.SMTP")
def test_send_email_rejects_refused_recipient(
    mock_smtp_class,
    outbound_email,
):
    smtp_connection = MagicMock()

    mock_smtp_class.return_value.__enter__.return_value = (
        smtp_connection
    )

    smtp_connection.send_message.return_value = {
        "customer@example.com": (
            550,
            b"recipient rejected",
        )
    }

    service = SMTPService()

    with pytest.raises(SMTPSendError):
        service.send_email(outbound_email)
