from sqlalchemy.orm import Session

from app.core.constants import AuditAction, TicketStatus
from app.core.exceptions import InvalidTicketTransitionError
from app.repositories.audit_repository import AuditRepository
from app.repositories.ticket_repository import TicketRepository


class TicketLifecycleService:
    ALLOWED_TRANSITIONS = {
        TicketStatus.OPEN: {
            TicketStatus.IN_PROGRESS,
        },
        TicketStatus.IN_PROGRESS: {
            TicketStatus.WAITING_FOR_CUSTOMER,
            TicketStatus.RESOLVED,
        },
        TicketStatus.WAITING_FOR_CUSTOMER: {
            TicketStatus.IN_PROGRESS,
            TicketStatus.RESOLVED,
        },
        TicketStatus.RESOLVED: {
            TicketStatus.CLOSED,
        },
        TicketStatus.CLOSED: set(),
    }

    def __init__(
        self,
        ticket_repository: TicketRepository | None = None,
        audit_repository: AuditRepository | None = None,
    ) -> None:
        self.ticket_repository = ticket_repository
        self.audit_repository = audit_repository

    def _get_ticket_repository(self) -> TicketRepository:
        if self.ticket_repository is None:
            raise RuntimeError("Ticket repository has not been configured.")

        return self.ticket_repository

    def _get_audit_repository(self) -> AuditRepository:
        if self.audit_repository is None:
            raise RuntimeError("Audit repository has not been configured.")

        return self.audit_repository

    def transition(
        self,
        db: Session,
        *,
        ticket_id: int,
        target_status: str,
        performed_by: str,
    ):
        ticket = self._get_ticket_repository().get_by_id(
            db,
            ticket_id,
        )

        if ticket is None:
            raise ValueError(f"Ticket {ticket_id} not found")

        current_status = str(getattr(ticket, "status", "") or "")
        normalized_target_status = str(target_status).upper()

        if current_status == normalized_target_status:
            return ticket

        allowed_targets = self.ALLOWED_TRANSITIONS.get(current_status)

        if allowed_targets is None or normalized_target_status not in allowed_targets:
            raise InvalidTicketTransitionError(
                current_status=current_status,
                target_status=normalized_target_status,
            )

        ticket.status = normalized_target_status

        self._get_audit_repository().create(
            db,
            ticket_id=ticket.id,
            action=AuditAction.STATUS_CHANGED,
            old_value=current_status,
            new_value=normalized_target_status,
            performed_by=performed_by,
        )

        db.flush()

        return ticket
