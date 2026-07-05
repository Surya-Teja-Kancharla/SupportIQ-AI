from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from decimal import Decimal

from sqlalchemy import select

from app.models.ticket import Ticket
from app.models.ticket_audit_log import TicketAuditLog
from app.models.workflow_execution import WorkflowExecution
from app.repositories.attachment_repository import (
    AttachmentRepository,
)
from app.repositories.audit_repository import AuditRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)
from app.schemas.email_schema import ParsedEmail
from app.schemas.reply_suggestion_schema import (
    ReplySuggestionResponse,
)
from app.schemas.ticket_analysis_schema import (
    TicketAnalysisResponse,
)
from app.services.priority_service import PriorityService
from app.services.routing_service import RoutingService
from app.services.ticket_analysis_normalizer import (
    TicketAnalysisNormalizer,
)
from app.services.ticket_service import TicketService
from app.services.workflow_service import WorkflowService


def build_email() -> ParsedEmail:
    suffix = uuid4().hex[:12]

    return ParsedEmail(
        message_id=f"<hour16-db-{suffix}@example.com>",
        sender_name="Production Customer",
        sender_email="customer@example.com",
        subject="Production outage affecting all customers",
        body=(
            "We have a production outage. "
            "The complete service unavailable condition "
            "is affecting all customers."
        ),
        received_at=datetime.now(timezone.utc),
        attachments=[],
    )


def build_ai_analysis() -> TicketAnalysisResponse:
    return TicketAnalysisResponse(
        customer_name="Production Customer",
        company="Example Corp",
        issue_summary="Production outage",
        detailed_description=(
            "The production service is completely unavailable "
            "for all customers."
        ),
        category="Technical Support",
        priority="High",
        sentiment="Negative",
        product_service="Production Service",
        suggested_department="Technical Support",
        tags=["production", "outage"],
        confidence_score=0.97,
    )


def test_email_groq_mock_database_workflow(
    db_session,
    unique_suffix,
):
    llm_service = MagicMock()
    reply_suggestion_service = MagicMock()

    llm_service.analyze_ticket.return_value = (
        build_ai_analysis()
    )

    reply_suggestion_service.generate_suggestion.return_value = (
        ReplySuggestionResponse(
            suggested_reply=(
                "We are investigating the production outage."
            )
        )
    )

    ticket_repository = TicketRepository(db_session)

    attachment_repository = AttachmentRepository(
        db_session
    )

    audit_repository = AuditRepository(db_session)

    workflow_execution_repository = (
        WorkflowExecutionRepository(db_session)
    )

    ticket_service = TicketService(
        ticket_repository=ticket_repository,
        attachment_repository=attachment_repository,
        audit_repository=audit_repository,
        ticket_number_generator=lambda: (
            f"SUP-H16-{unique_suffix[:12]}"
        ),
    )

    workflow_service = WorkflowService(
        session=db_session,
        llm_service=llm_service,
        ticket_analysis_normalizer=(
            TicketAnalysisNormalizer()
        ),
        priority_service=PriorityService(),
        routing_service=RoutingService(),
        reply_suggestion_service=reply_suggestion_service,
        ticket_service=ticket_service,
        workflow_execution_repository=(
            workflow_execution_repository
        ),
    )

    email = build_email()

    result = workflow_service.process_email(email)

    llm_service.analyze_ticket.assert_called_once()

    reply_suggestion_service.generate_suggestion.assert_called_once()

    persisted_ticket = db_session.scalar(
        select(Ticket).where(
            Ticket.id == result.ticket_id
        )
    )

    assert persisted_ticket is not None

    assert persisted_ticket.ticket_number == (
        f"SUP-H16-{unique_suffix[:12]}"
    )

    assert persisted_ticket.sender_email == (
        "customer@example.com"
    )

    assert persisted_ticket.category == (
        "Technical Support"
    )

    assert persisted_ticket.priority == "Critical"

    assert persisted_ticket.assigned_team == (
        "Technical Support"
    )

    assert persisted_ticket.confidence_score == Decimal("0.97")

    assert persisted_ticket.suggested_reply == (
        "We are investigating the production outage."
    )

    persisted_audits = list(
        db_session.scalars(
            select(TicketAuditLog).where(
                TicketAuditLog.ticket_id
                == persisted_ticket.id
            )
        )
    )

    assert len(persisted_audits) == 1

    assert persisted_audits[0].action == "ticket_created"

    persisted_execution = db_session.scalar(
        select(WorkflowExecution).where(
            WorkflowExecution.message_id
            == email.message_id
        )
    )

    assert persisted_execution is not None

    assert persisted_execution.ticket_id == (
        persisted_ticket.id
    )

    assert persisted_execution.message_id == (
        email.message_id
    )
