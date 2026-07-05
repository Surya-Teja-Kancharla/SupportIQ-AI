from datetime import datetime, timezone

from app.schemas.email_schema import ParsedEmail
from app.schemas.ticket_analysis_schema import TicketAnalysisRequest
from app.services.groq_llm_service import GroqLLMService


def main() -> None:
    email = ParsedEmail(
        message_id="<groq-smoke-test-001@supportiq.local>",
        sender_name="Rahul Sharma",
        sender_email="rahul.sharma@example.com",
        subject="Production payment API is completely unavailable",
        body=(
            "Our production payment API has been returning HTTP 503 errors "
            "for the last 25 minutes. None of our customers can complete "
            "payments. This is affecting all production transactions. "
            "Please investigate immediately."
        ),
        received_at=datetime.now(timezone.utc),
    )

    request = TicketAnalysisRequest(
        email=email,
        attachment_text=None,
    )

    service = GroqLLMService()

    result = service.analyze_ticket(request)

    print("\nREAL GROQ TICKET ANALYSIS")
    print("=" * 60)
    print(result.model_dump_json(indent=2))
    print("=" * 60)


if __name__ == "__main__":
    main()
