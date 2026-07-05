from datetime import datetime, timezone
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime, parseaddr

from bs4 import BeautifulSoup

from app.schemas.email_schema import ParsedEmail
from app.services.attachment_service import save_attachment


def decode_mime_header(value: str | None) -> str:
    if not value:
        return ""

    decoded_parts = decode_header(value)

    result = []

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(
                part.decode(
                    encoding or "utf-8",
                    errors="replace",
                )
            )
        else:
            result.append(part)

    return "".join(result)


def decode_payload(part: Message) -> str:
    payload = part.get_payload(decode=True)

    if payload is None:
        return ""

    charset = part.get_content_charset() or "utf-8"

    return payload.decode(
        charset,
        errors="replace",
    )


def extract_body(message: Message) -> str:
    plain_text_body = ""
    html_body = ""

    if message.is_multipart():
        for part in message.walk():
            content_disposition = (
                part.get_content_disposition()
            )

            if content_disposition == "attachment":
                continue

            content_type = part.get_content_type()

            if content_type == "text/plain" and not plain_text_body:
                plain_text_body = decode_payload(part)

            elif content_type == "text/html" and not html_body:
                html_body = decode_payload(part)

    else:
        content_type = message.get_content_type()

        if content_type == "text/plain":
            plain_text_body = decode_payload(message)

        elif content_type == "text/html":
            html_body = decode_payload(message)

    if plain_text_body.strip():
        return plain_text_body.strip()

    if html_body.strip():
        soup = BeautifulSoup(
            html_body,
            "lxml",
        )

        return soup.get_text(
            separator="\n",
            strip=True,
        )

    return ""


def extract_received_at(message: Message) -> datetime:
    date_header = message.get("Date")

    if not date_header:
        return datetime.now(timezone.utc)

    try:
        received_at = parsedate_to_datetime(date_header)

        if received_at.tzinfo is None:
            received_at = received_at.replace(
                tzinfo=timezone.utc
            )

        return received_at

    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def parse_email(message: Message) -> ParsedEmail:
    raw_sender = decode_mime_header(
        message.get("From")
    )

    sender_name, sender_email = parseaddr(
        raw_sender
    )

    subject = decode_mime_header(
        message.get("Subject")
    )

    message_id = (
        message.get("Message-ID")
        or message.get("Message-Id")
        or ""
    ).strip()

    attachments = []

    for part in message.walk():
        if (
            part.get_content_disposition()
            != "attachment"
        ):
            continue

        filename = part.get_filename()

        if not filename:
            continue

        filename = decode_mime_header(filename)

        content = part.get_payload(decode=True)

        if content is None:
            continue

        attachment = save_attachment(
            filename=filename,
            content=content,
            content_type=part.get_content_type(),
        )

        if attachment:
            attachments.append(attachment)

    return ParsedEmail(
        message_id=message_id,
        sender_name=sender_name or None,
        sender_email=sender_email,
        subject=subject or "(No Subject)",
        body=extract_body(message),
        received_at=extract_received_at(message),
        attachments=attachments,
    )
