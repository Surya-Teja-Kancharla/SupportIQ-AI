from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ParsedAttachment(BaseModel):
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str | None = None
    size_bytes: int = Field(ge=0)


class ParsedEmail(BaseModel):
    message_id: str

    sender_name: str | None = None
    sender_email: EmailStr

    subject: str
    body: str

    received_at: datetime

    attachments: list[ParsedAttachment] = Field(default_factory=list)