from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import RepositoryError
from app.models.ticket_audit_log import TicketAuditLog
from app.repositories.audit_repository import AuditRepository


@pytest.fixture
def session():
    return MagicMock(spec=Session)


@pytest.fixture
def repository(session):
    return AuditRepository(session)


@pytest.fixture
def audit_log():
    return TicketAuditLog(
        ticket_id=1,
        action="TICKET_CREATED",
        old_value=None,
        new_value="Ticket created successfully",
        performed_by="workflow",
    )


def test_add_audit_event(repository, session, audit_log):
    result = repository.add(audit_log)

    session.add.assert_called_once_with(audit_log)
    session.flush.assert_called_once_with()

    assert result is audit_log


def test_list_audit_events_by_ticket(
    repository,
    session,
):
    first = TicketAuditLog(
        id=1,
        ticket_id=10,
        action="TICKET_CREATED",
        new_value="Ticket created",
    )

    second = TicketAuditLog(
        id=2,
        ticket_id=10,
        action="PRIORITY_ASSIGNED",
        new_value="Critical",
    )

    session.scalars.return_value = [first, second]

    result = repository.list_by_ticket_id(10)

    session.scalars.assert_called_once()

    assert result == [first, second]


def test_list_audit_events_returns_empty_list(
    repository,
    session,
):
    session.scalars.return_value = []

    result = repository.list_by_ticket_id(999)

    assert result == []


def test_add_translates_sqlalchemy_error(
    repository,
    session,
    audit_log,
):
    session.flush.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.add(audit_log)

    assert "Audit-log persistence failed" in str(
        exc_info.value
    )


def test_list_by_ticket_id_translates_sqlalchemy_error(
    repository,
    session,
):
    session.scalars.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.list_by_ticket_id(10)

    assert "Audit-log lookup failed" in str(exc_info.value)


def test_repository_does_not_commit_transaction(
    repository,
    session,
    audit_log,
):
    repository.add(audit_log)

    session.commit.assert_not_called()
