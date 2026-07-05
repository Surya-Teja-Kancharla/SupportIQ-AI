from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.normalized_ticket_schema import NormalizedTicketAnalysis


class ReplySuggestionRequest(BaseModel):
    """
    Provider-independent input contract for AI-generated support reply suggestions.

    The request consumes trusted normalized ticket analysis together with the
    original customer email context required to generate a relevant response.

    The generated reply is intended for human review and must not be sent
    automatically.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    sender_email: str = Field(
        ...,
        min_length=1,
        description="Email address of the customer who submitted the ticket.",
    )

    email_subject: str = Field(
        ...,
        min_length=1,
        description="Original customer email subject.",
    )

    email_body: str = Field(
        ...,
        min_length=1,
        description="Original customer email body.",
    )

    normalized_analysis: NormalizedTicketAnalysis = Field(
        ...,
        description="Validated and normalized AI ticket analysis.",
    )

    @field_validator(
        "sender_email",
        "email_subject",
        "email_body",
        mode="before",
    )
    @classmethod
    def reject_blank_required_text(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            raise ValueError("value must not be blank")

        return value


class ReplySuggestionResponse(BaseModel):
    """
    Provider-independent output contract for an AI-generated reply suggestion.

    The response intentionally contains only the editable draft reply.
    Delivery, persistence, regeneration, and human approval are responsibilities
    of downstream application services.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    suggested_reply: str = Field(
        ...,
        min_length=1,
        description="AI-generated customer-support reply draft for human review.",
    )

    @field_validator("suggested_reply", mode="before")
    @classmethod
    def reject_blank_suggested_reply(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            raise ValueError("suggested_reply must not be blank")

        return value
