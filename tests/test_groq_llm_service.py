from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import httpx

from groq import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    APIStatusError
)

from app.core.exceptions import (
    LLMAuthenticationError,
    LLMJSONExtractionError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
    LLMRequestError
)
from app.schemas.email_schema import ParsedEmail
from app.schemas.ticket_analysis_schema import TicketAnalysisRequest
from app.services.groq_llm_service import GroqLLMService


def make_request() -> TicketAnalysisRequest:
    email = ParsedEmail(
        message_id="message-123",
        sender_name="Alex Johnson",
        sender_email="alex@example.com",
        subject="Cannot access my account",
        body="I cannot log in after resetting my password.",
        received_at=datetime.now(timezone.utc),
    )

    return TicketAnalysisRequest(email=email)


def valid_response_content() -> str:
    return """
    {
        "customer_name": "Alex Johnson",
        "company": null,
        "issue_summary": "Customer cannot access account.",
        "detailed_description": "Customer cannot log in after password reset.",
        "category": "Account Access",
        "priority": "High",
        "sentiment": "Negative",
        "product_service": null,
        "suggested_department": "Technical Support",
        "suggested_tags": ["login", "account-access"],
        "confidence_score": 0.95
    }
    """


def make_completion(content: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=content,
                )
            )
        ]
    )


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setattr(
        "app.services.groq_llm_service.Groq",
        Mock(),
    )

    service = GroqLLMService()

    service.client = Mock()

    service.retry_executor.sleep_function = Mock()
    service.retry_executor.random_function = Mock(
        return_value=0.0
    )

    return service


def test_returns_valid_ticket_analysis(service):
    service.client.chat.completions.create.return_value = (
        make_completion(valid_response_content())
    )

    result = service.analyze_ticket(make_request())

    assert result.category == "Account Access"
    assert result.priority == "High"
    assert result.confidence_score == 0.95

    service.client.chat.completions.create.assert_called_once()


def test_malformed_json_raises_json_extraction_error(service):
    service.client.chat.completions.create.return_value = (
        make_completion("not valid json")
    )

    with pytest.raises(LLMJSONExtractionError):
        service.analyze_ticket(make_request())

    service.client.chat.completions.create.assert_called_once()


def test_schema_invalid_response_raises_response_error(service):
    service.client.chat.completions.create.return_value = (
        make_completion(
            """
            {
                "customer_name": "Alex Johnson",
                "company": null,
                "issue_summary": "Cannot access account.",
                "detailed_description": "Login failure.",
                "category": "Account Access",
                "priority": "High",
                "sentiment": "Negative",
                "product_service": null,
                "suggested_department": "Technical Support",
                "suggested_tags": [],
                "confidence_score": 2.0
            }
            """
        )
    )

    with pytest.raises(LLMResponseError):
        service.analyze_ticket(make_request())

    service.client.chat.completions.create.assert_called_once()


def test_timeout_is_retried_and_preserved(service):
    service.client.chat.completions.create.side_effect = (
        APITimeoutError(request=Mock())
    )

    with pytest.raises(LLMTimeoutError):
        service.analyze_ticket(make_request())

    assert (
        service.client.chat.completions.create.call_count
        == service.retry_executor.policy.max_attempts
    )


def test_rate_limit_is_retried_and_preserved(service):
    service.client.chat.completions.create.side_effect = (
        RateLimitError(
            "Rate limit exceeded.",
            response=Mock(status_code=429),
            body=None,
        )
    )

    with pytest.raises(LLMRateLimitError):
        service.analyze_ticket(make_request())

    assert (
        service.client.chat.completions.create.call_count
        == service.retry_executor.policy.max_attempts
    )


def test_authentication_failure_is_not_retried(service):
    service.client.chat.completions.create.side_effect = (
        AuthenticationError(
            "Authentication failed.",
            response=Mock(status_code=401),
            body=None,
        )
    )

    with pytest.raises(LLMAuthenticationError):
        service.analyze_ticket(make_request())

    service.client.chat.completions.create.assert_called_once()


def test_connection_failure_is_retried_and_preserved(service):
    service.client.chat.completions.create.side_effect = (
        APIConnectionError(request=Mock())
    )

    with pytest.raises(LLMProviderError):
        service.analyze_ticket(make_request())

    assert (
        service.client.chat.completions.create.call_count
        == service.retry_executor.policy.max_attempts
    )


def test_empty_response_is_not_retried(service):
    service.client.chat.completions.create.return_value = (
        make_completion("")
    )

    with pytest.raises(LLMResponseError):
        service.analyze_ticket(make_request())

    service.client.chat.completions.create.assert_called_once()


def test_invalid_completion_structure_is_not_retried(service):
    service.client.chat.completions.create.return_value = (
        SimpleNamespace(choices=[])
    )

    with pytest.raises(LLMResponseError):
        service.analyze_ticket(make_request())

    service.client.chat.completions.create.assert_called_once()

def make_status_error(status_code: int) -> APIStatusError:
    request = httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions",
    )

    response = httpx.Response(
        status_code=status_code,
        request=request,
    )

    return APIStatusError(
        "Groq API error.",
        response=response,
        body=None,
    )

def test_http_500_is_retried_and_preserved(service):
    service.client.chat.completions.create.side_effect = (
        make_status_error(500)
    )

    with pytest.raises(LLMProviderError):
        service.analyze_ticket(make_request())

    assert (
        service.client.chat.completions.create.call_count
        == service.retry_executor.policy.max_attempts
    )


def test_http_400_is_not_retried(service):
    service.client.chat.completions.create.side_effect = (
        make_status_error(400)
    )

    with pytest.raises(LLMRequestError):
        service.analyze_ticket(make_request())

    service.client.chat.completions.create.assert_called_once()
