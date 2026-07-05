import email
import imaplib

from app.config.settings import settings
from app.schemas.email_schema import ParsedEmail
from app.services.email_parser import parse_email


class IMAPService:

    def __init__(self) -> None:
        self.connection: imaplib.IMAP4_SSL | None = None

    def connect(self) -> None:
        self.connection = imaplib.IMAP4_SSL(
            settings.imap_server
        )

        self.connection.login(
            settings.email_address,
            settings.email_password,
        )

        status, _ = self.connection.select(
            settings.email_folder
        )

        if status != "OK":
            raise RuntimeError(
                f"Unable to select email folder: "
                f"{settings.email_folder}"
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
            raise RuntimeError(
                "IMAP connection has not been established."
            )

        status, search_data = self.connection.search(
            None,
            "UNSEEN",
        )

        if status != "OK":
            raise RuntimeError(
                "Unable to search the support inbox."
            )

        imap_message_ids = search_data[0].split()

        parsed_emails = []

        for imap_message_id in imap_message_ids:
            status, message_data = self.connection.fetch(
                imap_message_id,
                "(BODY.PEEK[])",
            )

            if status != "OK":
                continue

            raw_email = None

            for response_part in message_data:
                if (
                    isinstance(response_part, tuple)
                    and len(response_part) > 1
                ):
                    raw_email = response_part[1]
                    break

            if raw_email is None:
                continue

            message = email.message_from_bytes(
                raw_email
            )

            parsed_email = parse_email(message)

            parsed_emails.append(
                (
                    imap_message_id,
                    parsed_email,
                )
            )

        return parsed_emails

    def mark_as_seen(
        self,
        imap_message_id: bytes,
    ) -> None:

        if self.connection is None:
            raise RuntimeError(
                "IMAP connection has not been established."
            )

        status, _ = self.connection.store(
            imap_message_id,
            "+FLAGS",
            "\\Seen",
        )

        if status != "OK":
            raise RuntimeError(
                "Unable to mark email as seen."
            )
