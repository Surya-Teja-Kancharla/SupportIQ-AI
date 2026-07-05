from app.core.logging import configure_logging
from app.schemas.smtp_schema import OutboundEmail
from app.services.smtp_service import SMTPService


def main() -> None:
    configure_logging()

    service = SMTPService()

    outbound_email = OutboundEmail(
        recipient_email="suryatejakancharla2005@gmail.com",
        subject="[SupportIQ AI] SMTP Integration Test",
        plain_text_body=(
            "This is a real SMTP integration test from SupportIQ AI.\n\n"
            "If you received this email, the SMTP transport layer "
            "is working correctly."
        ),
        html_body=(
            "<h2>SupportIQ AI</h2>"
            "<p>This is a real SMTP integration test.</p>"
            "<p>If you received this email, the SMTP transport "
            "layer is working correctly.</p>"
        ),
    )

    result = service.send_email(outbound_email)

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
