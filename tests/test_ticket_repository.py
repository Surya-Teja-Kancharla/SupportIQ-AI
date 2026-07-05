from unittest.mock import MagicMock, Mock
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateTicketError, RepositoryError
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository


@pytest.fixture
def session():
    return MagicMock(spec=Session)


@pytest.fixture
def repository(session):
    return TicketRepository(session)


@pytest.fixture
def ticket():
    return Ticket(
        ticket_number="SUP-20260705-0001",
        sender_email="customer@example.com",
        subject="Unable to access account",
        body="I cannot access my account.",
        received_at="2026-07-05 17:00:00",
    )


def test_add_ticket(repository, session, ticket):
    result = repository.add(ticket)

    session.add.assert_called_once_with(ticket)
    session.flush.assert_called_once_with()

    assert result is ticket


def test_get_ticket_by_id(repository, session, ticket):
    session.get.return_value = ticket

    result = repository.get_by_id(1)

    session.get.assert_called_once_with(Ticket, 1)

    assert result is ticket


def test_get_ticket_by_ticket_number(repository, session, ticket):
    session.scalar.return_value = ticket

    result = repository.get_by_ticket_number(
        "SUP-20260705-0001"
    )

    session.scalar.assert_called_once()

    assert result is ticket


def test_get_by_id_returns_none_for_unknown_ticket(
    repository,
    session,
):
    session.get.return_value = None

    result = repository.get_by_id(999)

    assert result is None


def test_get_by_ticket_number_returns_none_for_unknown_ticket(
    repository,
    session,
):
    session.scalar.return_value = None

    result = repository.get_by_ticket_number("UNKNOWN")

    assert result is None


def test_add_translates_integrity_error(
    repository,
    session,
    ticket,
):
    session.flush.side_effect = IntegrityError(
        statement="INSERT INTO tickets",
        params={},
        orig=Exception("duplicate ticket"),
    )

    with pytest.raises(DuplicateTicketError) as exc_info:
        repository.add(ticket)

    assert "uniqueness constraint" in str(exc_info.value)

    session.add.assert_called_once_with(ticket)
    session.flush.assert_called_once_with()


def test_add_translates_sqlalchemy_error(
    repository,
    session,
    ticket,
):
    session.flush.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.add(ticket)

    assert "Ticket persistence failed" in str(exc_info.value)


def test_get_by_id_translates_sqlalchemy_error(
    repository,
    session,
):
    session.get.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.get_by_id(1)

    assert "Ticket lookup failed" in str(exc_info.value)


def test_get_by_ticket_number_translates_sqlalchemy_error(
    repository,
    session,
):
    session.scalar.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.get_by_ticket_number(
            "SUP-20260705-0001"
        )

    assert "Ticket lookup failed" in str(exc_info.value)


def test_repository_does_not_commit_transaction(
    repository,
    session,
    ticket,
):
    repository.add(ticket)

    session.commit.assert_not_called()

def test_list_tickets_returns_repository_results():
    session = Mock()

    ticket_one = SimpleNamespace(id=2)
    ticket_two = SimpleNamespace(id=1)

    session.scalars.return_value = [
        ticket_one,
        ticket_two,
    ]

    repository = TicketRepository(session)

    result = repository.list_tickets()

    assert result == [ticket_one, ticket_two]
    session.scalars.assert_called_once()


def test_list_tickets_supports_all_dashboard_filters():
    session = Mock()
    session.scalars.return_value = []

    repository = TicketRepository(session)

    repository.list_tickets(
        status="open",
        priority="Critical",
        category="Technical Support",
        assigned_team="Technical Support",
        limit=25,
        offset=10,
    )

    statement = session.scalars.call_args.args[0]
    compiled = statement.compile()

    assert len(compiled.params) == 6
    assert "tickets.status" in str(statement)
    assert "tickets.priority" in str(statement)
    assert "tickets.category" in str(statement)
    assert "tickets.assigned_team" in str(statement)
    assert "LIMIT" in str(statement)
    assert "OFFSET" in str(statement)


def test_list_tickets_uses_newest_first_deterministic_order():
    session = Mock()
    session.scalars.return_value = []

    repository = TicketRepository(session)

    repository.list_tickets()

    statement = session.scalars.call_args.args[0]
    statement_text = str(statement)

    assert "tickets.received_at DESC" in statement_text
    assert "tickets.id DESC" in statement_text


def test_list_tickets_returns_empty_list():
    session = Mock()
    session.scalars.return_value = []

    repository = TicketRepository(session)

    assert repository.list_tickets() == []


def test_list_tickets_translates_sqlalchemy_error():
    session = Mock()
    session.scalars.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    repository = TicketRepository(session)

    with pytest.raises(RepositoryError):
        repository.list_tickets()


def test_count_tickets_returns_count():
    session = Mock()
    session.scalar.return_value = 17

    repository = TicketRepository(session)

    result = repository.count_tickets()

    assert result == 17
    session.scalar.assert_called_once()


def test_count_tickets_supports_all_dashboard_filters():
    session = Mock()
    session.scalar.return_value = 4

    repository = TicketRepository(session)

    result = repository.count_tickets(
        status="open",
        priority="High",
        category="Billing",
        assigned_team="Finance",
    )

    statement = session.scalar.call_args.args[0]

    assert result == 4
    assert "tickets.status" in str(statement)
    assert "tickets.priority" in str(statement)
    assert "tickets.category" in str(statement)
    assert "tickets.assigned_team" in str(statement)


def test_count_tickets_returns_zero_for_none():
    session = Mock()
    session.scalar.return_value = None

    repository = TicketRepository(session)

    assert repository.count_tickets() == 0


def test_count_tickets_translates_sqlalchemy_error():
    session = Mock()
    session.scalar.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    repository = TicketRepository(session)

    with pytest.raises(RepositoryError):
        repository.count_tickets()
