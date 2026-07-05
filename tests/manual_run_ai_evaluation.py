from pathlib import Path

from app.config.settings import settings
from app.evaluation.runner import EvaluationRunner
from app.services.groq_llm_service import GroqLLMService


ROOT_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    ROOT_DIR
    / "sample_data"
    / "ai_evaluation_dataset.json"
)

REPORT_PATH = (
    ROOT_DIR
    / "docs"
    / "ai_evaluation_report.json"
)


def main() -> None:
    service = GroqLLMService()

    runner = EvaluationRunner(
        llm_service=service,
        prompt_version=settings.prompt_version,
    )

    report = runner.run(DATASET_PATH)

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )

    print("\nSUPPORTIQ AI EVALUATION")
    print("=" * 60)
    print(f"Dataset: {report.dataset_name}")
    print(f"Dataset version: {report.dataset_version}")
    print(f"Prompt version: {report.prompt_version}")
    print("-" * 60)

    metrics = report.metrics

    print(f"Total cases: {metrics.total_cases}")
    print(
        f"Successful analyses: "
        f"{metrics.successful_analyses}"
    )
    print(
        f"Failed analyses: "
        f"{metrics.failed_analyses}"
    )

    print(
        "Structured output validity: "
        f"{metrics.structured_output_validity_rate:.2%}"
    )

    print(
        f"Category accuracy: "
        f"{metrics.category_accuracy:.2%}"
    )
    print(
        f"Priority accuracy: "
        f"{metrics.priority_accuracy:.2%}"
    )
    print(
        f"Sentiment accuracy: "
        f"{metrics.sentiment_accuracy:.2%}"
    )
    print(
        f"Department accuracy: "
        f"{metrics.department_accuracy:.2%}"
    )

    print("-" * 60)

    for case_type, case_metrics in (
        report.case_type_metrics.items()
    ):
        print(
            f"{case_type}: "
            f"{case_metrics.all_labels_accuracy:.2%} "
            f"all-label accuracy"
        )

    print("-" * 60)

    print(
        f"Average confidence: "
        f"{metrics.average_confidence}"
    )
    print(
        f"Average confidence (correct): "
        f"{metrics.average_confidence_correct}"
    )
    print(
        f"Average confidence (incorrect): "
        f"{metrics.average_confidence_incorrect}"
    )
    print(
        f"High-confidence errors: "
        f"{metrics.high_confidence_error_count}"
    )

    print("=" * 60)
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
