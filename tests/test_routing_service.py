import pytest

from app.core.exceptions import (
    RoutingConfigurationError,
    UnmappedCategoryError,
)
from app.schemas.normalized_ticket_schema import (
    NormalizationMetadata,
    NormalizedTicketAnalysis,
)
from app.services.routing_service import RoutingService


def make_analysis(
    category: str,
) -> NormalizedTicketAnalysis:
    return NormalizedTicketAnalysis(
        customer_name="Alex Johnson",
        company="Acme Corp",
        issue_summary="Customer reports an issue.",
        detailed_description="Customer requires assistance.",
        category=category,
        ai_recommended_priority="Medium",
        sentiment="Neutral",
        product_service="Customer Portal",
        suggested_department="Customer Success",
        tags=("support",),
        confidence_score=0.90,
        normalization_metadata=NormalizationMetadata(
            original_category=category,
            original_priority="Medium",
            original_sentiment="Neutral",
            original_department="Customer Success",
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
    ("category", "expected_team"),
    [
        ("Technical Support", "Technical Support"),
        ("Billing", "Finance"),
        ("Sales Inquiry", "Sales"),
        ("Feature Request", "Product Team"),
        ("Bug Report", "Technical Support"),
        ("Account Access", "Customer Success"),
        ("Refund Request", "Finance"),
        ("General Inquiry", "Customer Success"),
    ],
)
def test_routes_all_supported_categories(
    category,
    expected_team,
):
    service = RoutingService()

    analysis = make_analysis(category)

    result = service.route_ticket(analysis)

    assert result.category == category
    assert result.assigned_team == expected_team


def test_supports_injected_routing_configuration():
    service = RoutingService(
        routes={
            "Technical Support": "Platform Engineering",
        }
    )

    analysis = make_analysis("Technical Support")

    result = service.route_ticket(analysis)

    assert result.assigned_team == "Platform Engineering"


def test_rejects_unmapped_category():
    service = RoutingService()

    analysis = make_analysis("Unsupported Category")

    with pytest.raises(UnmappedCategoryError):
        service.route_ticket(analysis)


def test_rejects_empty_routing_configuration():
    with pytest.raises(RoutingConfigurationError):
        RoutingService(routes={})


def test_rejects_empty_category():
    with pytest.raises(RoutingConfigurationError):
        RoutingService(
            routes={
                "": "Customer Success",
            }
        )


def test_rejects_empty_team():
    with pytest.raises(RoutingConfigurationError):
        RoutingService(
            routes={
                "General Inquiry": "",
            }
        )


def test_does_not_mutate_normalized_analysis():
    service = RoutingService()

    analysis = make_analysis("Billing")

    original = analysis.model_dump()

    service.route_ticket(analysis)

    assert analysis.model_dump() == original
