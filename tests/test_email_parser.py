from datetime import timezone
from email.message import EmailMessage

from app.services.email_parser import (
    decode_mime_header,
    extract_body,
    extract_received_at,
    parse_email,
)


def test_decode_mime_header_returns_empty_string_for_none():
    assert decode_mime_header(None) == ""


def test_decode_mime_header_decodes_utf8_subject():
    encoded_subject = "=?utf-8?b?U3VwcG9ydCBUZXN0IOKckw==?="

    result = decode_mime_header(encoded_subject)

    assert result == "Support Test ✓"


def test_decode_mime_header_preserves_plain_text():
    subject = "Unable to login"

    result = decode_mime_header(subject)

    assert result == subject


def test_extract_body_from_plain_text_email():
    message = EmailMessage()

    message.set_content(
        "Hello Support,\n\n"
        "I cannot login to my account.\n\n"
        "Regards,\n"
        "Customer"
    )

    result = extract_body(message)

    assert "Hello Support" in result
    assert "I cannot login to my account." in result
    assert "Regards" in result


def test_extract_body_prefers_plain_text_over_html():
    message = EmailMessage()

    message.set_content("Plain text support request.")

    message.add_alternative(
        """
        <html>
            <body>
                <p>HTML support request.</p>
            </body>
        </html>
        """,
        subtype="html",
    )

    result = extract_body(message)

    assert result == "Plain text support request."
    assert "HTML support request" not in result


def test_extract_body_falls_back_to_html():
    message = EmailMessage()

    message.set_content(
        """
        <html>
            <body>
                <h1>Support Request</h1>
                <p>The application crashes.</p>
            </body>
        </html>
        """,
        subtype="html",
    )

    result = extract_body(message)

    assert "Support Request" in result
    assert "The application crashes." in result
    assert "<html>" not in result
    assert "<p>" not in result


def test_extract_body_returns_empty_string_when_body_is_unavailable():
    message = EmailMessage()

    message.set_type("application/octet-stream")
    message.set_payload(b"binary content")

    result = extract_body(message)

    assert result == ""


def test_extract_received_at_parses_valid_date():
    message = EmailMessage()

    message["Date"] = "Sun, 05 Jul 2026 12:15:51 +0530"

    result = extract_received_at(message)

    assert result.year == 2026
    assert result.month == 7
    assert result.day == 5
    assert result.hour == 12
    assert result.minute == 15
    assert result.utcoffset().total_seconds() == 19800


def test_extract_received_at_returns_utc_for_missing_date():
    message = EmailMessage()

    result = extract_received_at(message)

    assert result.tzinfo == timezone.utc


def test_extract_received_at_handles_malformed_date():
    message = EmailMessage()

    message["Date"] = "definitely-not-a-valid-date"

    result = extract_received_at(message)

    assert result.tzinfo == timezone.utc


def test_parse_email_extracts_required_metadata():
    message = EmailMessage()

    message["From"] = "Test Customer <customer@example.com>"
    message["To"] = "support@example.com"
    message["Subject"] = "Unable to login"
    message["Date"] = "Sun, 05 Jul 2026 12:15:51 +0530"
    message["Message-ID"] = "<support-test-001@example.com>"

    message.set_content(
        "Hello Support,\n\n"
        "I cannot login after resetting my password."
    )

    result = parse_email(message)

    assert result.message_id == "<support-test-001@example.com>"
    assert result.sender_name == "Test Customer"
    assert str(result.sender_email) == "customer@example.com"
    assert result.subject == "Unable to login"
    assert "cannot login" in result.body
    assert result.attachments == []


def test_parse_email_uses_default_subject_when_missing():
    message = EmailMessage()

    message["From"] = "customer@example.com"
    message["Date"] = "Sun, 05 Jul 2026 12:15:51 +0530"
    message["Message-ID"] = "<support-test-002@example.com>"

    message.set_content("Support request.")

    result = parse_email(message)

    assert result.subject == "(No Subject)"
