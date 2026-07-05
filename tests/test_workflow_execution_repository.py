from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateWorkflowExecutionError,
    RepositoryError,
)
from app.models.workflow_execution import WorkflowExecution
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)


@pytest.fixture
def session():
    return MagicMock(spec=Session)


@pytest.fixture
def repository(session):
    return WorkflowExecutionRepository(session)


@pytest.fixture
def execution():
    return WorkflowExecution(
        message_id="<message-001@example.com>",
        status="STARTED",
    )


def test_add_workflow_execution(
    repository,
    session,
    execution,
):
    result = repository.add(execution)

    session.add.assert_called_once_with(execution)
    session.flush.assert_called_once_with()

    assert result is execution


def test_get_workflow_execution_by_message_id(
    repository,
    session,
    execution,
):
    session.scalar.return_value = execution

    result = repository.get_by_message_id(
        "<message-001@example.com>"
    )

    session.scalar.assert_called_once()

    assert result is execution


def test_get_by_message_id_returns_none_for_unknown_message(
    repository,
    session,
):
    session.scalar.return_value = None

    result = repository.get_by_message_id(
        "<unknown@example.com>"
    )

    assert result is None


def test_add_rejects_duplicate_message_id(
    repository,
    session,
    execution,
):
    session.flush.side_effect = IntegrityError(
        statement="INSERT INTO workflow_executions",
        params={},
        orig=Exception("duplicate message_id"),
    )

    with pytest.raises(
        DuplicateWorkflowExecutionError
    ) as exc_info:
        repository.add(execution)

    assert "already exists" in str(exc_info.value)

    session.add.assert_called_once_with(execution)
    session.flush.assert_called_once_with()


def test_add_translates_sqlalchemy_error(
    repository,
    session,
    execution,
):
    session.flush.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.add(execution)

    assert "Workflow-execution persistence failed" in str(
        exc_info.value
    )


def test_get_by_message_id_translates_sqlalchemy_error(
    repository,
    session,
):
    session.scalar.side_effect = SQLAlchemyError(
        "database failure"
    )

    with pytest.raises(RepositoryError) as exc_info:
        repository.get_by_message_id(
            "<message-001@example.com>"
        )

    assert "Workflow-execution lookup failed" in str(
        exc_info.value
    )


def test_repository_does_not_commit_transaction(
    repository,
    session,
    execution,
):
    repository.add(execution)

    session.commit.assert_not_called()

def test_get_workflow_execution_by_ticket_id():
    session = Mock()

    workflow_execution = SimpleNamespace(
        id=1,
        ticket_id=501,
    )

    session.scalar.return_value = workflow_execution

    repository = WorkflowExecutionRepository(session)

    result = repository.get_by_ticket_id(501)

    assert result is workflow_execution
    session.scalar.assert_called_once()


def test_get_by_ticket_id_returns_none_for_unknown_ticket():
    session = Mock()
    session.scalar.return_value = None

    repository = WorkflowExecutionRepository(session)

    result = repository.get_by_ticket_id(999)

    assert result is None


def test_get_by_ticket_id_translates_sqlalchemy_error():
    session = Mock()
    session.scalar.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    repository = WorkflowExecutionRepository(session)

    with pytest.raises(RepositoryError):
        repository.get_by_ticket_id(501)
