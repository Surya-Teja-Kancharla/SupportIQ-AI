from app.utils.text_normalizer import (
    normalize_label,
    normalize_optional_text,
    normalize_tag,
    normalize_text,
    normalize_whitespace,
)


def test_normalize_whitespace_collapses_repeated_whitespace():
    result = normalize_whitespace(
        "Payment    API\tis\ncurrently   unavailable"
    )

    assert result == "Payment API is currently unavailable"


def test_normalize_whitespace_strips_leading_and_trailing_whitespace():
    result = normalize_whitespace("   Payment API   ")

    assert result == "Payment API"


def test_normalize_text_normalizes_unicode_nfkc():
    result = normalize_text("Ｐａｙｍｅｎｔ　ＡＰＩ")

    assert result == "Payment API"


def test_normalize_text_collapses_whitespace():
    result = normalize_text("  Production   payment\nAPI  ")

    assert result == "Production payment API"


def test_normalize_optional_text_returns_none_for_none():
    assert normalize_optional_text(None) is None


def test_normalize_optional_text_returns_none_for_empty_string():
    assert normalize_optional_text("") is None


def test_normalize_optional_text_returns_none_for_whitespace_only_string():
    assert normalize_optional_text("   \n\t  ") is None


def test_normalize_optional_text_normalizes_non_empty_value():
    result = normalize_optional_text("  Rahul   Sharma  ")

    assert result == "Rahul Sharma"


def test_normalize_label_casefolds_value():
    result = normalize_label("TECHNICAL SUPPORT")

    assert result == "technical support"


def test_normalize_label_normalizes_spaces_underscores_and_hyphens():
    assert normalize_label("Technical_Support") == "technical support"
    assert normalize_label("Technical-Support") == "technical support"
    assert normalize_label("Technical   Support") == "technical support"


def test_normalize_tag_casefolds_value():
    result = normalize_tag("Payment API")

    assert result == "payment-api"


def test_normalize_tag_replaces_special_characters_with_hyphen():
    result = normalize_tag("HTTP 503 / Payment Failure!")

    assert result == "http-503-payment-failure"


def test_normalize_tag_removes_leading_and_trailing_hyphens():
    result = normalize_tag("---Payment API---")

    assert result == "payment-api"


def test_normalize_tag_returns_empty_string_for_punctuation_only_value():
    result = normalize_tag("!!!___---")

    assert result == ""
