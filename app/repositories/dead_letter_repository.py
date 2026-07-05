from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import DeadLetterStatus
from app.core.exceptions import RepositoryError
from app.models.dead_letter_record import DeadLetterRecord


class DeadLetterRepository:
    """Persistence operations for dead-letter records."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        workflow_execution_id: int,
        ticket_id: int | None,
        failed_stage: str,
        exception_type: str,
        sanitized_error_message: str,
        retry_count: int,
        retry_exhausted: bool,
    ) -> DeadLetterRecord:
        """
        Create one dead-letter record per workflow execution.

        This operation is idempotent. If a record already exists for
        the supplied workflow execution, the existing record is
        returned without creating a duplicate.
        """

        existing_record = self.get_by_execution_id(
            workflow_execution_id
        )

        if existing_record is not None:
            return existing_record

        record = DeadLetterRecord(
            workflow_execution_id=workflow_execution_id,
            ticket_id=ticket_id,
            failed_stage=failed_stage,
            exception_type=exception_type,
            sanitized_error_message=(
                sanitized_error_message
            ),
            retry_count=retry_count,
            retry_exhausted=retry_exhausted,
            status=DeadLetterStatus.OPEN,
            manual_retry_count=0,
            last_retry_execution_id=None,
        )

        try:
            self._session.add(record)
            self._session.flush()

            return record

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Dead-letter record persistence failed."
            ) from exc

    def get_by_id(
        self,
        dead_letter_id: int,
    ) -> DeadLetterRecord | None:
        try:
            statement = select(
                DeadLetterRecord
            ).where(
                DeadLetterRecord.id == dead_letter_id
            )

            return self._session.scalar(statement)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Dead-letter record lookup failed."
            ) from exc

    def get_by_execution_id(
        self,
        workflow_execution_id: int,
    ) -> DeadLetterRecord | None:
        try:
            statement = select(
                DeadLetterRecord
            ).where(
                DeadLetterRecord.workflow_execution_id
                == workflow_execution_id
            )

            return self._session.scalar(statement)

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Dead-letter record lookup failed."
            ) from exc

    def list_records(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        status: str | None = None,
    ) -> list[DeadLetterRecord]:
        try:
            statement = select(DeadLetterRecord)

            if status is not None:
                statement = statement.where(
                    DeadLetterRecord.status == status
                )

            statement = (
                statement
                .order_by(
                    DeadLetterRecord.created_at.desc(),
                    DeadLetterRecord.id.desc(),
                )
                .offset(offset)
                .limit(limit)
            )

            return list(
                self._session.scalars(statement).all()
            )

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Dead-letter record listing failed."
            ) from exc

    def mark_retrying(
        self,
        record: DeadLetterRecord,
    ) -> DeadLetterRecord:
        record.status = DeadLetterStatus.RETRYING
        record.manual_retry_count += 1

        self._flush_mutation()

        return record

    def mark_resolved(
        self,
        record: DeadLetterRecord,
        *,
        retry_execution_id: int,
    ) -> DeadLetterRecord:
        record.status = DeadLetterStatus.RESOLVED
        record.last_retry_execution_id = retry_execution_id

        self._flush_mutation()

        return record

    def mark_retry_failed(
        self,
        record: DeadLetterRecord,
        *,
        retry_execution_id: int,
    ) -> DeadLetterRecord:
        record.status = DeadLetterStatus.OPEN
        record.last_retry_execution_id = retry_execution_id

        self._flush_mutation()

        return record

    def _flush_mutation(self) -> None:
        try:
            self._session.flush()

        except SQLAlchemyError as exc:
            raise RepositoryError(
                "Dead-letter record update failed."
            ) from exc
