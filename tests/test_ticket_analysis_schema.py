import pytest
from pydantic import ValidationError

from app.schemas.ticket_analysis_schema import TicketAnalysisResponse


def valid_payload() -> dict:
    return {
        "customer_name": "Alex Johnson",
        "company": "Acme Corp",
        "issue_summary": "Customer cannot access account.",
        "detailed_description": (
            "Customer reports repeated login failures."
        ),
        "category": "Account Access",
        "priority": "High",
        "sentiment": "Negative",
        "product_service": "Customer Portal",
        "suggested_department": "Technical Support",
        "suggested_tags": [
            "login",
            "account-access",
        ],
        "confidence_score": 0.94,
    }


def test_valid_ticket_analysis_response():
    result = TicketAnalysisResponse.model_validate(valid_payload())

    assert result.category == "Account Access"
    assert result.confidence_score == 0.94


def test_rejects_missing_required_field():
    payload = valid_payload()
    del payload["issue_summary"]

    with pytest.raises(ValidationError):
        TicketAnalysisResponse.model_validate(payload)


def test_rejects_confidence_above_one():
    payload = valid_payload()
    payload["confidence_score"] = 1.5

    with pytest.raises(ValidationError):
        TicketAnalysisResponse.model_validate(payload)


def test_rejects_extra_fields():
    payload = valid_payload()
    payload["unexpected_field"] = "value"

    with pytest.raises(ValidationError):
        TicketAnalysisResponse.model_validate(payload)
