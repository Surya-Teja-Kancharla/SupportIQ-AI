from app.repositories import (
    AttachmentRepository,
    AuditRepository,
    TicketRepository,
    WorkflowExecutionRepository,
)
from app.schemas.dashboard_schema import (
    AttachmentView,
    AuditEventView,
    TicketDetailView,
    TicketFilters,
    TicketListItem,
    TicketListResult,
    WorkflowExecutionView,
)


class DashboardService:
    """Application service for agent dashboard read operations."""

    def __init__(
        self,
        ticket_repository: TicketRepository,
        attachment_repository: AttachmentRepository,
        audit_repository: AuditRepository,
        workflow_execution_repository: WorkflowExecutionRepository,
    ) -> None:
        self._ticket_repository = ticket_repository
        self._attachment_repository = attachment_repository
        self._audit_repository = audit_repository
        self._workflow_execution_repository = (
            workflow_execution_repository
        )

    def list_tickets(
        self,
        filters: TicketFilters,
    ) -> TicketListResult:
        tickets = self._ticket_repository.list_tickets(
            status=filters.status,
            priority=filters.priority,
            category=filters.category,
            assigned_team=filters.assigned_team,
            limit=filters.limit,
            offset=filters.offset,
        )

        total = self._ticket_repository.count_tickets(
            status=filters.status,
            priority=filters.priority,
            category=filters.category,
            assigned_team=filters.assigned_team,
        )

        return TicketListResult(
            tickets=tuple(
                TicketListItem.model_validate(ticket)
                for ticket in tickets
            ),
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def get_ticket_detail(
        self,
        ticket_id: int,
    ) -> TicketDetailView | None:
        ticket = self._ticket_repository.get_by_id(ticket_id)

        if ticket is None:
            return None

        attachments = self._attachment_repository.list_by_ticket_id(
            ticket_id
        )

        audit_events = self._audit_repository.list_by_ticket_id(
            ticket_id
        )

        workflow_execution = (
            self._workflow_execution_repository.get_by_ticket_id(
                ticket_id
            )
        )

        workflow_view = None

        if workflow_execution is not None:
            workflow_view = WorkflowExecutionView.model_validate(
                workflow_execution
            )

        return TicketDetailView(
            id=ticket.id,
            ticket_number=ticket.ticket_number,
            customer_name=ticket.customer_name,
            company=ticket.company,
            sender_email=ticket.sender_email,
            email_subject=ticket.email_subject,
            original_email_body=ticket.original_email_body,
            issue_summary=ticket.issue_summary,
            detailed_description=ticket.detailed_description,
            category=ticket.category,
            priority=ticket.priority,
            sentiment=ticket.sentiment,
            product_or_service=ticket.product_or_service,
            suggested_department=ticket.suggested_department,
            assigned_team=ticket.assigned_team,
            confidence_score=ticket.confidence_score,
            status=ticket.status,
            received_at=ticket.received_at,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            priority_reason=ticket.priority_reason,
            suggested_reply=ticket.suggested_reply,
            attachments=tuple(
                AttachmentView.model_validate(attachment)
                for attachment in attachments
            ),
            audit_events=tuple(
                AuditEventView.model_validate(event)
                for event in audit_events
            ),
            workflow_execution=workflow_view,
        )
