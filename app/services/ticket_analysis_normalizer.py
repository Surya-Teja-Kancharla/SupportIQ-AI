from collections.abc import Mapping
from types import MappingProxyType

from app.schemas.normalized_ticket_schema import (
    NormalizationMetadata,
    NormalizedTicketAnalysis,
)
from app.schemas.ticket_analysis_schema import TicketAnalysisResponse
from app.utils.text_normalizer import (
    normalize_label,
    normalize_optional_text,
    normalize_tag,
    normalize_text,
)


# ---------------------------------------------------------------------------
# Canonical classification vocabularies
#
# These values must remain consistent with:
# app/prompts/ticket_analysis_v1.py
#
# Alias keys are normalized using normalize_label() before lookup.
# MappingProxyType prevents accidental runtime mutation.
# ---------------------------------------------------------------------------

CATEGORY_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        # Technical Support
        "technical support": "Technical Support",
        "technical issue": "Technical Support",
        "technical problem": "Technical Support",
        "tech support": "Technical Support",
        "support issue": "Technical Support",

        # Billing
        "billing": "Billing",
        "billing issue": "Billing",
        "billing problem": "Billing",
        "payment issue": "Billing",
        "payment problem": "Billing",
        "invoice issue": "Billing",

        # Sales Inquiry
        "sales inquiry": "Sales Inquiry",
        "sales enquiry": "Sales Inquiry",
        "sales question": "Sales Inquiry",
        "pricing inquiry": "Sales Inquiry",
        "pricing enquiry": "Sales Inquiry",
        "purchase inquiry": "Sales Inquiry",

        # Feature Request
        "feature request": "Feature Request",
        "feature suggestion": "Feature Request",
        "feature enhancement": "Feature Request",
        "enhancement request": "Feature Request",
        "product suggestion": "Feature Request",

        # Bug Report
        "bug report": "Bug Report",
        "bug": "Bug Report",
        "software bug": "Bug Report",
        "application bug": "Bug Report",
        "defect": "Bug Report",

        # Account Access
        "account access": "Account Access",
        "login issue": "Account Access",
        "login problem": "Account Access",
        "sign in issue": "Account Access",
        "signin issue": "Account Access",
        "authentication issue": "Account Access",
        "password issue": "Account Access",

        # Refund Request
        "refund request": "Refund Request",
        "refund": "Refund Request",
        "money back request": "Refund Request",
        "reimbursement request": "Refund Request",

        # General Inquiry
        "general inquiry": "General Inquiry",
        "general enquiry": "General Inquiry",
        "general question": "General Inquiry",
        "information request": "General Inquiry",
        "other": "General Inquiry",
    }
)


PRIORITY_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        # Critical
        "critical": "Critical",
        "urgent": "Critical",
        "emergency": "Critical",
        "highest": "Critical",
        "p0": "Critical",
        "sev 0": "Critical",
        "severity 0": "Critical",

        # High
        "high": "High",
        "important": "High",
        "p1": "High",
        "sev 1": "High",
        "severity 1": "High",

        # Medium
        "medium": "Medium",
        "normal": "Medium",
        "moderate": "Medium",
        "standard": "Medium",
        "p2": "Medium",
        "sev 2": "Medium",
        "severity 2": "Medium",

        # Low
        "low": "Low",
        "minor": "Low",
        "non urgent": "Low",
        "nonurgent": "Low",
        "p3": "Low",
        "sev 3": "Low",
        "severity 3": "Low",
    }
)


SENTIMENT_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        # Positive
        "positive": "Positive",
        "happy": "Positive",
        "satisfied": "Positive",
        "pleased": "Positive",
        "grateful": "Positive",

        # Neutral
        "neutral": "Neutral",
        "mixed": "Neutral",
        "unclear": "Neutral",
        "informational": "Neutral",

        # Negative
        "negative": "Negative",
        "angry": "Negative",
        "frustrated": "Negative",
        "upset": "Negative",
        "dissatisfied": "Negative",
        "unhappy": "Negative",
        "annoyed": "Negative",
    }
)


DEPARTMENT_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        # Technical Support
        "technical support": "Technical Support",
        "tech support": "Technical Support",
        "support": "Technical Support",
        "engineering": "Technical Support",
        "technical team": "Technical Support",

        # Finance
        "finance": "Finance",
        "billing": "Finance",
        "billing team": "Finance",
        "accounts": "Finance",
        "accounting": "Finance",

        # Sales
        "sales": "Sales",
        "sales team": "Sales",
        "business development": "Sales",

        # Customer Success
        "customer success": "Customer Success",
        "customer service": "Customer Success",
        "customer support": "Customer Success",
        "success team": "Customer Success",

        # Product Team
        "product team": "Product Team",
        "product": "Product Team",
        "product management": "Product Team",
        "product development": "Product Team",
    }
)


# ---------------------------------------------------------------------------
# Canonical label sets
#
# These sets provide an explicit invariant:
# every normalized classification label must belong to the vocabulary defined
# by the ticket-analysis prompt.
# ---------------------------------------------------------------------------

CANONICAL_CATEGORIES = frozenset(
    {
        "Technical Support",
        "Billing",
        "Sales Inquiry",
        "Feature Request",
        "Bug Report",
        "Account Access",
        "Refund Request",
        "General Inquiry",
    }
)


CANONICAL_PRIORITIES = frozenset(
    {
        "Critical",
        "High",
        "Medium",
        "Low",
    }
)


CANONICAL_SENTIMENTS = frozenset(
    {
        "Positive",
        "Neutral",
        "Negative",
    }
)


CANONICAL_DEPARTMENTS = frozenset(
    {
        "Technical Support",
        "Finance",
        "Sales",
        "Customer Success",
        "Product Team",
    }
)


def canonicalize_label(
    value: str,
    aliases: Mapping[str, str],
    canonical_values: frozenset[str],
) -> str:
    """
    Normalize a classification label and return its canonical value.

    Resolution order:
    1. Normalize the supplied label.
    2. Resolve a known alias.
    3. Match a canonical value case-insensitively.
    4. Preserve the normalized text for downstream validation.

    Unknown labels are intentionally not silently mapped to a fallback
    category. This prevents normalization from hiding classification errors.
    """
    normalized = normalize_label(value)

    alias_match = aliases.get(normalized)

    if alias_match is not None:
        return alias_match

    for canonical_value in canonical_values:
        if normalize_label(canonical_value) == normalized:
            return canonical_value

    return normalize_text(value)


def normalize_tags(
    tags: list[str],
) -> tuple[tuple[str, ...], int, int]:
    """
    Normalize tags while preserving first-seen ordering.

    Returns:
        normalized tags,
        duplicate tag count,
        empty tag count.
    """
    normalized_tags: list[str] = []
    seen: set[str] = set()

    duplicate_count = 0
    empty_count = 0

    for tag in tags:
        normalized = normalize_tag(tag)

        if not normalized:
            empty_count += 1
            continue

        if normalized in seen:
            duplicate_count += 1
            continue

        seen.add(normalized)
        normalized_tags.append(normalized)

    return (
        tuple(normalized_tags),
        duplicate_count,
        empty_count,
    )


def normalize_confidence(value: float) -> tuple[float, bool]:
    """
    Normalize confidence precision defensively.

    TicketAnalysisResponse already rejects values outside [0.0, 1.0].
    Clamping remains a defensive boundary for future callers or schema
    evolution.

    The returned boolean indicates whether range clamping occurred.
    """
    clamped = min(max(value, 0.0), 1.0)
    rounded = round(clamped, 4)

    return rounded, clamped != value


class TicketAnalysisNormalizer:
    """
    Converts a validated TicketAnalysisResponse into the canonical,
    provider-independent NormalizedTicketAnalysis contract.

    This service performs normalization only.

    It does not:
    - call an LLM provider,
    - assign the final business priority,
    - perform team routing,
    - persist ticket data,
    - silently replace unknown labels with fallback classifications.
    """

    def normalize(
        self,
        analysis: TicketAnalysisResponse,
    ) -> NormalizedTicketAnalysis:
        category = canonicalize_label(
            value=analysis.category,
            aliases=CATEGORY_ALIASES,
            canonical_values=CANONICAL_CATEGORIES,
        )

        priority = canonicalize_label(
            value=analysis.priority,
            aliases=PRIORITY_ALIASES,
            canonical_values=CANONICAL_PRIORITIES,
        )

        sentiment = canonicalize_label(
            value=analysis.sentiment,
            aliases=SENTIMENT_ALIASES,
            canonical_values=CANONICAL_SENTIMENTS,
        )

        department = canonicalize_label(
            value=analysis.suggested_department,
            aliases=DEPARTMENT_ALIASES,
            canonical_values=CANONICAL_DEPARTMENTS,
        )

        (
            normalized_tags,
            duplicate_tag_count,
            empty_tag_count,
        ) = normalize_tags(analysis.suggested_tags)

        (
            normalized_confidence,
            confidence_was_clamped,
        ) = normalize_confidence(analysis.confidence_score)

        metadata = NormalizationMetadata(
            original_category=analysis.category,
            original_priority=analysis.priority,
            original_sentiment=analysis.sentiment,
            original_department=analysis.suggested_department,
            category_was_normalized=(
                category != analysis.category
            ),
            priority_was_normalized=(
                priority != analysis.priority
            ),
            sentiment_was_normalized=(
                sentiment != analysis.sentiment
            ),
            department_was_normalized=(
                department != analysis.suggested_department
            ),
            removed_duplicate_tags=duplicate_tag_count,
            removed_empty_tags=empty_tag_count,
            confidence_was_clamped=confidence_was_clamped,
        )

        return NormalizedTicketAnalysis(
            customer_name=normalize_optional_text(
                analysis.customer_name
            ),
            company=normalize_optional_text(
                analysis.company
            ),
            issue_summary=normalize_text(
                analysis.issue_summary
            ),
            detailed_description=normalize_text(
                analysis.detailed_description
            ),
            category=category,
            ai_recommended_priority=priority,
            sentiment=sentiment,
            product_service=normalize_optional_text(
                analysis.product_service
            ),
            suggested_department=department,
            tags=normalized_tags,
            confidence_score=normalized_confidence,
            normalization_metadata=metadata,
        )
