import pytest
from pydantic import ValidationError

from app.schemas.normalized_ticket_schema import NormalizedTicketAnalysis
from app.schemas.ticket_analysis_schema import TicketAnalysisResponse
from app.services.ticket_analysis_normalizer import (
    CATEGORY_ALIASES,
    CANONICAL_CATEGORIES,
    TicketAnalysisNormalizer,
    canonicalize_label,
    normalize_confidence,
    normalize_tags,
)


def make_analysis(
    **overrides,
) -> TicketAnalysisResponse:
    data = {
        "customer_name": "Rahul Sharma",
        "company": "Acme Payments",
        "issue_summary": "Production payment API is unavailable",
        "detailed_description": (
            "The production payment API is returning HTTP 503 errors."
        ),
        "category": "Technical Support",
        "priority": "Critical",
        "sentiment": "Negative",
        "product_service": "Payment API",
        "suggested_department": "Technical Support",
        "suggested_tags": [
            "payment-api",
            "http-503",
        ],
        "confidence_score": 0.9,
    }

    data.update(overrides)

    return TicketAnalysisResponse(**data)


def test_normalizer_returns_normalized_ticket_analysis():
    normalizer = TicketAnalysisNormalizer()

    result = normalizer.normalize(make_analysis())

    assert isinstance(result, NormalizedTicketAnalysis)


def test_normalizer_normalizes_required_text_fields():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        issue_summary="  Payment   API is unavailable  ",
        detailed_description=(
            "  Production payment API\n"
            "is returning   HTTP 503 errors.  "
        ),
    )

    result = normalizer.normalize(analysis)

    assert result.issue_summary == "Payment API is unavailable"
    assert (
        result.detailed_description
        == "Production payment API is returning HTTP 503 errors."
    )


def test_normalizer_normalizes_optional_text_fields():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        customer_name="  Rahul   Sharma  ",
        company="  Acme   Payments  ",
        product_service="  Payment   API  ",
    )

    result = normalizer.normalize(analysis)

    assert result.customer_name == "Rahul Sharma"
    assert result.company == "Acme Payments"
    assert result.product_service == "Payment API"


def test_normalizer_converts_empty_optional_text_to_none():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        customer_name="   ",
        company=" \n ",
        product_service="\t",
    )

    result = normalizer.normalize(analysis)

    assert result.customer_name is None
    assert result.company is None
    assert result.product_service is None


def test_normalizer_canonicalizes_category_alias():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        category="tech_support",
    )

    result = normalizer.normalize(analysis)

    assert result.category == "Technical Support"
    assert result.normalization_metadata.category_was_normalized is True


def test_normalizer_canonicalizes_priority_alias():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        priority="urgent",
    )

    result = normalizer.normalize(analysis)

    assert result.ai_recommended_priority == "Critical"
    assert result.normalization_metadata.priority_was_normalized is True


def test_normalizer_canonicalizes_sentiment_alias():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        sentiment="frustrated",
    )

    result = normalizer.normalize(analysis)

    assert result.sentiment == "Negative"
    assert result.normalization_metadata.sentiment_was_normalized is True


def test_normalizer_canonicalizes_department_alias():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        suggested_department="engineering",
    )

    result = normalizer.normalize(analysis)

    assert result.suggested_department == "Technical Support"
    assert result.normalization_metadata.department_was_normalized is True


def test_normalizer_preserves_canonical_labels():
    normalizer = TicketAnalysisNormalizer()

    result = normalizer.normalize(make_analysis())

    assert result.category == "Technical Support"
    assert result.ai_recommended_priority == "Critical"
    assert result.sentiment == "Negative"
    assert result.suggested_department == "Technical Support"

    assert (
        result.normalization_metadata.category_was_normalized
        is False
    )
    assert (
        result.normalization_metadata.priority_was_normalized
        is False
    )
    assert (
        result.normalization_metadata.sentiment_was_normalized
        is False
    )
    assert (
        result.normalization_metadata.department_was_normalized
        is False
    )


def test_canonicalize_label_matches_canonical_value_case_insensitively():
    result = canonicalize_label(
        value="BUG REPORT",
        aliases=CATEGORY_ALIASES,
        canonical_values=CANONICAL_CATEGORIES,
    )

    assert result == "Bug Report"


def test_canonicalize_label_preserves_unknown_normalized_value():
    result = canonicalize_label(
        value="  Unexpected   Category  ",
        aliases=CATEGORY_ALIASES,
        canonical_values=CANONICAL_CATEGORIES,
    )

    assert result == "Unexpected Category"


def test_normalize_tags_lowercases_and_slug_normalizes():
    tags, duplicate_count, empty_count = normalize_tags(
        [
            "Payment API",
            "HTTP 503 Error",
        ]
    )

    assert tags == (
        "payment-api",
        "http-503-error",
    )
    assert duplicate_count == 0
    assert empty_count == 0


def test_normalize_tags_removes_duplicates():
    tags, duplicate_count, empty_count = normalize_tags(
        [
            "Payment API",
            "payment-api",
            "PAYMENT_API",
        ]
    )

    assert tags == ("payment-api",)
    assert duplicate_count == 2
    assert empty_count == 0


def test_normalize_tags_preserves_first_seen_order():
    tags, _, _ = normalize_tags(
        [
            "HTTP 503",
            "Payment API",
            "Production",
            "http-503",
        ]
    )

    assert tags == (
        "http-503",
        "payment-api",
        "production",
    )


def test_normalize_tags_removes_empty_tags():
    tags, duplicate_count, empty_count = normalize_tags(
        [
            "Payment API",
            "",
            "   ",
            "!!!",
            "HTTP 503",
        ]
    )

    assert tags == (
        "payment-api",
        "http-503",
    )
    assert duplicate_count == 0
    assert empty_count == 3


def test_normalizer_records_tag_metadata():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        suggested_tags=[
            "Payment API",
            "payment-api",
            "",
            "!!!",
            "HTTP 503",
        ]
    )

    result = normalizer.normalize(analysis)

    assert result.tags == (
        "payment-api",
        "http-503",
    )

    assert (
        result.normalization_metadata.removed_duplicate_tags
        == 1
    )

    assert (
        result.normalization_metadata.removed_empty_tags
        == 2
    )


def test_normalize_confidence_rounds_deterministically():
    confidence, was_clamped = normalize_confidence(0.876543)

    assert confidence == 0.8765
    assert was_clamped is False


def test_normalizer_rounds_confidence():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        confidence_score=0.876543,
    )

    result = normalizer.normalize(analysis)

    assert result.confidence_score == 0.8765
    assert result.normalization_metadata.confidence_was_clamped is False


def test_normalizer_does_not_mutate_original_analysis():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        category="tech_support",
        suggested_tags=[
            "Payment API",
            "payment-api",
        ],
        confidence_score=0.876543,
    )

    original_dump = analysis.model_dump()

    normalizer.normalize(analysis)

    assert analysis.model_dump() == original_dump


def test_normalized_result_is_immutable():
    normalizer = TicketAnalysisNormalizer()

    result = normalizer.normalize(make_analysis())

    with pytest.raises(ValidationError):
        result.category = "Billing"


def test_normalization_metadata_is_immutable():
    normalizer = TicketAnalysisNormalizer()

    result = normalizer.normalize(make_analysis())

    with pytest.raises(ValidationError):
        result.normalization_metadata.original_category = "Billing"


def test_normalized_schema_rejects_unexpected_fields():
    normalizer = TicketAnalysisNormalizer()

    result = normalizer.normalize(make_analysis())

    data = result.model_dump()
    data["unexpected_field"] = "invalid"

    with pytest.raises(ValidationError):
        NormalizedTicketAnalysis(**data)


def test_normalizer_preserves_original_labels_in_metadata():
    normalizer = TicketAnalysisNormalizer()

    analysis = make_analysis(
        category="tech_support",
        priority="urgent",
        sentiment="frustrated",
        suggested_department="engineering",
    )

    result = normalizer.normalize(analysis)

    metadata = result.normalization_metadata

    assert metadata.original_category == "tech_support"
    assert metadata.original_priority == "urgent"
    assert metadata.original_sentiment == "frustrated"
    assert metadata.original_department == "engineering"
