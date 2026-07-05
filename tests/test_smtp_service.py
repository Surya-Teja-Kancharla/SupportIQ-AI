import smtplib
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import (
    SMTPAuthenticationError,
    SMTPConnectionError,
    SMTPSendError,
)
from app.core.retry import RetryExecutor, RetryPolicy
from app.services.smtp_service import SMTPService

from app.schemas.smtp_schema import OutboundEmail


@pytest.fixture
def outbound_email():
    return OutboundEmail(
        recipient_email="customer@example.com",
        subject="Support request received",
        plain_text_body=(
            "Your support request has been received."
        ),
    )


def create_zero_delay_retry_executor(
    max_attempts: int = 3,
) -> RetryExecutor:
    return RetryExecutor(
        RetryPolicy(
            max_attempts=max_attempts,
            initial_delay_seconds=0,
            maximum_delay_seconds=0,
            exponential_base=1,
            jitter_seconds=0,
        ),
        sleep_function=lambda _: None,
        random_function=lambda _start, _end: 0,
    )


def test_transient_connection_failure_is_retried(
    outbound_email,
):
    service = SMTPService(
        retry_executor=create_zero_delay_retry_executor()
    )

    successful_connection = MagicMock()

    successful_connection.__enter__.return_value = (
        successful_connection
    )

    successful_connection.send_message.return_value = {}

    with patch(
        "app.services.smtp_service.smtplib.SMTP",
        side_effect=[
            OSError("temporary failure"),
            successful_connection,
        ],
    ) as mock_smtp:

        result = service.send_email(outbound_email)

    assert result.success is True
    assert mock_smtp.call_count == 2

    successful_connection.ehlo.assert_called()
    successful_connection.starttls.assert_called_once()
    successful_connection.login.assert_called_once()
    successful_connection.send_message.assert_called_once()


def test_transient_failure_eventually_succeeds(
    outbound_email,
):
    service = SMTPService(
        retry_executor=create_zero_delay_retry_executor()
    )

    successful_connection = MagicMock()
    successful_connection.__enter__.return_value = (
        successful_connection
    )
    successful_connection.send_message.return_value = {}

    with patch(
        "app.services.smtp_service.smtplib.SMTP",
        side_effect=[
            TimeoutError("timeout one"),
            ConnectionError("timeout two"),
            successful_connection,
        ],
    ) as mock_smtp:
        result = service.send_email(outbound_email)

    assert result.success is True
    assert mock_smtp.call_count == 3


def test_transient_failure_exhausts_retry_attempts(
    outbound_email,
):
    service = SMTPService(
        retry_executor=create_zero_delay_retry_executor()
    )

    with patch(
        "app.services.smtp_service.smtplib.SMTP",
        side_effect=OSError("SMTP unavailable"),
    ) as mock_smtp:

        with pytest.raises(SMTPConnectionError):
            service.send_email(outbound_email)

    assert mock_smtp.call_count == 3


def test_authentication_failure_is_not_retried(
    outbound_email,
):
    service = SMTPService(
        retry_executor=create_zero_delay_retry_executor()
    )

    smtp_connection = MagicMock()
    smtp_connection.__enter__.return_value = smtp_connection

    smtp_connection.login.side_effect = (
        smtplib.SMTPAuthenticationError(
            535,
            b"Authentication failed",
        )
    )

    with patch(
        "app.services.smtp_service.smtplib.SMTP",
        return_value=smtp_connection,
    ) as mock_smtp:

        with pytest.raises(SMTPAuthenticationError):
            service.send_email(outbound_email)

    assert mock_smtp.call_count == 1


def test_refused_recipient_is_not_retried(
    outbound_email,
):
    service = SMTPService(
        retry_executor=create_zero_delay_retry_executor()
    )

    smtp_connection = MagicMock()
    smtp_connection.__enter__.return_value = smtp_connection

    smtp_connection.send_message.return_value = {
        "customer@example.com": (
            550,
            b"Recipient rejected",
        )
    }

    with patch(
        "app.services.smtp_service.smtplib.SMTP",
        return_value=smtp_connection,
    ) as mock_smtp:

        with pytest.raises(SMTPSendError):
            service.send_email(outbound_email)

    assert mock_smtp.call_count == 1


def test_permanent_smtp_response_is_not_retried(
    outbound_email,
):
    service = SMTPService(
        retry_executor=create_zero_delay_retry_executor()
    )

    smtp_connection = MagicMock()
    smtp_connection.__enter__.return_value = smtp_connection

    smtp_connection.send_message.side_effect = (
        smtplib.SMTPDataError(
            550,
            b"Permanent delivery failure",
        )
    )

    with patch(
        "app.services.smtp_service.smtplib.SMTP",
        return_value=smtp_connection,
    ) as mock_smtp:

        with pytest.raises(SMTPSendError):
            service.send_email(outbound_email)

    assert mock_smtp.call_count == 1


def test_transient_smtp_response_is_retried(
    outbound_email,
):
    service = SMTPService(
        retry_executor=create_zero_delay_retry_executor()
    )

    first_connection = MagicMock()
    first_connection.__enter__.return_value = (
        first_connection
    )

    first_connection.send_message.side_effect = (
        smtplib.SMTPDataError(
            451,
            b"Temporary delivery failure",
        )
    )

    second_connection = MagicMock()
    second_connection.__enter__.return_value = (
        second_connection
    )
    second_connection.send_message.return_value = {}

    with patch(
        "app.services.smtp_service.smtplib.SMTP",
        side_effect=[
            first_connection,
            second_connection,
        ],
    ) as mock_smtp:

        result = service.send_email(outbound_email)

    assert result.success is True
    assert mock_smtp.call_count == 2
