from datetime import datetime, timezone

from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.email_schema import ParsedEmail
from app.schemas.normalized_ticket_schema import (
    NormalizationMetadata,
    NormalizedTicketAnalysis,
)
from app.schemas.reply_suggestion_schema import ReplySuggestionResponse
from app.schemas.ticket_decision_schema import (
    PriorityDecision,
    RoutingDecision,
)
from app.services.ticket_service import TicketService

from decimal import Decimal


def build_parsed_email(
    unique_suffix: str,
) -> ParsedEmail:
    return ParsedEmail(
        message_id=(
            f"<hour16-email-ticket-{unique_suffix}@example.com>"
        ),
        sender_name="Hour 16 Customer",
        sender_email=f"customer-{unique_suffix}@example.com",
        subject="Unable to access customer account",
        body=(
            "I cannot access my customer account after resetting "
            "my password."
        ),
        received_at=datetime.now(timezone.utc),
        attachments=[],
    )


def build_normalization_metadata(
    *,
    priority: str,
) -> NormalizationMetadata:
    return NormalizationMetadata(
        original_category="Account Access",
        original_priority=priority,
        original_sentiment="Negative",
        original_department="Customer Success",
        category_was_normalized=False,
        priority_was_normalized=False,
        sentiment_was_normalized=False,
        department_was_normalized=False,
        removed_duplicate_tags=0,
        removed_empty_tags=0,
        confidence_was_clamped=False,
    )


def build_analysis(
    *,
    summary: str,
    description: str,
    priority: str,
    sentiment: str,
    confidence_score: float,
) -> NormalizedTicketAnalysis:
    return NormalizedTicketAnalysis(
        customer_name="Hour 16 Customer",
        company="Example Corp",
        issue_summary=summary,
        detailed_description=description,
        category="Account Access",
        ai_recommended_priority=priority,
        sentiment=sentiment,
        product_service="Customer Portal",
        suggested_department="Customer Success",
        confidence_score=confidence_score,
        tags=[],
        normalization_metadata=build_normalization_metadata(
            priority=priority,
        ),
    )


def build_priority_decision(
    *,
    priority: str,
    reason: str,
) -> PriorityDecision:
    return PriorityDecision(
        ai_recommended_priority=priority,
        final_priority=priority,
        applied_rule=reason,
        was_overridden=False,
    )


def build_routing_decision() -> RoutingDecision:
    return RoutingDecision(
        category="Account Access",
        assigned_team="Customer Success",
        applied_rule="category_route",
    )


def build_reply_suggestion(
    suggested_reply: str,
) -> ReplySuggestionResponse:
    return ReplySuggestionResponse(
        suggested_reply=suggested_reply,
    )


def build_ticket_service(
    db_session,
) -> TicketService:
    return TicketService(
        ticket_repository=TicketRepository(db_session),
        attachment_repository=AttachmentRepository(db_session),
        audit_repository=AuditRepository(db_session),
    )


def create_ticket(
    ticket_service: TicketService,
    *,
    email: ParsedEmail,
    summary: str,
    description: str,
    priority: str,
    sentiment: str,
    confidence_score: float,
    priority_reason: str,
    suggested_reply: str,
):
    analysis = build_analysis(
        summary=summary,
        description=description,
        priority=priority,
        sentiment=sentiment,
        confidence_score=confidence_score,
    )

    priority_decision = build_priority_decision(
        priority=priority,
        reason=priority_reason,
    )

    routing_decision = build_routing_decision()

    reply_suggestion = build_reply_suggestion(
        suggested_reply,
    )

    return ticket_service.create_ticket(
        email=email,
        analysis=analysis,
        priority_decision=priority_decision,
        routing_decision=routing_decision,
        reply_suggestion=reply_suggestion,
    )


def test_email_to_ticket_workflow(
    db_session,
    unique_suffix,
):
    parsed_email = build_parsed_email(unique_suffix)

    ticket_repository = TicketRepository(db_session)

    ticket_service = TicketService(
        ticket_repository=ticket_repository,
        attachment_repository=AttachmentRepository(db_session),
        audit_repository=AuditRepository(db_session),
    )

    result = create_ticket(
        ticket_service,
        email=parsed_email,
        summary="Customer cannot access account.",
        description=(
            "Customer reports account access failure after "
            "resetting the password."
        ),
        priority="High",
        sentiment="Negative",
        confidence_score=0.96,
        priority_reason=(
            "The customer cannot access a core account feature."
        ),
        suggested_reply=(
            "We are investigating your account access issue."
        ),
    )

    db_session.commit()

    assert result.ticket_id > 0
    assert result.ticket_number

    persisted_ticket = ticket_repository.get_by_id(
        db_session,
        result.ticket_id,
    )

    assert persisted_ticket is not None

    assert persisted_ticket.id == result.ticket_id

    assert (
        persisted_ticket.ticket_number
        == result.ticket_number
    )

    assert (
        persisted_ticket.sender_email
        == parsed_email.sender_email
    )

    assert persisted_ticket.subject == parsed_email.subject
    assert persisted_ticket.body == parsed_email.body

    assert (
        persisted_ticket.summary
        == "Customer cannot access account."
    )

    assert persisted_ticket.category == "Account Access"
    assert persisted_ticket.priority == "High"
    assert persisted_ticket.sentiment == "Negative"

    assert persisted_ticket.product == "Customer Portal"

    assert (
        persisted_ticket.suggested_department
        == "Customer Success"
    )

    assert (
        persisted_ticket.assigned_team
        == "Customer Success"
    )

    assert persisted_ticket.confidence_score == Decimal("0.96")

    assert (
        persisted_ticket.suggested_reply
        == "We are investigating your account access issue."
    )


def test_email_to_ticket_persists_distinct_tickets(
    db_session,
    unique_suffix,
):
    ticket_repository = TicketRepository(db_session)

    ticket_service = TicketService(
        ticket_repository=ticket_repository,
        attachment_repository=AttachmentRepository(db_session),
        audit_repository=AuditRepository(db_session),
    )

    first_email = build_parsed_email(
        f"{unique_suffix}-first",
    )

    second_email = build_parsed_email(
        f"{unique_suffix}-second",
    )

    first_result = create_ticket(
        ticket_service,
        email=first_email,
        summary="First account access issue.",
        description="First customer account access failure.",
        priority="High",
        sentiment="Negative",
        confidence_score=0.95,
        priority_reason="Account access is unavailable.",
        suggested_reply="We are investigating the issue.",
    )

    second_result = create_ticket(
        ticket_service,
        email=second_email,
        summary="Second account access issue.",
        description="Second customer account access failure.",
        priority="Medium",
        sentiment="Neutral",
        confidence_score=0.90,
        priority_reason=(
            "Account access requires investigation."
        ),
        suggested_reply="We are reviewing the issue.",
    )

    db_session.commit()

    first_ticket = ticket_repository.get_by_id(
        db_session,
        first_result.ticket_id,
    )

    second_ticket = ticket_repository.get_by_id(
        db_session,
        second_result.ticket_id,
    )

    assert first_ticket is not None
    assert second_ticket is not None

    assert first_ticket.id != second_ticket.id

    assert (
        first_ticket.ticket_number
        != second_ticket.ticket_number
    )

    assert (
        first_ticket.sender_email
        != second_ticket.sender_email
    )


def test_email_to_ticket_rollback_does_not_persist_ticket(
    db_session,
    unique_suffix,
):
    parsed_email = build_parsed_email(
        f"{unique_suffix}-rollback",
    )

    ticket_repository = TicketRepository(db_session)

    ticket_service = TicketService(
        ticket_repository=ticket_repository,
        attachment_repository=AttachmentRepository(db_session),
        audit_repository=AuditRepository(db_session),
    )

    result = create_ticket(
        ticket_service,
        email=parsed_email,
        summary="Rollback account access issue.",
        description=(
            "Ticket should not survive transaction rollback."
        ),
        priority="Low",
        sentiment="Neutral",
        confidence_score=0.85,
        priority_reason="Integration rollback verification.",
        suggested_reply="We are reviewing your request.",
    )

    ticket_id = result.ticket_id

    assert ticket_id > 0

    db_session.rollback()

    persisted_ticket = ticket_repository.get_by_id(
        db_session,
        ticket_id,
    )

    assert persisted_ticket is None
