import pytest
from pydantic import ValidationError

from app.schemas.normalized_ticket_schema import (
    NormalizationMetadata,
    NormalizedTicketAnalysis,
)
from app.schemas.reply_suggestion_schema import (
    ReplySuggestionRequest,
    ReplySuggestionResponse,
)


def make_normalized_analysis() -> NormalizedTicketAnalysis:
    return NormalizedTicketAnalysis(
        customer_name="Alex Johnson",
        company=None,
        issue_summary="Customer cannot access account.",
        detailed_description=(
            "Customer cannot log in after resetting the password."
        ),
        category="Account Access",
        ai_recommended_priority="High",
        sentiment="Negative",
        product_service=None,
        suggested_department="Technical Support",
        tags=("login", "account-access"),
        confidence_score=0.95,
        normalization_metadata=NormalizationMetadata(
            original_category="Account Access",
            original_priority="High",
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


def test_valid_reply_suggestion_request():
    request = ReplySuggestionRequest(
        sender_email="alex@example.com",
        email_subject="Cannot access my account",
        email_body="I cannot log in after resetting my password.",
        normalized_analysis=make_normalized_analysis(),
    )

    assert request.sender_email == "alex@example.com"
    assert request.email_subject == "Cannot access my account"
    assert request.normalized_analysis.category == "Account Access"


@pytest.mark.parametrize(
    "field_name",
    [
        "sender_email",
        "email_subject",
        "email_body",
    ],
)
def test_request_rejects_blank_required_text(field_name):
    data = {
        "sender_email": "alex@example.com",
        "email_subject": "Cannot access my account",
        "email_body": "I cannot log in.",
        "normalized_analysis": make_normalized_analysis(),
    }

    data[field_name] = "   "

    with pytest.raises(ValidationError):
        ReplySuggestionRequest(**data)


def test_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ReplySuggestionRequest(
            sender_email="alex@example.com",
            email_subject="Cannot access my account",
            email_body="I cannot log in.",
            normalized_analysis=make_normalized_analysis(),
            unexpected_field="invalid",
        )


def test_valid_reply_suggestion_response():
    response = ReplySuggestionResponse(
        suggested_reply=(
            "Thank you for contacting us. "
            "We understand that you are unable to access your account."
        )
    )

    assert response.suggested_reply.startswith("Thank you")


def test_response_strips_leading_and_trailing_whitespace():
    response = ReplySuggestionResponse(
        suggested_reply="   Thank you for contacting us.   "
    )

    assert response.suggested_reply == "Thank you for contacting us."


def test_response_rejects_empty_reply():
    with pytest.raises(ValidationError):
        ReplySuggestionResponse(
            suggested_reply="",
        )


def test_response_rejects_whitespace_only_reply():
    with pytest.raises(ValidationError):
        ReplySuggestionResponse(
            suggested_reply="   \n\t   ",
        )


def test_response_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ReplySuggestionResponse(
            suggested_reply="Thank you for contacting us.",
            unexpected_field="invalid",
        )


def test_response_is_immutable():
    response = ReplySuggestionResponse(
        suggested_reply="Thank you for contacting us."
    )

    with pytest.raises(ValidationError):
        response.suggested_reply = "Changed reply."
