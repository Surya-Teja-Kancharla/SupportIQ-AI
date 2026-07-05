import logging
from datetime import datetime, timezone

from pydantic import ValidationError

from app.core.constants import (
    FailureType,
    LogEvent,
    ProcessingStatus,
)
from app.core.exceptions import (
    EmailConnectionError,
    EmailError,
)
from app.core.logging import get_logger, log_event
from app.schemas.email_schema import ParsedEmail
from app.schemas.ingestion_schema import (
    EmailProcessingResult,
    IngestionBatchResult,
    IngestionFailure,
)
from app.services.imap_service import IMAPService


logger = get_logger(__name__)


class EmailIngestionService:

    def __init__(
        self,
        imap_service: IMAPService | None = None,
    ) -> None:
        self.imap_service = (
            imap_service or IMAPService()
        )

    def _validate_ingested_email(
        self,
        parsed_email: ParsedEmail,
    ) -> list[IngestionFailure]:

        failures: list[IngestionFailure] = []

        if not parsed_email.message_id.strip():
            failures.append(
                IngestionFailure(
                    failure_type=FailureType.VALIDATION_ERROR,
                    message=(
                        "Email does not contain a Message-ID."
                    ),
                    retryable=False,
                )
            )

        if not parsed_email.body.strip():
            failures.append(
                IngestionFailure(
                    failure_type=FailureType.VALIDATION_ERROR,
                    message="Email body is empty.",
                    retryable=False,
                )
            )

        return failures

    def _process_email(
        self,
        imap_message_id: bytes,
        parsed_email: ParsedEmail,
    ) -> EmailProcessingResult:

        imap_id = imap_message_id.decode(
            errors="replace"
        )

        log_event(
            logger,
            logging.INFO,
            LogEvent.EMAIL_PROCESSING_STARTED,
            "Email ingestion processing started.",
            imap_message_id=imap_id,
            message_id=parsed_email.message_id,
            sender_email=str(
                parsed_email.sender_email
            ),
        )

        validation_failures = (
            self._validate_ingested_email(
                parsed_email
            )
        )

        if validation_failures:
            log_event(
                logger,
                logging.WARNING,
                LogEvent.EMAIL_PROCESSING_FAILED,
                "Email ingestion validation failed.",
                imap_message_id=imap_id,
                message_id=parsed_email.message_id,
                failure_count=len(
                    validation_failures
                ),
            )

            return EmailProcessingResult(
                imap_message_id=imap_id,
                message_id=(
                    parsed_email.message_id or None
                ),
                status=ProcessingStatus.FAILED,
                email=parsed_email,
                failures=validation_failures,
            )

        log_event(
            logger,
            logging.INFO,
            LogEvent.EMAIL_PROCESSING_SUCCEEDED,
            "Email ingestion processing succeeded.",
            imap_message_id=imap_id,
            message_id=parsed_email.message_id,
            attachment_count=len(
                parsed_email.attachments
            ),
        )

        return EmailProcessingResult(
            imap_message_id=imap_id,
            message_id=parsed_email.message_id,
            status=ProcessingStatus.SUCCESS,
            email=parsed_email,
        )

    def ingest_unread_emails(
        self,
    ) -> IngestionBatchResult:

        batch_result = IngestionBatchResult()

        try:
            self.imap_service.connect()

            fetched_emails = (
                self.imap_service.fetch_unread_emails()
            )

            batch_result.total_messages = len(
                fetched_emails
            )

            for (
                imap_message_id,
                parsed_email,
            ) in fetched_emails:

                try:
                    processing_result = (
                        self._process_email(
                            imap_message_id,
                            parsed_email,
                        )
                    )

                except ValidationError as exc:
                    processing_result = (
                        EmailProcessingResult(
                            imap_message_id=(
                                imap_message_id.decode(
                                    errors="replace"
                                )
                            ),
                            message_id=(
                                parsed_email.message_id
                                or None
                            ),
                            status=ProcessingStatus.FAILED,
                            email=parsed_email,
                            failures=[
                                IngestionFailure(
                                    failure_type=(
                                        FailureType
                                        .VALIDATION_ERROR
                                    ),
                                    message=str(exc),
                                    exception_type=(
                                        type(exc).__name__
                                    ),
                                    retryable=False,
                                )
                            ],
                        )
                    )

                except Exception as exc:
                    logger.exception(
                        "Unexpected email ingestion failure.",
                        extra={
                            "event": str(
                                LogEvent
                                .EMAIL_PROCESSING_FAILED
                            ),
                            "imap_message_id": (
                                imap_message_id.decode(
                                    errors="replace"
                                )
                            ),
                            "exception_type": (
                                type(exc).__name__
                            ),
                        },
                    )

                    processing_result = (
                        EmailProcessingResult(
                            imap_message_id=(
                                imap_message_id.decode(
                                    errors="replace"
                                )
                            ),
                            message_id=(
                                parsed_email.message_id
                                or None
                            ),
                            status=ProcessingStatus.FAILED,
                            email=parsed_email,
                            failures=[
                                IngestionFailure(
                                    failure_type=(
                                        FailureType
                                        .UNKNOWN_ERROR
                                    ),
                                    message=(
                                        "Unexpected ingestion "
                                        "processing failure."
                                    ),
                                    exception_type=(
                                        type(exc).__name__
                                    ),
                                    retryable=False,
                                )
                            ],
                        )
                    )

                batch_result.results.append(
                    processing_result
                )

                if (
                    processing_result.status
                    == ProcessingStatus.SUCCESS
                ):
                    batch_result.successful_messages += 1

                elif (
                    processing_result.status
                    == ProcessingStatus.SKIPPED
                ):
                    batch_result.skipped_messages += 1

                else:
                    batch_result.failed_messages += 1

        except EmailConnectionError as exc:
            log_event(
                logger,
                logging.ERROR,
                LogEvent.IMAP_CONNECTION_FAILED,
                "Email ingestion batch connection failed.",
                exception_type=type(exc).__name__,
            )

            batch_result.results.append(
                EmailProcessingResult(
                    imap_message_id="",
                    status=ProcessingStatus.FAILED,
                    failures=[
                        IngestionFailure(
                            failure_type=(
                                FailureType.CONNECTION_ERROR
                            ),
                            message=str(exc),
                            exception_type=(
                                type(exc).__name__
                            ),
                            retryable=True,
                        )
                    ],
                )
            )

            batch_result.failed_messages += 1

        except EmailError as exc:
            log_event(
                logger,
                logging.ERROR,
                LogEvent.EMAIL_FETCH_FAILED,
                "Email ingestion batch failed.",
                exception_type=type(exc).__name__,
            )

            batch_result.results.append(
                EmailProcessingResult(
                    imap_message_id="",
                    status=ProcessingStatus.FAILED,
                    failures=[
                        IngestionFailure(
                            failure_type=(
                                FailureType.FETCH_ERROR
                            ),
                            message=str(exc),
                            exception_type=(
                                type(exc).__name__
                            ),
                            retryable=True,
                        )
                    ],
                )
            )

            batch_result.failed_messages += 1

        finally:
            try:
                self.imap_service.disconnect()
            except Exception:
                logger.exception(
                    "Failed to disconnect IMAP service."
                )

            batch_result.completed_at = (
                datetime.now(timezone.utc)
            )

        return batch_result
