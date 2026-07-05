from pydantic import BaseModel, Field


class CategoryUpdateRequest(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    performed_by: str = Field(default="support-agent", min_length=1, max_length=100)


class PriorityUpdateRequest(BaseModel):
    priority: str = Field(min_length=1, max_length=20)
    performed_by: str = Field(default="support-agent", min_length=1, max_length=100)


class TeamReassignmentRequest(BaseModel):
    assigned_team: str = Field(min_length=1, max_length=100)
    performed_by: str = Field(default="support-agent", min_length=1, max_length=100)


class StatusUpdateRequest(BaseModel):
    status: str = Field(min_length=1, max_length=30)
    performed_by: str = Field(default="support-agent", min_length=1, max_length=100)


class InternalNoteCreateRequest(BaseModel):
    note: str = Field(min_length=1)
    created_by: str = Field(default="support-agent", min_length=1, max_length=100)


class SuggestedReplyUpdateRequest(BaseModel):
    suggested_reply: str = Field(min_length=1)
    performed_by: str = Field(default="support-agent", min_length=1, max_length=100)


class SuggestedReplyRegenerateRequest(BaseModel):
    performed_by: str = Field(default="support-agent", min_length=1, max_length=100)
