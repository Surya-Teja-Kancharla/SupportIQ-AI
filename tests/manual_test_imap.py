from app.services.imap_service import IMAPService


def main() -> None:
    imap_service = IMAPService()

    try:
        print("Connecting to support inbox...")

        imap_service.connect()

        print("Connected successfully.")

        emails = imap_service.fetch_unread_emails()

        print(
            f"Unread emails found: {len(emails)}"
        )

        for imap_message_id, parsed_email in emails:
            print("-" * 70)
            print(f"IMAP ID: {imap_message_id!r}")
            print(f"Message-ID: {parsed_email.message_id}")
            print(f"From: {parsed_email.sender_name}")
            print(f"Email: {parsed_email.sender_email}")
            print(f"Subject: {parsed_email.subject}")
            print(f"Received: {parsed_email.received_at}")
            print(f"Body:\n{parsed_email.body}")
            print(
                f"Attachments: "
                f"{len(parsed_email.attachments)}"
            )

            for attachment in parsed_email.attachments:
                print(
                    f"  - {attachment.original_filename}"
                    f" -> {attachment.file_path}"
                )

    finally:
        imap_service.disconnect()


if __name__ == "__main__":
    main()
