from types import MappingProxyType


PRIORITY_ORDER = MappingProxyType(
    {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4,
    }
)


CRITICAL_PHRASES = (
    "production outage",
    "security incident",
    "complete service unavailable",
)


HIGH_PHRASES = (
    "payment charged incorrectly",
    "account inaccessible",
    "major functionality unavailable",
)


MEDIUM_PHRASES = (
    "normal technical issue",
    "general billing issue",
)


LOW_PHRASES = (
    "feature request",
    "general inquiry",
)
