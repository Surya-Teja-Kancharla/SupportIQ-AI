PRIORITY_RESPONSE_TIME = {
    "CRITICAL": "Within 1 hour",
    "HIGH": "Within 4 hours",
    "MEDIUM": "Within 1 business day",
    "LOW": "Within 2 business days",
}

DEFAULT_RESPONSE_TIME = "Within 1 business day"


def get_estimated_response_time(priority: str | None) -> str:
    if priority is None:
        return DEFAULT_RESPONSE_TIME

    normalized_priority = priority.strip().upper()

    return PRIORITY_RESPONSE_TIME.get(
        normalized_priority,
        DEFAULT_RESPONSE_TIME,
    )
