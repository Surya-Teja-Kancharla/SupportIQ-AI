from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.constants import (
    DeadLetterStatus,
    WorkflowExecutionStatus,
)
from app.models.dead_letter_record import DeadLetterRecord
from app.models.workflow_execution import WorkflowExecution
from app.repositories.dead_letter_repository import (
    DeadLetterRepository,
)
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)
from app.schemas.email_schema import ParsedEmail
from app.schemas.failure_recovery_schema import (
    WorkflowRetryResponse,
)


class FailureRecoveryService:
    """
    Coordinates administrator-triggered workflow recovery.

    Recovery preserves the original failed workflow execution and creates
    a child execution for every manual retry attempt.

    Recovery lifecycle:

        FAILED execution
            ->
        OPEN dead letter
            ->
        RETRYING
            ->
        child workflow execution
            ->
        SUCCESS -> RESOLVED

        FAILURE -> OPEN
    """

    def __init__(
        self,
        session: Session,
        *,
        workflow_execution_repository: (
            WorkflowExecutionRepository | None
        ) = None,
        dead_letter_repository: (
            DeadLetterRepository | None
        ) = None,
        workflow_service: Any | None = None,
    ) -> None:
        self._session = session

        self._workflow_execution_repository = (
            workflow_execution_repository
            or WorkflowExecutionRepository(session)
        )

        self._dead_letter_repository = (
            dead_letter_repository
            or DeadLetterRepository(session)
        )

        self._workflow_service = workflow_service

    def retry_execution(
        self,
        execution_id: str,
    ) -> WorkflowRetryResponse:
        """
        Retry one failed workflow execution.

        The public execution UUID is used by the API.

        The original failed execution is preserved. A new child execution
        is created for the manual retry.
        """

        original_execution = self._get_original_execution(
            execution_id
        )

        self._validate_failed_execution(
            original_execution
        )

        dead_letter = self._get_dead_letter(
            original_execution
        )

        self._validate_dead_letter(dead_letter)

        try:
            email = self._reconstruct_email(
                original_execution
            )

        except Exception:
            self._session.rollback()
            raise

        retry_execution: WorkflowExecution | None = None

        try:
            self._dead_letter_repository.mark_retrying(
                dead_letter
            )

            self._session.commit()

            retry_execution = (
                self._workflow_execution_repository
                .create_retry_execution(
                    original_execution=original_execution
                )
            )

            self._session.commit()

            workflow_service = self._get_workflow_service()

            workflow_service.process_email(
                email,
                workflow_execution=retry_execution,
            )

            retry_execution.status = (
                WorkflowExecutionStatus.SUCCESS
            )

            self._dead_letter_repository.mark_resolved(
                dead_letter,
                retry_execution_id=retry_execution.id,
            )

            self._session.commit()

            return WorkflowRetryResponse(
                original_execution_id=original_execution.id,
                retry_execution_id=retry_execution.id,
                attempt_number=retry_execution.attempt_number,
                status=WorkflowExecutionStatus.SUCCESS,
            )

        except Exception:
            self._handle_retry_failure(
                dead_letter=dead_letter,
                retry_execution=retry_execution,
            )

            raise

    def _get_original_execution(
        self,
        execution_id: str,
    ) -> WorkflowExecution:
        execution = (
            self._workflow_execution_repository
            .get_by_execution_id(execution_id)
        )

        if execution is None:
            raise LookupError(
                "Workflow execution not found."
            )

        return execution

    @staticmethod
    def _validate_failed_execution(
        execution: WorkflowExecution,
    ) -> None:
        if (
            execution.status
            != WorkflowExecutionStatus.FAILED
        ):
            raise ValueError(
                "Workflow execution is not FAILED."
            )

    def _get_dead_letter(
        self,
        execution: WorkflowExecution,
    ) -> DeadLetterRecord:
        record = (
            self._dead_letter_repository
            .get_by_execution_id(execution.id)
        )

        if record is None:
            raise LookupError(
                "Dead-letter record not found."
            )

        return record

    @staticmethod
    def _validate_dead_letter(
        record: DeadLetterRecord,
    ) -> None:
        if record.status == DeadLetterStatus.RESOLVED:
            raise ValueError(
                "Workflow execution has already been recovered."
            )

        if record.status == DeadLetterStatus.RETRYING:
            raise ValueError(
                "Workflow execution retry is already in progress."
            )

        if record.status != DeadLetterStatus.OPEN:
            raise ValueError(
                "Dead-letter record is not available for retry."
            )

    @staticmethod
    def _reconstruct_email(
        execution: WorkflowExecution,
    ) -> ParsedEmail:
        metadata = execution.execution_metadata

        if (
            not isinstance(metadata, dict)
            or not isinstance(metadata.get("email"), dict)
        ):
            raise ValueError(
                "Original workflow email metadata is unavailable."
            )

        email_metadata = dict(metadata["email"])

        try:
            return ParsedEmail.model_validate(
                email_metadata
            )

        except ValidationError as exc:
            raise ValueError(
                "Original workflow email metadata is invalid."
            ) from exc

    def _get_workflow_service(self) -> Any:
        """
        Return the injected workflow service.

        Production dependency construction must explicitly provide the
        complete WorkflowService because it requires the LLM, normalizer,
        priority, routing, reply-suggestion, and ticket services.
        """

        if self._workflow_service is None:
            raise RuntimeError(
                "WorkflowService is not configured for "
                "failure recovery."
            )

        return self._workflow_service

    def _handle_retry_failure(
        self,
        *,
        dead_letter: DeadLetterRecord,
        retry_execution: WorkflowExecution | None,
    ) -> None:
        """
        Restore administrator-visible dead-letter state after a failed
        manual retry.

        WorkflowService owns its business transaction rollback and failure
        telemetry persistence. This method only restores the dead-letter
        lifecycle state.
        """

        self._session.rollback()

        if retry_execution is None:
            dead_letter.status = DeadLetterStatus.OPEN
            self._session.commit()
            return

        self._dead_letter_repository.mark_retry_failed(
            dead_letter,
            retry_execution_id=retry_execution.id,
        )

        self._session.commit()
