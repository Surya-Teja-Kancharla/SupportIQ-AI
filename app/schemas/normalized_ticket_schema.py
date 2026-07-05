from pydantic import BaseModel, ConfigDict, Field


class NormalizationMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    original_category: str
    original_priority: str
    original_sentiment: str
    original_department: str

    category_was_normalized: bool
    priority_was_normalized: bool
    sentiment_was_normalized: bool
    department_was_normalized: bool

    removed_duplicate_tags: int = Field(ge=0)
    removed_empty_tags: int = Field(ge=0)

    confidence_was_clamped: bool


class NormalizedTicketAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    customer_name: str | None
    company: str | None

    issue_summary: str
    detailed_description: str

    category: str
    ai_recommended_priority: str
    sentiment: str

    product_service: str | None
    suggested_department: str

    tags: tuple[str, ...]

    confidence_score: float = Field(ge=0.0, le=1.0)

    normalization_metadata: NormalizationMetadata
