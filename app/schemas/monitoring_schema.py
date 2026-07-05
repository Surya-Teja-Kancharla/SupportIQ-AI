from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str


class TicketPriorityMetric(BaseModel):
    priority: str
    count: int = Field(ge=0)


class TicketStatusMetric(BaseModel):
    status: str
    count: int = Field(ge=0)


class WorkflowExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execution_id: str
    message_id: str
    ticket_id: int | None

    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None

    status: str
    current_stage: str
    retry_count: int

    error_type: str | None
    error_message: str | None


class WorkflowExecutionListResponse(BaseModel):
    items: list[WorkflowExecutionResponse]

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)


class WorkflowMetricsResponse(BaseModel):
    successful_workflows: int = Field(ge=0)
    failed_workflows: int = Field(ge=0)

    average_processing_time_ms: float = Field(ge=0)

    tickets_by_priority: list[TicketPriorityMetric]
    tickets_by_status: list[TicketStatusMetric]
