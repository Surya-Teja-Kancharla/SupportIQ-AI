import pytest

from app.evaluation.metrics import calculate_evaluation_metrics
from app.schemas.evaluation_schema import (
    EvaluationCaseResult,
    ExpectedTicketLabels,
)


def expected_labels() -> ExpectedTicketLabels:
    return ExpectedTicketLabels(
        category="Billing",
        priority="Medium",
        sentiment="Negative",
        suggested_department="Finance",
    )


def make_result(
    case_id: str,
    case_type: str,
    *,
    success: bool = True,
    category_correct: bool = True,
    priority_correct: bool = True,
    sentiment_correct: bool = True,
    department_correct: bool = True,
    confidence_score: float | None = 0.9,
) -> EvaluationCaseResult:

    all_labels_correct = all(
        (
            category_correct,
            priority_correct,
            sentiment_correct,
            department_correct,
        )
    )

    return EvaluationCaseResult(
        case_id=case_id,
        case_type=case_type,
        success=success,
        expected=expected_labels(),
        actual_category="Billing" if success else None,
        actual_priority="Medium" if success else None,
        actual_sentiment="Negative" if success else None,
        actual_department="Finance" if success else None,
        category_correct=category_correct if success else False,
        priority_correct=priority_correct if success else False,
        sentiment_correct=sentiment_correct if success else False,
        department_correct=department_correct if success else False,
        all_labels_correct=all_labels_correct if success else False,
        confidence_score=confidence_score if success else None,
        error_type=None if success else "LLMProviderError",
        error_message=None if success else "Provider failed.",
    )


def test_calculates_per_label_accuracy():
    results = [
        make_result(
            "standard-001",
            "standard",
        ),
        make_result(
            "standard-002",
            "standard",
            priority_correct=False,
        ),
    ]

    metrics, _ = calculate_evaluation_metrics(results)

    assert metrics.category_accuracy == 1.0
    assert metrics.priority_accuracy == 0.5
    assert metrics.sentiment_accuracy == 1.0
    assert metrics.department_accuracy == 1.0


def test_failed_analysis_reduces_validity_and_accuracy():
    results = [
        make_result(
            "standard-001",
            "standard",
        ),
        make_result(
            "standard-002",
            "standard",
            success=False,
        ),
    ]

    metrics, _ = calculate_evaluation_metrics(results)

    assert metrics.structured_output_validity_rate == 0.5
    assert metrics.category_accuracy == 0.5


def test_calculates_case_type_accuracy():
    results = [
        make_result(
            "standard-001",
            "standard",
        ),
        make_result(
            "standard-002",
            "standard",
            category_correct=False,
        ),
        make_result(
            "priority-001",
            "priority_sensitive",
        ),
        make_result(
            "ambiguous-001",
            "ambiguous",
        ),
        make_result(
            "adversarial-001",
            "adversarial",
        ),
    ]

    metrics, case_type_metrics = (
        calculate_evaluation_metrics(results)
    )

    assert metrics.standard_case_accuracy == 0.5
    assert (
        case_type_metrics["priority_sensitive"]
        .all_labels_accuracy
        == 1.0
    )
    assert metrics.ambiguous_case_accuracy == 1.0
    assert metrics.adversarial_case_accuracy == 1.0


def test_calculates_confidence_statistics():
    results = [
        make_result(
            "standard-001",
            "standard",
            confidence_score=0.9,
        ),
        make_result(
            "standard-002",
            "standard",
            category_correct=False,
            confidence_score=0.8,
        ),
    ]

    metrics, _ = calculate_evaluation_metrics(results)

    assert metrics.average_confidence == pytest.approx(0.85)
    assert metrics.average_confidence_correct == pytest.approx(0.9)
    assert metrics.average_confidence_incorrect == pytest.approx(0.8)
    assert metrics.high_confidence_error_count == 1


def test_handles_empty_results():
    metrics, case_type_metrics = (
        calculate_evaluation_metrics([])
    )

    assert metrics.total_cases == 0
    assert metrics.structured_output_validity_rate == 0.0
    assert metrics.category_accuracy == 0.0
    assert metrics.average_confidence is None

    assert (
        case_type_metrics["standard"]
        .all_labels_accuracy
        == 0.0
    )
