from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketFilters(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    status: str | None = None
    priority: str | None = None
    category: str | None = None
    assigned_team: str | None = None

    limit: int = Field(
        default=50,
        ge=1,
        le=100,
    )

    offset: int = Field(
        default=0,
        ge=0,
    )


class TicketListItem(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
    )

    id: int
    ticket_number: str
    email_subject: str
    category: str
    priority: str
    status: str
    assigned_team: str
    confidence_score: float
    received_at: datetime


class TicketListResult(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    tickets: tuple[TicketListItem, ...]
    total: int
    limit: int
    offset: int


class AttachmentView(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
    )

    id: int
    original_filename: str
    content_type: str | None
    file_size: int


class AuditEventView(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
    )

    id: int
    action: str
    field_name: str | None
    old_value: str | None
    new_value: str | None
    changed_by: str
    created_at: datetime


class WorkflowExecutionView(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
    )

    status: str
    failure_stage: str | None
    error_type: str | None
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None


class TicketDetailView(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
    )

    id: int
    ticket_number: str

    customer_name: str | None
    company: str | None
    sender_email: str

    email_subject: str
    original_email_body: str

    issue_summary: str
    detailed_description: str

    category: str
    priority: str
    sentiment: str

    product_or_service: str | None
    suggested_department: str | None
    assigned_team: str

    confidence_score: float
    status: str

    received_at: datetime
    created_at: datetime
    updated_at: datetime

    priority_reason: str | None = None
    suggested_reply: str | None = None

    attachments: tuple[AttachmentView, ...]
    audit_events: tuple[AuditEventView, ...]
    workflow_execution: WorkflowExecutionView | None
