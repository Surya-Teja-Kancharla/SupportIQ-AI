from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import RepositoryError
from app.models.ticket_attachment import TicketAttachment
from app.repositories.attachment_repository import AttachmentRepository


@pytest.fixture
def session():
    return MagicMock(spec=Session)


@pytest.fixture
def repository(session):
    return AttachmentRepository(session)


@pytest.fixture
def attachment():
    return TicketAttachment(
        ticket_id=1,
        file_name="error.png",
        file_path="uploads/attachments/error.png",
        file_type="image/png",
    )


def test_add_attachment(repository, session, attachment):
    result = repository.add(attachment)

    session.add.assert_called_once_with(attachment)
    session.flush.assert_called_once_with()

    assert result is attachment


def test_list_attachments_by_ticket(repository, session):
    first = TicketAttachment(
        id=1,
        ticket_id=10,
        file_name="first.png",
        file_path="uploads/attachments/first.png",
        file_type="image/png",
    )

    second = TicketAttachment(
        id=2,
        ticket_id=10,
        file_name="second.pdf",
        file_path="uploads/attachments/second.pdf",
        file_type="application/pdf",
    )

    session.scalars.return_value = [first, second]

    result = repository.list_by_ticket_id(10)

    session.scalars.assert_called_once()

    assert result == [first, second]


def test_list_attachments_preserves_repository_order(
    repository,
    session,
):
    first = TicketAttachment(
        id=1,
        ticket_id=10,
        file_name="first.png",
        file_path="uploads/attachments/first.png",
    )

    second = TicketAttachment(
        id=2,
        ticket_id=10,
        file_name="second.png",
        file_path="uploads/attachments/second.png",
    )

    session.scalars.return_value = [first, second]

    result = repository.list_by_ticket_id(10)

    assert [item.id for item in result] == [1, 2]


def test_list_attachments_returns_empty_list(
    repository,
    session,
):
    session.scalars.return_value = []

    result = repository.list_by_ticket_id(999)

    assert result == []


def test_add_translates_sqlalchemy_error(
    repository,
    session,
    attachment,
):
    session.flush.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.add(attachment)

    assert "Attachment persistence failed" in str(
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

    assert "Attachment lookup failed" in str(exc_info.value)


def test_repository_does_not_commit_transaction(
    repository,
    session,
    attachment,
):
    repository.add(attachment)

    session.commit.assert_not_called()
