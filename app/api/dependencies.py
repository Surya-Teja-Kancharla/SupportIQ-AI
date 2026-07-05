from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.repositories import (
    AttachmentRepository,
    AuditRepository,
    TicketRepository,
    WorkflowExecutionRepository,
)
from app.services.dashboard_service import DashboardService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Backward-compatible alias for existing Hour 10 routes/tests.
get_db_session = get_db


def get_dashboard_service(
    session: Session = Depends(get_db_session),
) -> DashboardService:
    return DashboardService(
        ticket_repository=TicketRepository(session),
        attachment_repository=AttachmentRepository(session),
        audit_repository=AuditRepository(session),
        workflow_execution_repository=(
            WorkflowExecutionRepository(session)
        ),
    )
