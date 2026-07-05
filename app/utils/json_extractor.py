import json
from typing import Any

from app.core.exceptions import LLMJSONExtractionError


def extract_json_object(content: str) -> dict[str, Any]:
    if not content or not content.strip():
        raise LLMJSONExtractionError(
            "LLM response content is empty."
        )

    cleaned = content.strip()

    try:
        parsed = json.loads(cleaned)

        if not isinstance(parsed, dict):
            raise LLMJSONExtractionError(
                "LLM response JSON must be an object."
            )

        return parsed

    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()

    for index, character in enumerate(cleaned):
        if character != "{":
            continue

        try:
            parsed, _ = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            return parsed

    raise LLMJSONExtractionError(
        "No valid JSON object found in LLM response."
    )
