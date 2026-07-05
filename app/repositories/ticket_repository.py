from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateTicketError,
    RepositoryError,
)
from app.models.ticket import Ticket


class TicketRepository:
    """Persistence operations for tickets."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, ticket: Ticket) -> Ticket:
        try:
            self._session.add(ticket)
            self._session.flush()

            return ticket

        except IntegrityError as exc:
            raise DuplicateTicketError(
                "Ticket could not be persisted because "
                "a uniqueness constraint was violated."
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Ticket persistence failed."
            ) from exc

    def get_by_id(
        self,
        ticket_id: int,
    ) -> Ticket | None:
        try:
            return self._session.get(Ticket, ticket_id)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Ticket lookup failed."
            ) from exc

    def get_by_ticket_number(
        self,
        ticket_number: str,
    ) -> Ticket | None:
        try:
            statement = select(Ticket).where(
                Ticket.ticket_number == ticket_number
            )

            return self._session.scalar(statement)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Ticket lookup failed."
            ) from exc
