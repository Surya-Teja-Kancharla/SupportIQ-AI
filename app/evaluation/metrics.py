from collections import defaultdict

from app.schemas.evaluation_schema import (
    CaseTypeMetrics,
    EvaluationCaseResult,
    EvaluationMetrics,
)


HIGH_CONFIDENCE_THRESHOLD = 0.8


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def _average(values: list[float]) -> float | None:
    if not values:
        return None

    return sum(values) / len(values)


def calculate_evaluation_metrics(
    results: list[EvaluationCaseResult],
) -> tuple[EvaluationMetrics, dict[str, CaseTypeMetrics]]:

    total_cases = len(results)

    successful_results = [
        result
        for result in results
        if result.success
    ]

    failed_analyses = total_cases - len(successful_results)

    category_correct = sum(
        result.category_correct
        for result in successful_results
    )

    priority_correct = sum(
        result.priority_correct
        for result in successful_results
    )

    sentiment_correct = sum(
        result.sentiment_correct
        for result in successful_results
    )

    department_correct = sum(
        result.department_correct
        for result in successful_results
    )

    confidences = [
        result.confidence_score
        for result in successful_results
        if result.confidence_score is not None
    ]

    correct_confidences = [
        result.confidence_score
        for result in successful_results
        if result.all_labels_correct
        and result.confidence_score is not None
    ]

    incorrect_confidences = [
        result.confidence_score
        for result in successful_results
        if not result.all_labels_correct
        and result.confidence_score is not None
    ]

    high_confidence_error_count = sum(
        1
        for result in successful_results
        if not result.all_labels_correct
        and result.confidence_score is not None
        and result.confidence_score >= HIGH_CONFIDENCE_THRESHOLD
    )

    grouped_results: dict[
        str,
        list[EvaluationCaseResult],
    ] = defaultdict(list)

    for result in results:
        grouped_results[result.case_type].append(result)

    case_type_metrics: dict[str, CaseTypeMetrics] = {}

    for case_type in (
        "standard",
        "priority_sensitive",
        "ambiguous",
        "adversarial",
    ):
        group = grouped_results[case_type]

        group_successes = [
            result
            for result in group
            if result.success
        ]

        group_all_correct = sum(
            result.all_labels_correct
            for result in group_successes
        )

        case_type_metrics[case_type] = CaseTypeMetrics(
            total_cases=len(group),
            successful_analyses=len(group_successes),
            all_labels_correct=group_all_correct,
            all_labels_accuracy=_safe_rate(
                group_all_correct,
                len(group),
            ),
        )

    metrics = EvaluationMetrics(
        total_cases=total_cases,
        successful_analyses=len(successful_results),
        failed_analyses=failed_analyses,
        structured_output_validity_rate=_safe_rate(len(successful_results), total_cases),
        category_accuracy=_safe_rate(category_correct, total_cases),
        priority_accuracy=_safe_rate(priority_correct, total_cases),
        sentiment_accuracy=_safe_rate(sentiment_correct, total_cases),
        department_accuracy=_safe_rate(department_correct, total_cases),
        standard_case_accuracy=case_type_metrics["standard"].all_labels_accuracy,
        priority_sensitive_case_accuracy=case_type_metrics["priority_sensitive"].all_labels_accuracy,
        ambiguous_case_accuracy=case_type_metrics["ambiguous"].all_labels_accuracy,
        adversarial_case_accuracy=case_type_metrics["adversarial"].all_labels_accuracy,
        average_confidence=_average(confidences),
        average_confidence_correct=_average(correct_confidences),
        average_confidence_incorrect=_average(incorrect_confidences),
        high_confidence_error_count=(high_confidence_error_count),
    )

    return metrics, case_type_metrics
