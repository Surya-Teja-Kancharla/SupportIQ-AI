import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.evaluation_schema import EvaluationDataset


DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "sample_data"
    / "ai_evaluation_dataset.json"
)


def load_dataset_payload() -> dict:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_evaluation_dataset_is_valid():
    dataset = EvaluationDataset.model_validate(
        load_dataset_payload()
    )

    assert dataset.dataset_name == (
        "supportiq-ticket-analysis-evaluation"
    )
    assert dataset.dataset_version == "1.0.0"
    assert len(dataset.cases) == 24


def test_evaluation_dataset_has_unique_case_ids():
    dataset = EvaluationDataset.model_validate(
        load_dataset_payload()
    )

    case_ids = [case.case_id for case in dataset.cases]

    assert len(case_ids) == len(set(case_ids))


def test_evaluation_dataset_contains_all_case_types():
    dataset = EvaluationDataset.model_validate(
        load_dataset_payload()
    )

    case_types = {case.case_type for case in dataset.cases}

    assert case_types == {
        "standard",
        "priority_sensitive",
        "ambiguous",
        "adversarial",
    }


def test_evaluation_dataset_rejects_unknown_case_type():
    payload = load_dataset_payload()
    payload["cases"][0]["case_type"] = "unknown"

    with pytest.raises(ValidationError):
        EvaluationDataset.model_validate(payload)


def test_evaluation_dataset_rejects_extra_fields():
    payload = load_dataset_payload()
    payload["unexpected_field"] = "value"

    with pytest.raises(ValidationError):
        EvaluationDataset.model_validate(payload)
