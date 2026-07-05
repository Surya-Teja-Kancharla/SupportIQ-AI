from unittest.mock import MagicMock

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
