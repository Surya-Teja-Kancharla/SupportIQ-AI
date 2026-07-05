import re
import unicodedata


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return normalize_whitespace(normalized).strip()


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = normalize_text(value)

    return normalized or None


def normalize_label(value: str) -> str:
    normalized = normalize_text(value).casefold()

    normalized = re.sub(r"[\s_-]+", " ", normalized)

    return normalized.strip()


def normalize_tag(value: str) -> str:
    normalized = normalize_text(value).casefold()

    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)

    return normalized.strip("-")
