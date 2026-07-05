from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WorkflowRetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    original_execution_id: int
    retry_execution_id: int
    attempt_number: int
    status: str


class DeadLetterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_execution_id: int
    ticket_id: int | None

    failed_stage: str
    exception_type: str
    sanitized_error_message: str

    retry_count: int
    retry_exhausted: bool

    status: str
    manual_retry_count: int

    created_at: datetime
    updated_at: datetime
