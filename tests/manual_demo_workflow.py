from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.ticket import Ticket
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)
from app.schemas.email_schema import ParsedEmail
from app.schemas.reply_suggestion_schema import ReplySuggestionResponse
from app.schemas.ticket_analysis_schema import TicketAnalysisResponse
from app.services.priority_service import PriorityService
from app.services.routing_service import RoutingService
from app.services.ticket_analysis_normalizer import TicketAnalysisNormalizer
from app.services.ticket_service import TicketService
from app.services.workflow_service import WorkflowService


def main() -> None:
    db = SessionLocal()

    try:
        suffix = uuid4().hex[:12]

        email = ParsedEmail(
            message_id=f"<demo-{suffix}@supportiq.local>",
            sender_name="Demo Customer",
            sender_email="demo.customer@example.com",
            subject="Production outage affecting all customers",
            body=(
                "Our production service is completely unavailable. "
                "All customers are affected and cannot use the service."
            ),
            received_at=datetime.now(timezone.utc),
            attachments=[],
        )

        llm_service = MagicMock()
        llm_service.analyze_ticket.return_value = TicketAnalysisResponse(
            customer_name="Demo Customer",
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

        reply_suggestion_service = MagicMock()
        reply_suggestion_service.generate_suggestion.return_value = (
            ReplySuggestionResponse(
                suggested_reply=(
                    "We have received your report regarding the production "
                    "service outage and the support team is reviewing the issue."
                )
            )
        )

        ticket_repository = TicketRepository(db)

        ticket_service = TicketService(
            ticket_repository=ticket_repository,
            attachment_repository=AttachmentRepository(db),
            audit_repository=AuditRepository(db),
            ticket_number_generator=lambda: f"SUP-DEMO-{suffix.upper()}",
        )

        workflow_service = WorkflowService(
            session=db,
            llm_service=llm_service,
            ticket_analysis_normalizer=TicketAnalysisNormalizer(),
            priority_service=PriorityService(),
            routing_service=RoutingService(),
            reply_suggestion_service=reply_suggestion_service,
            ticket_service=ticket_service,
            workflow_execution_repository=WorkflowExecutionRepository(db),
        )

        result = workflow_service.process_email(email)

        db.commit()

        persisted_ticket = db.scalar(
            select(Ticket).where(Ticket.id == result.ticket_id)
        )

        if persisted_ticket is None:
            raise RuntimeError("Demo ticket was not persisted.")

        print()
        print("=" * 60)
        print("SupportIQ AI Deterministic Demo Workflow")
        print("=" * 60)
        print(f"Ticket ID:       {persisted_ticket.id}")
        print(f"Ticket Number:   {persisted_ticket.ticket_number}")
        print(f"Subject:         {persisted_ticket.subject}")
        print(f"Category:        {persisted_ticket.category}")
        print(f"Priority:        {persisted_ticket.priority}")
        print(f"Assigned Team:   {persisted_ticket.assigned_team}")
        print(f"AI Confidence:   {persisted_ticket.confidence_score}")
        print(f"Status:          {persisted_ticket.status}")
        print("=" * 60)
        print()
        print("Demo ticket persisted successfully.")
        print("Refresh: http://127.0.0.1:8000/dashboard/tickets")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
