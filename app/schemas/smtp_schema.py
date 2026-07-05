from pydantic import BaseModel, EmailStr, Field


class OutboundEmail(BaseModel):
    recipient_email: EmailStr

    subject: str = Field(
        min_length=1,
        max_length=998,
    )

    plain_text_body: str = Field(
        min_length=1,
    )

    html_body: str | None = None

    reply_to: EmailStr | None = None


class EmailDeliveryResult(BaseModel):
    success: bool

    recipient_email: EmailStr

    message_id: str | None = None

    error_message: str | None = None
