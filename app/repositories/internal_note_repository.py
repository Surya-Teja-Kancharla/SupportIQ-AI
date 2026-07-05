from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.internal_note import InternalNote


class InternalNoteRepository:

    def create(
        self,
        db: Session,
        *,
        ticket_id: int,
        note: str,
        created_by: str,
    ) -> InternalNote:
        internal_note = InternalNote(
            ticket_id=ticket_id,
            note=note,
            created_by=created_by,
        )

        db.add(internal_note)
        db.flush()
        db.refresh(internal_note)

        return internal_note

    def list_by_ticket(
        self,
        db: Session,
        ticket_id: int,
    ) -> list[InternalNote]:
        statement = (
            select(InternalNote)
            .where(InternalNote.ticket_id == ticket_id)
            .order_by(InternalNote.created_at.desc())
        )

        return list(db.scalars(statement).all())
