from pathlib import Path

from app.evaluation.classification_evaluation import (
    run_classification_evaluation,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "sample_data"
    / "classification_evaluation_dataset.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "docs"
    / "evaluation_results.json"
)


def main() -> None:
    results = run_classification_evaluation(
        DATASET_PATH,
        OUTPUT_PATH,
    )

    metrics = results["metrics"]

    print()
    print("=" * 60)
    print("SupportIQ Classification Evaluation")
    print("=" * 60)

    print(f"Dataset: {results['dataset_name']}")
    print(f"Samples: {results['total_samples']}")

    print(
        "Category Accuracy: "
        f"{metrics['category_accuracy']:.2%}"
    )

    print(
        "Priority Accuracy: "
        f"{metrics['priority_accuracy']:.2%}"
    )

    print(
        "Routing Accuracy: "
        f"{metrics['routing_accuracy']:.2%}"
    )

    print("=" * 60)

    print(f"Results written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
