import json

import pytest

from app.evaluation.classification_evaluation import (
    ClassificationEvaluationError,
    ClassificationEvaluator,
    run_classification_evaluation,
)


def build_sample(
    *,
    sample_id: str = "TEST-001",
) -> dict:
    return {
        "id": sample_id,
        "subject": "Production outage",
        "body": (
            "The production service is completely unavailable "
            "and all customers are affected."
        ),
        "predicted_category": "Technical Support",
        "predicted_priority": "High",
        "confidence_score": 0.98,
        "expected_category": "Technical Support",
        "expected_priority": "Critical",
        "expected_route": "Technical Support",
    }


def write_dataset(
    tmp_path,
    samples: list[dict],
):
    path = tmp_path / "classification_dataset.json"

    path.write_text(
        json.dumps(
            {
                "dataset_name": "Test Dataset",
                "version": "1.0",
                "samples": samples,
            }
        ),
        encoding="utf-8",
    )

    return path


def test_load_dataset(tmp_path):
    evaluator = ClassificationEvaluator()

    dataset_path = write_dataset(
        tmp_path,
        [build_sample()],
    )

    dataset = evaluator.load_dataset(dataset_path)

    assert dataset["dataset_name"] == "Test Dataset"
    assert len(dataset["samples"]) == 1


def test_missing_dataset_raises_error(tmp_path):
    evaluator = ClassificationEvaluator()

    missing_path = tmp_path / "missing.json"

    with pytest.raises(
        ClassificationEvaluationError,
        match="not found",
    ):
        evaluator.load_dataset(missing_path)


def test_invalid_json_raises_error(tmp_path):
    evaluator = ClassificationEvaluator()

    dataset_path = tmp_path / "invalid.json"
    dataset_path.write_text("{invalid-json", encoding="utf-8")

    with pytest.raises(
        ClassificationEvaluationError,
        match="invalid JSON",
    ):
        evaluator.load_dataset(dataset_path)


def test_missing_required_field_raises_error(tmp_path):
    evaluator = ClassificationEvaluator()

    sample = build_sample()
    del sample["expected_route"]

    dataset_path = write_dataset(
        tmp_path,
        [sample],
    )

    with pytest.raises(
        ClassificationEvaluationError,
        match="missing required fields",
    ):
        evaluator.load_dataset(dataset_path)


def test_duplicate_sample_id_raises_error(tmp_path):
    evaluator = ClassificationEvaluator()

    dataset_path = write_dataset(
        tmp_path,
        [
            build_sample(sample_id="DUPLICATE"),
            build_sample(sample_id="DUPLICATE"),
        ],
    )

    with pytest.raises(
        ClassificationEvaluationError,
        match="Duplicate sample id",
    ):
        evaluator.load_dataset(dataset_path)


def test_evaluate_sample():
    evaluator = ClassificationEvaluator()

    result = evaluator.evaluate_sample(build_sample())

    assert result["actual"]["category"] == (
        "Technical Support"
    )

    assert result["actual"]["priority"] == "Critical"

    assert result["actual"]["route"] == "Technical Support"

    assert result["correct"] == {
        "category": True,
        "priority": True,
        "routing": True,
    }


def test_evaluate_dataset_calculates_accuracy(tmp_path):
    evaluator = ClassificationEvaluator()

    first_sample = build_sample(sample_id="TEST-001")

    second_sample = build_sample(sample_id="TEST-002")
    second_sample["expected_category"] = "Billing"

    dataset_path = write_dataset(
        tmp_path,
        [
            first_sample,
            second_sample,
        ],
    )

    results = evaluator.evaluate_dataset(dataset_path)

    assert results["total_samples"] == 2

    assert results["metrics"]["category_accuracy"] == 0.5

    assert results["metrics"]["priority_accuracy"] == 1.0

    assert results["metrics"]["routing_accuracy"] == 1.0

    assert results["correct_counts"] == {
        "category": 1,
        "priority": 2,
        "routing": 2,
    }


def test_write_results_creates_json_file(tmp_path):
    evaluator = ClassificationEvaluator()

    output_path = tmp_path / "evaluation_results.json"

    results = {
        "total_samples": 1,
        "metrics": {
            "category_accuracy": 1.0,
            "priority_accuracy": 1.0,
            "routing_accuracy": 1.0,
        },
    }

    written_path = evaluator.write_results(
        results,
        output_path,
    )

    assert written_path == output_path
    assert output_path.exists()

    saved_results = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert saved_results == results


def test_run_classification_evaluation_writes_results(
    tmp_path,
):
    dataset_path = write_dataset(
        tmp_path,
        [build_sample()],
    )

    output_path = tmp_path / "evaluation_results.json"

    results = run_classification_evaluation(
        dataset_path,
        output_path,
    )

    assert output_path.exists()
    assert results["total_samples"] == 1

    assert results["metrics"] == {
        "category_accuracy": 1.0,
        "priority_accuracy": 1.0,
        "routing_accuracy": 1.0,
    }
