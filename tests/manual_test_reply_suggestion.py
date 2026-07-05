from datetime import datetime, timezone

from app.schemas.email_schema import ParsedEmail
from app.schemas.ticket_analysis_schema import TicketAnalysisRequest
from app.services.groq_llm_service import GroqLLMService
from app.services.reply_suggestion_service import ReplySuggestionService
from app.services.ticket_analysis_normalizer import TicketAnalysisNormalizer


def make_sample_email() -> ParsedEmail:
    """
    Create a realistic sample customer-support email for manual verification.
    """

    return ParsedEmail(
        message_id="manual-reply-suggestion-001",
        sender_name="Rahul Sharma",
        sender_email="rahul.sharma@example.com",
        subject="Unable to complete payment",
        body=(
            "Hello Support Team,\n\n"
            "I have been trying to complete a payment for the last "
            "30 minutes, but every attempt fails with an error message. "
            "I tried again several times and the payment still does not "
            "go through.\n\n"
            "Please help me understand what I should do next.\n\n"
            "Regards,\n"
            "Rahul Sharma"
        ),
        received_at=datetime.now(timezone.utc),
    )


def main() -> None:
    """
    Execute the complete real-provider reply-suggestion verification pipeline.

    Pipeline:

    ParsedEmail
        -> Groq ticket analysis
        -> TicketAnalysisResponse validation
        -> deterministic normalization
        -> ReplySuggestionService
        -> Groq reply generation
        -> ReplySuggestionResponse validation
        -> deterministic reply normalization
        -> print results

    This script performs real Groq API calls and must not be included in the
    automated pytest suite.
    """

    email = make_sample_email()

    llm_service = GroqLLMService()

    ticket_analysis_request = TicketAnalysisRequest(
        email=email,
    )

    print("=" * 70)
    print("REAL GROQ REPLY SUGGESTION PIPELINE")
    print("=" * 70)

    print("\n1. CUSTOMER EMAIL")
    print("-" * 70)
    print(f"Sender:  {email.sender_name} <{email.sender_email}>")
    print(f"Subject: {email.subject}")
    print(f"Body:\n{email.body}")

    print("\n2. REAL GROQ TICKET ANALYSIS")
    print("-" * 70)

    ticket_analysis = llm_service.analyze_ticket(
        ticket_analysis_request
    )

    print(
        ticket_analysis.model_dump_json(
            indent=2,
        )
    )

    print("\n3. DETERMINISTIC NORMALIZATION")
    print("-" * 70)

    normalizer = TicketAnalysisNormalizer()

    normalized_analysis = normalizer.normalize(
        ticket_analysis
    )

    print(
        normalized_analysis.model_dump_json(
            indent=2,
        )
    )

    print("\n4. REAL GROQ REPLY SUGGESTION")
    print("-" * 70)

    reply_suggestion_service = ReplySuggestionService(
        llm_service=llm_service,
    )

    reply_suggestion = (
        reply_suggestion_service.generate_suggestion(
            email=email,
            normalized_analysis=normalized_analysis,
        )
    )

    print(reply_suggestion.suggested_reply)

    print("\n5. VALIDATED REPLY RESPONSE")
    print("-" * 70)

    print(
        reply_suggestion.model_dump_json(
            indent=2,
        )
    )

    print("\n" + "=" * 70)
    print("MANUAL REPLY SUGGESTION VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
