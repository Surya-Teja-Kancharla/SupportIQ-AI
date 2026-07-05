from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


EvaluationCaseType = Literal[
    "standard",
    "priority_sensitive",
    "ambiguous",
    "adversarial",
]


class ExpectedTicketLabels(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1, max_length=100)
    priority: str = Field(min_length=1, max_length=50)
    sentiment: str = Field(min_length=1, max_length=50)
    suggested_department: str = Field(min_length=1, max_length=100)


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(min_length=1, max_length=100)
    case_type: EvaluationCaseType

    sender_name: str | None = None
    sender_email: EmailStr

    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)

    attachment_text: str | None = None

    expected: ExpectedTicketLabels


class EvaluationDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_name: str = Field(min_length=1)
    dataset_version: str = Field(min_length=1)
    cases: list[EvaluationCase] = Field(min_length=1)


class EvaluationCaseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    case_type: EvaluationCaseType

    success: bool

    expected: ExpectedTicketLabels

    actual_category: str | None = None
    actual_priority: str | None = None
    actual_sentiment: str | None = None
    actual_department: str | None = None

    category_correct: bool = False
    priority_correct: bool = False
    sentiment_correct: bool = False
    department_correct: bool = False

    all_labels_correct: bool = False

    confidence_score: float | None = None

    error_type: str | None = None
    error_message: str | None = None


class CaseTypeMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_cases: int = Field(ge=0)
    successful_analyses: int = Field(ge=0)
    all_labels_correct: int = Field(ge=0)
    all_labels_accuracy: float = Field(ge=0.0, le=1.0)


class EvaluationMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_cases: int = Field(ge=0)
    successful_analyses: int = Field(ge=0)
    failed_analyses: int = Field(ge=0)

    structured_output_validity_rate: float = Field(ge=0.0, le=1.0)

    category_accuracy: float = Field(ge=0.0, le=1.0)
    priority_accuracy: float = Field(ge=0.0, le=1.0)
    sentiment_accuracy: float = Field(ge=0.0, le=1.0)
    department_accuracy: float = Field(ge=0.0, le=1.0)

    standard_case_accuracy: float = Field(ge=0.0, le=1.0)
    priority_sensitive_case_accuracy: float = Field(ge=0.0, le=1.0)
    ambiguous_case_accuracy: float = Field(ge=0.0, le=1.0)
    adversarial_case_accuracy: float = Field(ge=0.0, le=1.0)

    average_confidence: float | None = None
    average_confidence_correct: float | None = None
    average_confidence_incorrect: float | None = None

    high_confidence_error_count: int = Field(ge=0)


class EvaluationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_name: str
    dataset_version: str
    prompt_version: str

    metrics: EvaluationMetrics

    case_type_metrics: dict[str, CaseTypeMetrics]

    results: list[EvaluationCaseResult]
