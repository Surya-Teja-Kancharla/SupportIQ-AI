from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.core.constants import (
    FailureType,
    ProcessingStatus,
)
from app.schemas.email_schema import ParsedEmail


class IngestionFailure(BaseModel):
    failure_type: FailureType

    message: str

    exception_type: str | None = None

    retryable: bool = False


class EmailProcessingResult(BaseModel):
    imap_message_id: str

    message_id: str | None = None

    status: ProcessingStatus

    email: ParsedEmail | None = None

    failures: list[IngestionFailure] = Field(
        default_factory=list
    )

    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


class IngestionBatchResult(BaseModel):
    total_messages: int = 0

    successful_messages: int = 0

    failed_messages: int = 0

    skipped_messages: int = 0

    results: list[EmailProcessingResult] = Field(
        default_factory=list
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    completed_at: datetime | None = None

    @property
    def success_rate(self) -> float:
        if self.total_messages == 0:
            return 100.0

        return (
            self.successful_messages
            / self.total_messages
        ) * 100
