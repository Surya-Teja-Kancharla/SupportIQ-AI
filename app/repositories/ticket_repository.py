from collections.abc import Sequence

from sqlalchemy import func, select

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateTicketError,
    RepositoryError,
)
from app.models.ticket import Ticket


class TicketRepository:
    """Persistence operations for tickets."""

    def __init__(self, session: Session | None = None) -> None:
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

    def create(self, ticket: Ticket) -> Ticket:
        return self.add(ticket)

    def get_by_id(
        self,
        *args,
    ) -> Ticket | None:
        try:
            if len(args) == 2:
                session, ticket_id = args
            else:
                session = self._session
                ticket_id = args[0]

            return session.get(Ticket, ticket_id)

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

    def list_tickets(
        self,
        *,
        status: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        assigned_team: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:
        """
        Return tickets matching optional dashboard filters.

        Results are ordered newest first with ID as a deterministic
        secondary ordering key.
        """

        try:
            statement = select(Ticket)

            if status is not None:
                statement = statement.where(
                    Ticket.status == status
                )

            if priority is not None:
                statement = statement.where(
                    Ticket.priority == priority
                )

            if category is not None:
                statement = statement.where(
                    Ticket.category == category
                )

            if assigned_team is not None:
                statement = statement.where(
                    Ticket.assigned_team == assigned_team
                )

            statement = (
                statement
                .order_by(
                    Ticket.received_at.desc(),
                    Ticket.id.desc(),
                )
                .limit(limit)
                .offset(offset)
            )

            return list(self._session.scalars(statement))

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Ticket listing failed."
            ) from exc


    def count_tickets(
        self,
        *,
        status: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        assigned_team: str | None = None,
    ) -> int:
        """Count tickets matching optional dashboard filters."""

        try:
            statement = select(func.count(Ticket.id))

            if status is not None:
                statement = statement.where(
                    Ticket.status == status
                )

            if priority is not None:
                statement = statement.where(
                    Ticket.priority == priority
                )

            if category is not None:
                statement = statement.where(
                    Ticket.category == category
                )

            if assigned_team is not None:
                statement = statement.where(
                    Ticket.assigned_team == assigned_team
                )

            return int(self._session.scalar(statement) or 0)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Ticket count failed."
            ) from exc
