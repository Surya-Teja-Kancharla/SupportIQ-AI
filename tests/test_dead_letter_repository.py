from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.core.constants import DeadLetterStatus
from app.core.exceptions import RepositoryError
from app.models.dead_letter_record import DeadLetterRecord
from app.repositories.dead_letter_repository import (
    DeadLetterRepository,
)


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def repository(
    session: MagicMock,
) -> DeadLetterRepository:
    return DeadLetterRepository(session)


def build_dead_letter_record() -> DeadLetterRecord:
    return DeadLetterRecord(
        id=1,
        workflow_execution_id=10,
        ticket_id=20,
        failed_stage="AI_ANALYSIS_STARTED",
        exception_type="LLMTimeoutError",
        sanitized_error_message=(
            "The LLM provider request timed out."
        ),
        retry_count=3,
        retry_exhausted=True,
        status=DeadLetterStatus.OPEN,
        manual_retry_count=0,
        last_retry_execution_id=None,
    )


def test_create_dead_letter_record(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    session.scalar.return_value = None

    record = repository.create(
        workflow_execution_id=10,
        ticket_id=20,
        failed_stage="AI_ANALYSIS_STARTED",
        exception_type="LLMTimeoutError",
        sanitized_error_message=(
            "The LLM provider request timed out."
        ),
        retry_count=3,
        retry_exhausted=True,
    )

    session.add.assert_called_once_with(record)
    session.flush.assert_called_once()

    assert record.workflow_execution_id == 10
    assert record.ticket_id == 20
    assert record.failed_stage == "AI_ANALYSIS_STARTED"
    assert record.exception_type == "LLMTimeoutError"
    assert record.retry_count == 3
    assert record.retry_exhausted is True
    assert record.status == DeadLetterStatus.OPEN
    assert record.manual_retry_count == 0


def test_create_returns_existing_record(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    existing_record = build_dead_letter_record()

    session.scalar.return_value = existing_record

    result = repository.create(
        workflow_execution_id=10,
        ticket_id=20,
        failed_stage="AI_ANALYSIS_STARTED",
        exception_type="LLMTimeoutError",
        sanitized_error_message="Timeout.",
        retry_count=3,
        retry_exhausted=True,
    )

    assert result is existing_record

    session.add.assert_not_called()
    session.flush.assert_not_called()


def test_create_wraps_database_failure(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    session.scalar.return_value = None
    session.flush.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    with pytest.raises(
        RepositoryError,
        match="Dead-letter record persistence failed.",
    ):
        repository.create(
            workflow_execution_id=10,
            ticket_id=None,
            failed_stage="DATABASE_PERSISTENCE",
            exception_type="OperationalError",
            sanitized_error_message=(
                "Database operation failed."
            ),
            retry_count=3,
            retry_exhausted=True,
        )


def test_get_by_id_returns_record(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    record = build_dead_letter_record()

    session.scalar.return_value = record

    result = repository.get_by_id(1)

    assert result is record
    session.scalar.assert_called_once()


def test_get_by_execution_id_returns_record(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    record = build_dead_letter_record()

    session.scalar.return_value = record

    result = repository.get_by_execution_id(10)

    assert result is record
    session.scalar.assert_called_once()


def test_get_by_execution_id_returns_none(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    session.scalar.return_value = None

    result = repository.get_by_execution_id(999)

    assert result is None


def test_get_by_execution_id_wraps_database_failure(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    session.scalar.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    with pytest.raises(
        RepositoryError,
        match="Dead-letter record lookup failed.",
    ):
        repository.get_by_execution_id(10)


def test_list_records_returns_records(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    first_record = build_dead_letter_record()

    second_record = build_dead_letter_record()
    second_record.id = 2
    second_record.workflow_execution_id = 11

    scalar_result = MagicMock()
    scalar_result.all.return_value = [
        first_record,
        second_record,
    ]

    session.scalars.return_value = scalar_result

    result = repository.list_records()

    assert result == [
        first_record,
        second_record,
    ]


def test_list_records_wraps_database_failure(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    session.scalars.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    with pytest.raises(
        RepositoryError,
        match="Dead-letter record listing failed.",
    ):
        repository.list_records()


def test_mark_retrying(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    record = build_dead_letter_record()

    result = repository.mark_retrying(record)

    assert result is record
    assert record.status == DeadLetterStatus.RETRYING
    assert record.manual_retry_count == 1

    session.flush.assert_called_once()


def test_mark_resolved(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    record = build_dead_letter_record()

    result = repository.mark_resolved(
        record,
        retry_execution_id=50,
    )

    assert result is record
    assert record.status == DeadLetterStatus.RESOLVED
    assert record.last_retry_execution_id == 50

    session.flush.assert_called_once()


def test_mark_retry_failed(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    record = build_dead_letter_record()
    record.status = DeadLetterStatus.RETRYING

    result = repository.mark_retry_failed(
        record,
        retry_execution_id=51,
    )

    assert result is record
    assert record.status == DeadLetterStatus.OPEN
    assert record.last_retry_execution_id == 51

    session.flush.assert_called_once()


def test_mutation_wraps_database_failure(
    repository: DeadLetterRepository,
    session: MagicMock,
) -> None:
    record = build_dead_letter_record()

    session.flush.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    with pytest.raises(
        RepositoryError,
        match="Dead-letter record update failed.",
    ):
        repository.mark_retrying(record)
