import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.schemas.normalized_ticket_schema import (
    NormalizedTicketAnalysis,
)
from app.services.priority_service import PriorityService
from app.services.routing_service import RoutingService


class ClassificationEvaluationError(Exception):
    """Raised when classification evaluation cannot be completed."""


class ClassificationEvaluator:
    REQUIRED_FIELDS = {
        "id",
        "subject",
        "body",
        "predicted_category",
        "predicted_priority",
        "confidence_score",
        "expected_category",
        "expected_priority",
        "expected_route",
    }

    def __init__(
        self,
        priority_service: PriorityService | None = None,
        routing_service: RoutingService | None = None,
    ) -> None:
        self.priority_service = priority_service or PriorityService()
        self.routing_service = routing_service or RoutingService()

    def load_dataset(
        self,
        dataset_path: str | Path,
    ) -> dict[str, Any]:
        path = Path(dataset_path)

        if not path.exists():
            raise ClassificationEvaluationError(
                f"Classification dataset not found: {path}"
            )

        try:
            with path.open("r", encoding="utf-8") as file:
                dataset = json.load(file)
        except json.JSONDecodeError as exc:
            raise ClassificationEvaluationError(
                f"Classification dataset contains invalid JSON: {path}"
            ) from exc

        if not isinstance(dataset, dict):
            raise ClassificationEvaluationError(
                "Classification dataset must be a JSON object."
            )

        samples = dataset.get("samples")

        if not isinstance(samples, list) or not samples:
            raise ClassificationEvaluationError(
                "Classification dataset must contain a non-empty "
                "'samples' list."
            )

        self._validate_samples(samples)

        return dataset

    def _validate_samples(
        self,
        samples: list[dict[str, Any]],
    ) -> None:
        sample_ids: set[str] = set()

        for index, sample in enumerate(samples, start=1):
            if not isinstance(sample, dict):
                raise ClassificationEvaluationError(
                    f"Sample {index} must be a JSON object."
                )

            missing_fields = (
                self.REQUIRED_FIELDS - set(sample.keys())
            )

            if missing_fields:
                raise ClassificationEvaluationError(
                    f"Sample {index} is missing required fields: "
                    f"{sorted(missing_fields)}"
                )

            sample_id = str(sample["id"])

            if not sample_id.strip():
                raise ClassificationEvaluationError(
                    f"Sample {index} has an empty id."
                )

            if sample_id in sample_ids:
                raise ClassificationEvaluationError(
                    f"Duplicate sample id: {sample_id}"
                )

            sample_ids.add(sample_id)

    @staticmethod
    def _build_analysis(
        sample: dict[str, Any],
    ) -> NormalizedTicketAnalysis:
        subject = str(sample["subject"])
        body = str(sample["body"])
        category = str(sample["predicted_category"])
        predicted_priority = str(
            sample["predicted_priority"]
        )
        confidence_score = float(
            sample["confidence_score"]
        )

        return NormalizedTicketAnalysis(
            customer_name="Evaluation Customer",
            company="Evaluation Dataset",
            issue_summary=subject,
            detailed_description=body,
            category=category,
            ai_recommended_priority=predicted_priority,
            sentiment="Neutral",
            product_service="SupportIQ",
            suggested_department="Evaluation",
            confidence_score=confidence_score,
            tags=[],
            normalization_metadata={
                "original_category": category,
                "original_priority": predicted_priority,
                "original_sentiment": "Neutral",
                "original_department": "Evaluation",
                "category_was_normalized": False,
                "priority_was_normalized": False,
                "sentiment_was_normalized": False,
                "department_was_normalized": False,
                "removed_duplicate_tags": 0,
                "removed_empty_tags": 0,
                "confidence_was_clamped": False,
            },
        )

    def _evaluate_priority(
        self,
        analysis: NormalizedTicketAnalysis,
    ) -> str:
        decision = self.priority_service.assign_priority(
            analysis
        )

        return decision.final_priority

    def _evaluate_route(
        self,
        analysis: NormalizedTicketAnalysis,
    ) -> str:
        decision = self.routing_service.route_ticket(
            analysis
        )

        return decision.assigned_team

    def evaluate_sample(
        self,
        sample: dict[str, Any],
    ) -> dict[str, Any]:
        analysis = self._build_analysis(sample)

        actual_category = analysis.category

        actual_priority = self._evaluate_priority(
            analysis
        )

        actual_route = self._evaluate_route(
            analysis
        )

        category_correct = (
            actual_category == sample["expected_category"]
        )

        priority_correct = (
            actual_priority == sample["expected_priority"]
        )

        routing_correct = (
            actual_route == sample["expected_route"]
        )

        return {
            "id": sample["id"],
            "expected": {
                "category": sample["expected_category"],
                "priority": sample["expected_priority"],
                "route": sample["expected_route"],
            },
            "actual": {
                "category": actual_category,
                "priority": actual_priority,
                "route": actual_route,
            },
            "correct": {
                "category": category_correct,
                "priority": priority_correct,
                "routing": routing_correct,
            },
        }

    def evaluate_dataset(
        self,
        dataset_path: str | Path,
    ) -> dict[str, Any]:
        dataset = self.load_dataset(dataset_path)

        sample_results = [
            self.evaluate_sample(sample)
            for sample in dataset["samples"]
        ]

        total_samples = len(sample_results)

        category_correct = sum(
            int(result["correct"]["category"])
            for result in sample_results
        )

        priority_correct = sum(
            int(result["correct"]["priority"])
            for result in sample_results
        )

        routing_correct = sum(
            int(result["correct"]["routing"])
            for result in sample_results
        )

        return {
            "dataset_name": dataset.get(
                "dataset_name",
                "Classification Evaluation Dataset",
            ),
            "dataset_version": dataset.get(
                "version",
                "unknown",
            ),
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "total_samples": total_samples,
            "metrics": {
                "category_accuracy": (
                    category_correct / total_samples
                ),
                "priority_accuracy": (
                    priority_correct / total_samples
                ),
                "routing_accuracy": (
                    routing_correct / total_samples
                ),
            },
            "correct_counts": {
                "category": category_correct,
                "priority": priority_correct,
                "routing": routing_correct,
            },
            "sample_results": sample_results,
        }

    @staticmethod
    def write_results(
        results: dict[str, Any],
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                results,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return path


def run_classification_evaluation(
    dataset_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    evaluator = ClassificationEvaluator()

    results = evaluator.evaluate_dataset(
        dataset_path
    )

    evaluator.write_results(
        results,
        output_path,
    )

    return results
