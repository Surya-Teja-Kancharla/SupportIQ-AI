from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import RepositoryError
from app.models.ticket_attachment import TicketAttachment


class AttachmentRepository:
    """Persistence operations for ticket attachments."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        attachment: TicketAttachment,
    ) -> TicketAttachment:
        try:
            self._session.add(attachment)
            self._session.flush()

            return attachment

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Attachment persistence failed."
            ) from exc

    def list_by_ticket_id(
        self,
        ticket_id: int,
    ) -> list[TicketAttachment]:
        try:
            statement = (
                select(TicketAttachment)
                .where(
                    TicketAttachment.ticket_id == ticket_id
                )
                .order_by(TicketAttachment.id)
            )

            return list(self._session.scalars(statement))

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Attachment lookup failed."
            ) from exc
