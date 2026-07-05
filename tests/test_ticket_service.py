from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from app.schemas.email_schema import ParsedAttachment, ParsedEmail
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


def build_email() -> ParsedEmail:
    return ParsedEmail(
        sender_name="Customer",
        sender_email="customer@example.com",
        subject="Payment API unavailable",
        body="Our production payment API is completely unavailable.",
        received_at=datetime.now(timezone.utc),
        message_id="<hour9-ticket-service@example.com>",
        attachments=[
            ParsedAttachment(
                original_filename="error.png",
                stored_filename="abc123_error.png",
                file_path="uploads/attachments/abc123_error.png",
                size_bytes=1024,
                content_type="image/png",
            ),
            ParsedAttachment(
                original_filename="logs.txt",
                stored_filename="def456_logs.txt",
                file_path="uploads/attachments/def456_logs.txt",
                size_bytes=2048,
                content_type="text/plain",
            ),
        ],
    )


def build_analysis() -> NormalizedTicketAnalysis:
    return NormalizedTicketAnalysis(
        customer_name="Customer",
        company="Example Corp",
        issue_summary="Payment API unavailable",
        detailed_description=(
            "The production payment API is completely unavailable."
        ),
        category="Technical Support",
        ai_recommended_priority="High",
        sentiment="Negative",
        product_service="Payment API",
        suggested_department="Technical Support",
        tags=["payment-api", "production-outage"],
        confidence_score=0.95,
        normalization_metadata=NormalizationMetadata(
            original_category="Technical Support",
            original_priority="High",
            original_sentiment="Negative",
            original_department="Technical Support",
            category_was_normalized=False,
            priority_was_normalized=False,
            sentiment_was_normalized=False,
            department_was_normalized=False,
            removed_duplicate_tags=0,
            removed_empty_tags=0,
            confidence_was_clamped=False,
        ),
    )


def build_priority_decision() -> PriorityDecision:
    return PriorityDecision(
        ai_recommended_priority="High",
        final_priority="Critical",
        applied_rule=(
            "Matched Critical priority business rule: production outage"
        ),
        was_overridden=True,
    )


def build_routing_decision() -> RoutingDecision:
    return RoutingDecision(
        category="Technical Support",
        assigned_team="Technical Support",
        applied_rule=(
            "Category 'Technical Support' routed to 'Technical Support'"
        ),
    )


def build_reply_suggestion() -> ReplySuggestionResponse:
    return ReplySuggestionResponse(
        suggested_reply=(
            "Hello Customer, we are investigating the production "
            "payment API outage and will provide updates as soon as possible."
        )
    )


def build_service():
    ticket_repository = Mock()
    attachment_repository = Mock()
    audit_repository = Mock()

    ticket_repository.create.side_effect = lambda ticket: SimpleNamespace(
        id=101,
        ticket_number=ticket.ticket_number,
    )

    service = TicketService(
        ticket_repository=ticket_repository,
        attachment_repository=attachment_repository,
        audit_repository=audit_repository,
        ticket_number_generator=lambda: "SUP-20260705-TEST0001",
    )

    return (
        service,
        ticket_repository,
        attachment_repository,
        audit_repository,
    )


def create_ticket(service: TicketService):
    return service.create_ticket(
        build_email(),
        build_analysis(),
        build_priority_decision(),
        build_routing_decision(),
        build_reply_suggestion(),
    )


def test_create_ticket_persists_ticket():
    service, ticket_repository, _, _ = build_service()

    create_ticket(service)

    ticket_repository.create.assert_called_once()


def test_create_ticket_uses_final_priority():
    service, ticket_repository, _, _ = build_service()

    create_ticket(service)

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.priority == "Critical"


def test_create_ticket_uses_assigned_team():
    service, ticket_repository, _, _ = build_service()

    create_ticket(service)

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.assigned_team == "Technical Support"


def test_create_ticket_persists_priority_reason():
    service, ticket_repository, _, _ = build_service()

    create_ticket(service)

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.priority_reason == (
        "Matched Critical priority business rule: production outage"
    )


def test_create_ticket_persists_suggested_reply():
    service, ticket_repository, _, _ = build_service()

    create_ticket(service)

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.suggested_reply == (
        "Hello Customer, we are investigating the production "
        "payment API outage and will provide updates as soon as possible."
    )


def test_create_ticket_persists_all_attachments():
    service, _, attachment_repository, _ = build_service()

    create_ticket(service)

    assert attachment_repository.create.call_count == 2


def test_create_ticket_creates_ticket_created_audit_event():
    service, _, _, audit_repository = build_service()

    create_ticket(service)

    audit_repository.create.assert_called_once()

    audit_event = audit_repository.create.call_args.args[0]

    assert audit_event.action == "ticket_created"
    assert audit_event.ticket_id == 101


def test_create_ticket_returns_creation_result():
    service, _, _, _ = build_service()

    result = create_ticket(service)

    assert result.ticket_id == 101
    assert result.ticket_number == "SUP-20260705-TEST0001"


def test_create_ticket_does_not_mutate_email():
    service, _, _, _ = build_service()

    email = build_email()
    original_email = deepcopy(email)

    service.create_ticket(
        email,
        build_analysis(),
        build_priority_decision(),
        build_routing_decision(),
        build_reply_suggestion(),
    )

    assert email == original_email


def test_create_ticket_does_not_mutate_analysis():
    service, _, _, _ = build_service()

    analysis = build_analysis()
    original_analysis = deepcopy(analysis)

    service.create_ticket(
        build_email(),
        analysis,
        build_priority_decision(),
        build_routing_decision(),
        build_reply_suggestion(),
    )

    assert analysis == original_analysis


def test_create_ticket_repository_calls_are_limited_to_persistence_operations():
    service, ticket_repository, attachment_repository, audit_repository = (
        build_service()
    )

    create_ticket(service)

    assert ticket_repository.create.call_count == 1
    assert attachment_repository.create.call_count == 2
    assert audit_repository.create.call_count == 1


def test_create_ticket_uses_deterministic_injected_ticket_number():
    service, ticket_repository, _, _ = build_service()

    create_ticket(service)

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.ticket_number == "SUP-20260705-TEST0001"
