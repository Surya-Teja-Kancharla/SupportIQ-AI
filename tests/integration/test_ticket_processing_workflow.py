from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateWorkflowError
from app.schemas.email_schema import ParsedEmail
from app.schemas.ticket_analysis_schema import TicketAnalysisResponse
from app.schemas.reply_suggestion_schema import ReplySuggestionResponse
from app.services.priority_service import PriorityService
from app.services.routing_service import RoutingService
from app.services.ticket_analysis_normalizer import (
    TicketAnalysisNormalizer,
)
from app.services.ticket_service import TicketService
from app.services.workflow_service import WorkflowService


def build_email() -> ParsedEmail:
    return ParsedEmail(
        sender_name="Customer",
        sender_email="customer@example.com",
        subject="Production service outage",
        body=(
            "Our production service is completely unavailable. "
            "All customers are affected."
        ),
        received_at=datetime.now(timezone.utc),
        message_id="<hour9-integration@example.com>",
        attachments=[],
    )


def build_ai_analysis() -> TicketAnalysisResponse:
    return TicketAnalysisResponse(
        customer_name="Customer",
        company="Example Corp",
        issue_summary="Production service outage",
        detailed_description=(
            "The production service is completely unavailable "
            "and all customers are affected."
        ),
        category="Technical Support",
        priority="High",
        sentiment="Negative",
        product_service="Production Service",
        suggested_department="Technical Support",
        tags=["production", "outage"],
        confidence_score=0.97,
    )


def build_reply_suggestion() -> ReplySuggestionResponse:
    return ReplySuggestionResponse(
        suggested_reply=(
            "Hello Customer, we are investigating the production "
            "service outage and will provide updates as soon as possible."
        )
    )


def build_workflow():
    session = Mock(spec=Session)

    llm_service = Mock()
    reply_suggestion_service = Mock()

    ticket_repository = Mock()
    attachment_repository = Mock()
    audit_repository = Mock()
    workflow_execution_repository = Mock()

    llm_service.analyze_ticket.return_value = build_ai_analysis()

    reply_suggestion_service.generate_suggestion.return_value = (
        build_reply_suggestion()
    )

    workflow_execution_repository.get_by_message_id.return_value = None

    def persist_ticket(ticket):
        ticket.id = 501
        return ticket

    ticket_repository.add.side_effect = persist_ticket

    ticket_service = TicketService(
        ticket_repository=ticket_repository,
        attachment_repository=attachment_repository,
        audit_repository=audit_repository,
        ticket_number_generator=lambda: "SUP-20260705-INTEGRATION",
    )

    workflow_service = WorkflowService(
        session=session,
        llm_service=llm_service,
        ticket_analysis_normalizer=TicketAnalysisNormalizer(),
        priority_service=PriorityService(),
        routing_service=RoutingService(),
        reply_suggestion_service=reply_suggestion_service,
        ticket_service=ticket_service,
        workflow_execution_repository=workflow_execution_repository,
    )

    return SimpleNamespace(
        workflow_service=workflow_service,
        session=session,
        llm_service=llm_service,
        reply_suggestion_service=reply_suggestion_service,
        ticket_repository=ticket_repository,
        attachment_repository=attachment_repository,
        audit_repository=audit_repository,
        workflow_repository=workflow_execution_repository,
    )


def test_complete_ticket_processing_workflow_succeeds():
    context = build_workflow()

    result = context.workflow_service.process_email(
        build_email()
    )

    context.llm_service.analyze_ticket.assert_called_once()

    context.ticket_repository.add.assert_called_once()

    context.audit_repository.add.assert_called_once()

    context.workflow_repository.add.assert_called_once()

    context.session.commit.assert_called_once_with()
    context.session.rollback.assert_not_called()

    persisted_ticket = (
        context.ticket_repository.add.call_args.args[0]
    )

    persisted_audit = (
        context.audit_repository.add.call_args.args[0]
    )

    persisted_execution = (
        context.workflow_repository.add.call_args.args[0]
    )

    assert persisted_ticket.priority == "Critical"
    assert persisted_ticket.assigned_team == "Technical Support"

    assert persisted_ticket.priority_reason == (
        result.priority_decision.applied_rule
    )

    assert persisted_ticket.suggested_reply == (
        "Hello Customer, we are investigating the production "
        "service outage and will provide updates as soon as possible."
    )

    assert persisted_audit.ticket_id == 501
    assert persisted_audit.action == "ticket_created"

    assert persisted_execution.ticket_id == 501
    assert persisted_execution.message_id == (
        "<hour9-integration@example.com>"
    )

    assert result.ticket_id == 501
    assert result.ticket_number == (
        "SUP-20260705-INTEGRATION"
    )
    assert result.priority_decision.final_priority == "Critical"
    assert result.routing_decision.assigned_team == (
        "Technical Support"
    )


def test_complete_ticket_processing_workflow_rolls_back_on_persistence_failure():
    context = build_workflow()

    original_error = RuntimeError(
        "workflow execution persistence failed"
    )

    context.workflow_repository.add.side_effect = original_error

    with pytest.raises(RuntimeError) as exc_info:
        context.workflow_service.process_email(build_email())

    assert exc_info.value is original_error

    context.ticket_repository.add.assert_not_called()
    context.audit_repository.add.assert_not_called()
    context.workflow_repository.add.assert_called_once()

    context.session.rollback.assert_not_called()
    context.session.commit.assert_not_called()


def test_duplicate_message_id_stops_complete_workflow():
    context = build_workflow()

    context.workflow_repository.get_by_message_id.return_value = (
        SimpleNamespace(
            id=99,
            message_id="<hour9-integration@example.com>",
        )
    )

    with pytest.raises(DuplicateWorkflowError):
        context.workflow_service.process_email(build_email())

    context.llm_service.analyze_ticket.assert_not_called()

    context.ticket_repository.add.assert_not_called()
    context.attachment_repository.add.assert_not_called()
    context.audit_repository.add.assert_not_called()
    context.workflow_repository.add.assert_not_called()

    context.session.commit.assert_not_called()

    context.session.rollback.assert_not_called()
