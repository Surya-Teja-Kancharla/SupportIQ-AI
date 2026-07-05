from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.schemas.email_schema import ParsedEmail


class TicketAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: ParsedEmail
    attachment_text: str | None = None


class TicketAnalysisResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_name: str | None = None
    company: str | None = None

    issue_summary: str = Field(min_length=1, max_length=300)

    detailed_description: str = Field(min_length=1, max_length=5000)

    category: str = Field(min_length=1, max_length=100)

    priority: str = Field(min_length=1, max_length=50)

    sentiment: str = Field(min_length=1, max_length=50)

    product_service: str | None = Field(default=None, max_length=200)

    suggested_department: str = Field(min_length=1, max_length=100)

    suggested_tags: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("suggested_tags", "tags"),
    )

    confidence_score: float = Field(ge=0.0, le=1.0)
