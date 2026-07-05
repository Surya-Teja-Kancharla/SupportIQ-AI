from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import RepositoryError
from app.models.ticket_audit_log import TicketAuditLog


class AuditRepository:
    """Persistence operations for ticket audit logs."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        audit_log: TicketAuditLog,
    ) -> TicketAuditLog:
        try:
            self._session.add(audit_log)
            self._session.flush()

            return audit_log

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Audit-log persistence failed."
            ) from exc

    def list_by_ticket_id(
        self,
        ticket_id: int,
    ) -> list[TicketAuditLog]:
        try:
            statement = (
                select(TicketAuditLog)
                .where(
                    TicketAuditLog.ticket_id == ticket_id
                )
                .order_by(
                    TicketAuditLog.created_at,
                    TicketAuditLog.id,
                )
            )

            return list(self._session.scalars(statement))

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Audit-log lookup failed."
            ) from exc
