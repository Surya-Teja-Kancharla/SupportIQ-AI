import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from app.config.settings import settings
from app.core.constants import LogEvent
from app.core.exceptions import (
    RetryExhaustedError,
    SMTPAuthenticationError,
    SMTPConnectionError,
    SMTPSendError,
)
from app.core.logging import get_logger, log_event
from app.core.retry import RetryExecutor, RetryPolicy
from app.schemas.smtp_schema import (
    EmailDeliveryResult,
    OutboundEmail,
)


logger = get_logger(__name__)


class _TransientSMTPError(Exception):
    """Internal exception used only to identify retryable SMTP failures."""


class SMTPService:

    def __init__(
        self,
        retry_executor: RetryExecutor | None = None,
    ) -> None:
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.email_address = settings.email_address
        self.email_password = settings.email_password

        self.retry_executor = retry_executor or RetryExecutor(
            RetryPolicy(
                max_attempts=3,
                initial_delay_seconds=1.0,
                maximum_delay_seconds=5.0,
                exponential_base=2.0,
                jitter_seconds=0.25,
            )
        )

    def _build_message(
        self,
        outbound_email: OutboundEmail,
    ) -> EmailMessage:

        message = EmailMessage()

        message_id = make_msgid(
            domain=self.email_address.split("@")[-1]
        )

        message["From"] = self.email_address
        message["To"] = str(
            outbound_email.recipient_email
        )
        message["Subject"] = outbound_email.subject
        message["Date"] = formatdate(localtime=False)
        message["Message-ID"] = message_id

        if outbound_email.reply_to:
            message["Reply-To"] = str(
                outbound_email.reply_to
            )

        message.set_content(
            outbound_email.plain_text_body
        )

        if outbound_email.html_body:
            message.add_alternative(
                outbound_email.html_body,
                subtype="html",
            )

        return message

    def _deliver_message(
        self,
        message: EmailMessage,
    ) -> None:

        tls_context = ssl.create_default_context()

        try:
            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port,
                timeout=30,
            ) as smtp_connection:

                smtp_connection.ehlo()

                smtp_connection.starttls(
                    context=tls_context
                )

                smtp_connection.ehlo()

                smtp_connection.login(
                    self.email_address,
                    self.email_password,
                )

                refused_recipients = (
                    smtp_connection.send_message(message)
                )

                if refused_recipients:
                    raise SMTPSendError(
                        "SMTP server refused one or more recipients.",
                        context={
                            "refused_recipients": list(
                                refused_recipients.keys()
                            ),
                        },
                    )

        except smtplib.SMTPAuthenticationError as exc:
            raise SMTPAuthenticationError(
                context={
                    "smtp_server": self.smtp_server,
                }
            ) from exc

        except smtplib.SMTPRecipientsRefused as exc:
            raise SMTPSendError(
                "SMTP server refused one or more recipients.",
                context={
                    "refused_recipients": list(
                        exc.recipients.keys()
                    ),
                },
            ) from exc

        except smtplib.SMTPResponseException as exc:
            smtp_code = exc.smtp_code

            if 400 <= smtp_code < 500:
                raise _TransientSMTPError(
                    f"Transient SMTP response: {smtp_code}"
                ) from exc

            raise SMTPSendError(
                "Permanent SMTP response failure.",
                context={
                    "smtp_code": smtp_code,
                },
            ) from exc

        except (
            smtplib.SMTPConnectError,
            smtplib.SMTPServerDisconnected,
            ConnectionError,
            TimeoutError,
            OSError,
        ) as exc:
            raise _TransientSMTPError(
                "Transient SMTP connection failure."
            ) from exc

        except SMTPSendError:
            raise

        except smtplib.SMTPException as exc:
            raise SMTPSendError(
                context={
                    "exception_type": type(exc).__name__,
                }
            ) from exc

    def send_email(
        self,
        outbound_email: OutboundEmail,
    ) -> EmailDeliveryResult:

        message = self._build_message(
            outbound_email
        )

        message_id = message["Message-ID"]

        log_event(
            logger,
            logging.INFO,
            LogEvent.SMTP_SEND_STARTED,
            "SMTP email delivery started.",
            recipient=str(
                outbound_email.recipient_email
            ),
            message_id=message_id,
        )

        try:
            self.retry_executor.execute(
                self._deliver_message,
                message,
                retry_on=(_TransientSMTPError,),
                operation_name="smtp_email_delivery",
            )

        except RetryExhaustedError as exc:
            log_event(
                logger,
                logging.ERROR,
                LogEvent.SMTP_SEND_FAILED,
                "SMTP connection failed after retry exhaustion.",
                recipient=str(
                    outbound_email.recipient_email
                ),
                exception_type=type(exc).__name__,
            )

            raise SMTPConnectionError(
                context={
                    "smtp_server": self.smtp_server,
                    "smtp_port": self.smtp_port,
                }
            ) from exc

        except SMTPAuthenticationError as exc:
            log_event(
                logger,
                logging.ERROR,
                LogEvent.SMTP_SEND_FAILED,
                "SMTP authentication failed.",
                exception_type=type(exc).__name__,
            )

            raise

        except SMTPSendError as exc:
            log_event(
                logger,
                logging.ERROR,
                LogEvent.SMTP_SEND_FAILED,
                "SMTP message delivery failed.",
                recipient=str(
                    outbound_email.recipient_email
                ),
                exception_type=type(exc).__name__,
            )

            raise

        log_event(
            logger,
            logging.INFO,
            LogEvent.SMTP_SEND_SUCCEEDED,
            "SMTP email delivery succeeded.",
            recipient=str(
                outbound_email.recipient_email
            ),
            message_id=message_id,
        )

        return EmailDeliveryResult(
            success=True,
            recipient_email=outbound_email.recipient_email,
            message_id=message_id,
        )
