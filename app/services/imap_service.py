import email
import imaplib
import logging

from app.config.settings import settings
from app.core.constants import LogEvent
from app.core.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailFetchError,
    MailboxSelectionError,
)
from app.core.logging import get_logger, log_event
from app.schemas.email_schema import ParsedEmail
from app.services.email_parser import parse_email


logger = get_logger(__name__)


class IMAPService:

    def __init__(self) -> None:
        self.connection: imaplib.IMAP4_SSL | None = None

    def connect(self) -> None:

        log_event(
            logger,
            logging.INFO,
            LogEvent.IMAP_CONNECTION_STARTED,
            "IMAP connection started.",
            imap_server=settings.imap_server,
            mailbox=settings.email_folder,
        )

        try:
            self.connection = imaplib.IMAP4_SSL(
                settings.imap_server
            )

            self.connection.login(
                settings.email_address,
                settings.email_password,
            )

        except imaplib.IMAP4.error as exc:
            self.connection = None

            raise EmailAuthenticationError(
                context={
                    "imap_server": settings.imap_server,
                }
            ) from exc

        except (
            ConnectionError,
            TimeoutError,
            OSError,
        ) as exc:
            self.connection = None

            raise EmailConnectionError(
                context={
                    "imap_server": settings.imap_server,
                }
            ) from exc

        status, _ = self.connection.select(
            settings.email_folder
        )

        if status != "OK":
            raise MailboxSelectionError(
                context={
                    "mailbox": settings.email_folder,
                }
            )

        log_event(
            logger,
            logging.INFO,
            LogEvent.IMAP_CONNECTION_SUCCEEDED,
            "IMAP connection succeeded.",
            mailbox=settings.email_folder,
        )

    def disconnect(self) -> None:
        if self.connection is None:
            return

        try:
            self.connection.logout()
        finally:
            self.connection = None

    def fetch_unread_emails(
        self,
    ) -> list[tuple[bytes, ParsedEmail]]:

        if self.connection is None:
            raise EmailConnectionError(
                "IMAP connection has not been established."
            )

        log_event(
            logger,
            logging.INFO,
            LogEvent.EMAIL_FETCH_STARTED,
            "Unread email retrieval started.",
        )

        try:
            status, search_data = (
                self.connection.search(
                    None,
                    "UNSEEN",
                )
            )

            if status != "OK":
                raise EmailFetchError(
                    "Unable to search the support inbox."
                )

            imap_message_ids = (
                search_data[0].split()
            )

            parsed_emails = []

            for imap_message_id in imap_message_ids:

                status, message_data = (
                    self.connection.fetch(
                        imap_message_id,
                        "(BODY.PEEK[])",
                    )
                )

                if status != "OK":
                    log_event(
                        logger,
                        logging.WARNING,
                        LogEvent.EMAIL_FETCH_FAILED,
                        "Individual email fetch failed.",
                        imap_message_id=(
                            imap_message_id.decode(
                                errors="replace"
                            )
                        ),
                    )
                    continue

                raw_email = None

                for response_part in message_data:
                    if (
                        isinstance(
                            response_part,
                            tuple,
                        )
                        and len(response_part) > 1
                    ):
                        raw_email = response_part[1]
                        break

                if raw_email is None:
                    continue

                try:
                    message = email.message_from_bytes(
                        raw_email
                    )

                    parsed_email = parse_email(
                        message
                    )

                except Exception:
                    logger.exception(
                        "Email parsing failed.",
                        extra={
                            "event": str(
                                LogEvent
                                .EMAIL_PROCESSING_FAILED
                            ),
                            "imap_message_id": (
                                imap_message_id.decode(
                                    errors="replace"
                                )
                            ),
                        },
                    )
                    continue

                parsed_emails.append(
                    (
                        imap_message_id,
                        parsed_email,
                    )
                )

        except EmailFetchError:
            raise

        except imaplib.IMAP4.error as exc:
            raise EmailFetchError(
                "IMAP operation failed."
            ) from exc

        log_event(
            logger,
            logging.INFO,
            LogEvent.EMAIL_FETCH_SUCCEEDED,
            "Unread email retrieval succeeded.",
            message_count=len(parsed_emails),
        )

        return parsed_emails

    def mark_as_seen(
        self,
        imap_message_id: bytes,
    ) -> None:

        if self.connection is None:
            raise EmailConnectionError(
                "IMAP connection has not been established."
            )

        try:
            status, _ = self.connection.store(
                imap_message_id,
                "+FLAGS",
                "\\Seen",
            )

        except imaplib.IMAP4.error as exc:
            raise EmailFetchError(
                "Unable to update email flags."
            ) from exc

        if status != "OK":
            raise EmailFetchError(
                "Unable to mark email as seen."
            )
