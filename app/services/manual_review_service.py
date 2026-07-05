from sqlalchemy.orm import Session

from app.core.constants import AuditAction
from app.repositories.audit_repository import AuditRepository
from app.repositories.internal_note_repository import InternalNoteRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.reply_suggestion_service import ReplySuggestionService
from app.services.ticket_lifecycle_service import TicketLifecycleService


class ManualReviewService:
    CATEGORY_CHANGED = AuditAction.CATEGORY_CHANGED
    PRIORITY_CHANGED = AuditAction.PRIORITY_CHANGED
    TEAM_REASSIGNED = AuditAction.TEAM_REASSIGNED
    STATUS_CHANGED = AuditAction.STATUS_CHANGED
    INTERNAL_NOTE_ADDED = AuditAction.INTERNAL_NOTE_ADDED
    SUGGESTED_REPLY_EDITED = AuditAction.SUGGESTED_REPLY_EDITED
    SUGGESTED_REPLY_REGENERATED = AuditAction.SUGGESTED_REPLY_REGENERATED

    def __init__(
        self,
        ticket_repository: TicketRepository | None = None,
        audit_repository: AuditRepository | None = None,
        internal_note_repository: InternalNoteRepository | None = None,
        reply_suggestion_service: ReplySuggestionService | None = None,
        ticket_lifecycle_service: TicketLifecycleService | None = None,
    ) -> None:
        self.ticket_repository = ticket_repository
        self.audit_repository = audit_repository
        self.internal_note_repository = internal_note_repository
        self.reply_suggestion_service = reply_suggestion_service
        self.ticket_lifecycle_service = ticket_lifecycle_service or TicketLifecycleService(
            ticket_repository=ticket_repository,
            audit_repository=audit_repository,
        )

    def _get_ticket_repository(self) -> TicketRepository:
        if self.ticket_repository is None:
            raise RuntimeError(
                "Ticket repository has not been configured."
            )

        return self.ticket_repository

    def _get_audit_repository(self) -> AuditRepository:
        if self.audit_repository is None:
            raise RuntimeError(
                "Audit repository has not been configured."
            )

        return self.audit_repository

    def _get_internal_note_repository(self) -> InternalNoteRepository:
        if self.internal_note_repository is None:
            raise RuntimeError(
                "Internal note repository has not been configured."
            )

        return self.internal_note_repository

    def _get_reply_suggestion_service(self) -> ReplySuggestionService:
        if self.reply_suggestion_service is None:
            raise RuntimeError(
                "Reply suggestion service has not been configured."
            )

        return self.reply_suggestion_service

    def _get_ticket_lifecycle_service(self) -> TicketLifecycleService:
        return self.ticket_lifecycle_service

    def _get_ticket_or_raise(
        self,
        db: Session,
        ticket_id: int,
    ):
        ticket = self._get_ticket_repository().get_by_id(
            db,
            ticket_id,
        )

        if ticket is None:
            raise ValueError(f"Ticket {ticket_id} not found")

        return ticket

    def _update_field(
        self,
        db: Session,
        *,
        ticket_id: int,
        field_name: str,
        new_value: str,
        action: str,
        performed_by: str,
    ):
        ticket = self._get_ticket_or_raise(
            db,
            ticket_id,
        )

        old_value = getattr(ticket, field_name)

        # A no-op update is not considered an effective mutation.
        if old_value == new_value:
            return ticket

        try:
            setattr(ticket, field_name, new_value)

            self._get_audit_repository().create(
                db,
                ticket_id=ticket.id,
                action=action,
                old_value=old_value,
                new_value=new_value,
                performed_by=performed_by,
            )

            db.commit()
            db.refresh(ticket)

            return ticket

        except Exception:
            db.rollback()
            raise

    def update_category(
        self,
        db: Session,
        *,
        ticket_id: int,
        category: str,
        performed_by: str,
    ):
        return self._update_field(
            db,
            ticket_id=ticket_id,
            field_name="category",
            new_value=category,
            action=self.CATEGORY_CHANGED,
            performed_by=performed_by,
        )

    def update_priority(
        self,
        db: Session,
        *,
        ticket_id: int,
        priority: str,
        performed_by: str,
    ):
        return self._update_field(
            db,
            ticket_id=ticket_id,
            field_name="priority",
            new_value=priority,
            action=self.PRIORITY_CHANGED,
            performed_by=performed_by,
        )

    def reassign_team(
        self,
        db: Session,
        *,
        ticket_id: int,
        assigned_team: str,
        performed_by: str,
    ):
        return self._update_field(
            db,
            ticket_id=ticket_id,
            field_name="assigned_team",
            new_value=assigned_team,
            action=self.TEAM_REASSIGNED,
            performed_by=performed_by,
        )

    def update_status(
        self,
        db: Session,
        *,
        ticket_id: int,
        status: str,
        performed_by: str,
    ):
        ticket = self._get_ticket_lifecycle_service().transition(
            db,
            ticket_id=ticket_id,
            target_status=status,
            performed_by=performed_by,
        )

        db.commit()
        db.refresh(ticket)

        return ticket

    def edit_suggested_reply(
        self,
        db: Session,
        *,
        ticket_id: int,
        suggested_reply: str,
        performed_by: str,
    ):
        return self._update_field(
            db,
            ticket_id=ticket_id,
            field_name="suggested_reply",
            new_value=suggested_reply,
            action=self.SUGGESTED_REPLY_EDITED,
            performed_by=performed_by,
        )

    def add_internal_note(
        self,
        db: Session,
        *,
        ticket_id: int,
        note: str,
        created_by: str,
    ):
        ticket = self._get_ticket_or_raise(
            db,
            ticket_id,
        )

        try:
            internal_note = self._get_internal_note_repository().create(
                db,
                ticket_id=ticket.id,
                note=note,
                created_by=created_by,
            )

            self._get_audit_repository().create(
                db,
                ticket_id=ticket.id,
                action=self.INTERNAL_NOTE_ADDED,
                old_value=None,
                new_value=note,
                performed_by=created_by,
            )

            db.commit()
            db.refresh(internal_note)

            return internal_note

        except Exception:
            db.rollback()
            raise

    def regenerate_suggested_reply(
        self,
        db: Session,
        *,
        ticket_id: int,
        performed_by: str,
    ):
        ticket = self._get_ticket_or_raise(
            db,
            ticket_id,
        )

        old_reply = ticket.suggested_reply

        try:
            result = self._get_reply_suggestion_service().generate(
                subject=ticket.subject,
                body=ticket.body,
                category=ticket.category,
                priority=ticket.priority,
                sentiment=ticket.sentiment,
                assigned_team=ticket.assigned_team,
            )

            new_reply = result.suggested_reply

            ticket.suggested_reply = new_reply

            self._get_audit_repository().create(
                db,
                ticket_id=ticket.id,
                action=self.SUGGESTED_REPLY_REGENERATED,
                old_value=old_reply,
                new_value=new_reply,
                performed_by=performed_by,
            )

            db.commit()
            db.refresh(ticket)

            return ticket

        except Exception:
            db.rollback()
            raise
