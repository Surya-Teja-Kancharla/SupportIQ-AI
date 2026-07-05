from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.core.exceptions import LLMResponseError
from app.schemas.email_schema import ParsedEmail
from app.schemas.normalized_ticket_schema import (
    NormalizationMetadata,
    NormalizedTicketAnalysis,
)
from app.schemas.reply_suggestion_schema import ReplySuggestionResponse
from app.services.reply_suggestion_service import ReplySuggestionService


def make_email() -> ParsedEmail:
    return ParsedEmail(
        message_id="message-123",
        sender_name="Alex Johnson",
        sender_email="alex@example.com",
        subject="Cannot access my account",
        body="I cannot log in after resetting my password.",
        received_at=datetime.now(timezone.utc),
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


@pytest.fixture
def llm_service():
    service = Mock()
    service.generate_reply_suggestion.return_value = (
        ReplySuggestionResponse(
            suggested_reply="Thank you for contacting us."
        )
    )

    return service


def test_generates_valid_reply_suggestion(llm_service):
    service = ReplySuggestionService(llm_service)

    result = service.generate_suggestion(
        email=make_email(),
        normalized_analysis=make_normalized_analysis(),
    )

    assert isinstance(result, ReplySuggestionResponse)
    assert result.suggested_reply == "Thank you for contacting us."

    llm_service.generate_reply_suggestion.assert_called_once()


def test_constructs_provider_independent_request(llm_service):
    service = ReplySuggestionService(llm_service)

    email = make_email()
    analysis = make_normalized_analysis()

    service.generate_suggestion(
        email=email,
        normalized_analysis=analysis,
    )

    request = (
        llm_service.generate_reply_suggestion.call_args.args[0]
    )

    assert request.sender_email == str(email.sender_email)
    assert request.email_subject == email.subject
    assert request.email_body == email.body
    assert request.normalized_analysis is analysis


def test_reply_whitespace_is_normalized(llm_service):
    llm_service.generate_reply_suggestion.return_value = (
        ReplySuggestionResponse(
            suggested_reply=(
                "  Thank you   for contacting us.\n"
                "We understand your issue.  "
            )
        )
    )

    service = ReplySuggestionService(llm_service)

    result = service.generate_suggestion(
        email=make_email(),
        normalized_analysis=make_normalized_analysis(),
    )

    assert (
        result.suggested_reply
        == "Thank you for contacting us. We understand your issue."
    )


def test_oversized_reply_is_rejected(llm_service):
    llm_service.generate_reply_suggestion.return_value = (
        ReplySuggestionResponse(
            suggested_reply="A" * 101
        )
    )

    service = ReplySuggestionService(
        llm_service,
        max_reply_length=100,
    )

    with pytest.raises(LLMResponseError):
        service.generate_suggestion(
            email=make_email(),
            normalized_analysis=make_normalized_analysis(),
        )


def test_reply_at_maximum_length_is_accepted(llm_service):
    llm_service.generate_reply_suggestion.return_value = (
        ReplySuggestionResponse(
            suggested_reply="A" * 100
        )
    )

    service = ReplySuggestionService(
        llm_service,
        max_reply_length=100,
    )

    result = service.generate_suggestion(
        email=make_email(),
        normalized_analysis=make_normalized_analysis(),
    )

    assert len(result.suggested_reply) == 100


def test_rejects_non_positive_maximum_reply_length(llm_service):
    with pytest.raises(ValueError):
        ReplySuggestionService(
            llm_service,
            max_reply_length=0,
        )


def test_original_normalized_analysis_is_not_mutated(llm_service):
    service = ReplySuggestionService(llm_service)

    analysis = make_normalized_analysis()
    original_dump = analysis.model_dump()

    service.generate_suggestion(
        email=make_email(),
        normalized_analysis=analysis,
    )

    assert analysis.model_dump() == original_dump


def test_original_email_is_not_mutated(llm_service):
    service = ReplySuggestionService(llm_service)

    email = make_email()
    original_dump = email.model_dump()

    service.generate_suggestion(
        email=email,
        normalized_analysis=make_normalized_analysis(),
    )

    assert email.model_dump() == original_dump


def test_returns_new_response_after_normalization(llm_service):
    provider_response = ReplySuggestionResponse(
        suggested_reply="Thank you   for contacting us."
    )

    llm_service.generate_reply_suggestion.return_value = (
        provider_response
    )

    service = ReplySuggestionService(llm_service)

    result = service.generate_suggestion(
        email=make_email(),
        normalized_analysis=make_normalized_analysis(),
    )

    assert result is not provider_response
    assert result.suggested_reply == "Thank you for contacting us."


def test_provider_failure_is_propagated(llm_service):
    llm_service.generate_reply_suggestion.side_effect = (
        LLMResponseError("Provider returned an invalid reply.")
    )

    service = ReplySuggestionService(llm_service)

    with pytest.raises(LLMResponseError):
        service.generate_suggestion(
            email=make_email(),
            normalized_analysis=make_normalized_analysis(),
        )

    llm_service.generate_reply_suggestion.assert_called_once()
