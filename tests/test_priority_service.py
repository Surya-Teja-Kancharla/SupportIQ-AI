import pytest

from app.core.exceptions import PriorityAssignmentError
from app.schemas.normalized_ticket_schema import (
    NormalizationMetadata,
    NormalizedTicketAnalysis,
)
from app.services.priority_service import PriorityService


def make_analysis(
    *,
    issue_summary: str = "Customer reports a technical issue.",
    detailed_description: str = "The customer needs assistance.",
    category: str = "Technical Support",
    ai_recommended_priority: str = "Medium",
    product_service: str | None = "Customer Portal",
    tags: tuple[str, ...] = ("technical-issue",),
) -> NormalizedTicketAnalysis:
    return NormalizedTicketAnalysis(
        customer_name="Alex Johnson",
        company="Acme Corp",
        issue_summary=issue_summary,
        detailed_description=detailed_description,
        category=category,
        ai_recommended_priority=ai_recommended_priority,
        sentiment="Negative",
        product_service=product_service,
        suggested_department="Technical Support",
        tags=tags,
        confidence_score=0.94,
        normalization_metadata=NormalizationMetadata(
            original_category=category,
            original_priority=ai_recommended_priority,
            original_sentiment="Negative",
            original_department="Technical Support",
            category_was_normalized=False,
            priority_was_normalized=False,
            sentiment_was_normalized=False,
            department_was_normalized=False,
            removed_duplicate_tags=0,
            removed_empty_tags=0,
            confidence_was_clamped=False,
        ),
    )


@pytest.mark.parametrize(
    ("phrase", "expected_priority"),
    [
        ("production outage", "Critical"),
        ("security incident", "Critical"),
        ("complete service unavailable", "Critical"),
        ("payment charged incorrectly", "High"),
        ("account inaccessible", "High"),
        ("major functionality unavailable", "High"),
        ("normal technical issue", "Medium"),
        ("general billing issue", "Medium"),
        ("feature request", "Low"),
        ("general inquiry", "Low"),
    ],
)
def test_assigns_priority_from_business_rules(
    phrase,
    expected_priority,
):
    service = PriorityService()

    analysis = make_analysis(
        issue_summary=phrase,
        ai_recommended_priority="Low",
    )

    result = service.assign_priority(analysis)

    assert result.final_priority == expected_priority


def test_critical_rule_overrides_medium_ai_recommendation():
    service = PriorityService()

    analysis = make_analysis(
        detailed_description=(
            "Customers report a complete service unavailable condition."
        ),
        ai_recommended_priority="Medium",
    )

    result = service.assign_priority(analysis)

    assert result.ai_recommended_priority == "Medium"
    assert result.final_priority == "Critical"
    assert result.was_overridden is True


def test_high_rule_overrides_low_ai_recommendation():
    service = PriorityService()

    analysis = make_analysis(
        issue_summary="Customer reports account inaccessible.",
        ai_recommended_priority="Low",
    )

    result = service.assign_priority(analysis)

    assert result.final_priority == "High"
    assert result.was_overridden is True


def test_lower_rule_does_not_downgrade_ai_priority():
    service = PriorityService()

    analysis = make_analysis(
        issue_summary="Customer submitted a general inquiry.",
        ai_recommended_priority="Critical",
    )

    result = service.assign_priority(analysis)

    assert result.final_priority == "Critical"
    assert result.was_overridden is False


def test_preserves_ai_priority_when_no_rule_matches():
    service = PriorityService()

    analysis = make_analysis(
        issue_summary="Customer needs help updating profile details.",
        detailed_description="No service impact was reported.",
        ai_recommended_priority="Medium",
        tags=("profile-update",),
    )

    result = service.assign_priority(analysis)

    assert result.final_priority == "Medium"
    assert result.was_overridden is False
    assert result.applied_rule == "AI recommendation preserved"


def test_uses_highest_matching_business_rule():
    service = PriorityService()

    analysis = make_analysis(
        issue_summary="Customer reports a general inquiry.",
        detailed_description=(
            "Investigation confirms a production outage."
        ),
        ai_recommended_priority="Low",
    )

    result = service.assign_priority(analysis)

    assert result.final_priority == "Critical"


def test_matches_business_rules_case_insensitively():
    service = PriorityService()

    analysis = make_analysis(
        issue_summary="PRODUCTION OUTAGE affecting all users.",
        ai_recommended_priority="Low",
    )

    result = service.assign_priority(analysis)

    assert result.final_priority == "Critical"


def test_searches_tags():
    service = PriorityService(
        critical_phrases=("production-outage",),
    )

    analysis = make_analysis(
        issue_summary="Customer reports an incident.",
        detailed_description="Further investigation is required.",
        ai_recommended_priority="Low",
        tags=("production-outage",),
    )

    result = service.assign_priority(analysis)

    assert result.final_priority == "Critical"


def test_does_not_mutate_normalized_analysis():
    service = PriorityService()

    analysis = make_analysis(
        issue_summary="Production outage reported.",
        ai_recommended_priority="Low",
    )

    original = analysis.model_dump()

    service.assign_priority(analysis)

    assert analysis.model_dump() == original


def test_rejects_invalid_priority_configuration():
    with pytest.raises(PriorityAssignmentError):
        PriorityService(
            priority_order={
                "Critical": 4,
                "High": 3,
                "Medium": 2,
            }
        )


def test_rejects_duplicate_priority_ranks():
    with pytest.raises(PriorityAssignmentError):
        PriorityService(
            priority_order={
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 2,
            }
        )


def test_rejects_empty_business_rule_collection():
    with pytest.raises(PriorityAssignmentError):
        PriorityService(
            critical_phrases=(),
        )


def test_rejects_empty_business_rule_phrase():
    with pytest.raises(PriorityAssignmentError):
        PriorityService(
            critical_phrases=("",),
        )
