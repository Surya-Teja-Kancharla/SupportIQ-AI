import pytest

from app.core.exceptions import LLMJSONExtractionError
from app.utils.json_extractor import extract_json_object


def test_extracts_clean_json_object():
    result = extract_json_object('{"category": "Billing"}')

    assert result == {"category": "Billing"}


def test_extracts_json_from_markdown_code_fence():
    content = """
    ```json
    {
        "category": "Billing"
    }
    ```
    """

    result = extract_json_object(content)

    assert result == {"category": "Billing"}


def test_extracts_json_surrounded_by_text():
    content = """
    Here is the result:

    {
        "category": "Technical Support"
    }

    Done.
    """

    result = extract_json_object(content)

    assert result == {
        "category": "Technical Support"
    }


def test_handles_braces_inside_json_strings():
    content = """
    Result:
    {
        "detailed_description": "Customer received error {code 500}.",
        "category": "Technical Support"
    }
    """

    result = extract_json_object(content)

    assert result["category"] == "Technical Support"


def test_rejects_json_array():
    with pytest.raises(LLMJSONExtractionError):
        extract_json_object('["Billing", "Technical Support"]')


def test_rejects_empty_response():
    with pytest.raises(LLMJSONExtractionError):
        extract_json_object("")


def test_rejects_response_without_json():
    with pytest.raises(LLMJSONExtractionError):
        extract_json_object(
            "The customer has a billing issue."
        )
