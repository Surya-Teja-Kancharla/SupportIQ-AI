from collections.abc import Mapping, Sequence

from app.config.priority_rules import (
    CRITICAL_PHRASES,
    HIGH_PHRASES,
    LOW_PHRASES,
    MEDIUM_PHRASES,
    PRIORITY_ORDER,
)
from app.core.exceptions import PriorityAssignmentError
from app.schemas.normalized_ticket_schema import (
    NormalizedTicketAnalysis,
)
from app.schemas.ticket_decision_schema import PriorityDecision
from app.utils.text_normalizer import normalize_text


class PriorityService:
    def __init__(
        self,
        priority_order: Mapping[str, int] = PRIORITY_ORDER,
        critical_phrases: Sequence[str] = CRITICAL_PHRASES,
        high_phrases: Sequence[str] = HIGH_PHRASES,
        medium_phrases: Sequence[str] = MEDIUM_PHRASES,
        low_phrases: Sequence[str] = LOW_PHRASES,
    ) -> None:
        self.priority_order = priority_order

        self.rules = (
            ("Critical", tuple(critical_phrases)),
            ("High", tuple(high_phrases)),
            ("Medium", tuple(medium_phrases)),
            ("Low", tuple(low_phrases)),
        )

        self._validate_configuration()

    def assign_priority(
        self,
        analysis: NormalizedTicketAnalysis,
    ) -> PriorityDecision:
        ai_priority = analysis.ai_recommended_priority

        if ai_priority not in self.priority_order:
            raise PriorityAssignmentError(
                "Unsupported AI-recommended priority: "
                f"{ai_priority}"
            )

        searchable_text = self._build_searchable_text(analysis)

        matched_priority, matched_phrase = self._find_highest_rule_match(
            searchable_text
        )

        if matched_priority is None:
            return PriorityDecision(
                ai_recommended_priority=ai_priority,
                final_priority=ai_priority,
                applied_rule="AI recommendation preserved",
                was_overridden=False,
            )

        final_priority = self._higher_priority(
            ai_priority,
            matched_priority,
        )

        was_overridden = final_priority != ai_priority

        if was_overridden:
            applied_rule = (
                f"Matched '{matched_phrase}' business rule "
                f"for {matched_priority} priority"
            )
        else:
            applied_rule = (
                f"AI recommendation preserved over matched "
                f"'{matched_phrase}' {matched_priority} rule"
            )

        return PriorityDecision(
            ai_recommended_priority=ai_priority,
            final_priority=final_priority,
            applied_rule=applied_rule,
            was_overridden=was_overridden,
        )

    def _build_searchable_text(
        self,
        analysis: NormalizedTicketAnalysis,
    ) -> str:
        fields = (
            analysis.issue_summary,
            analysis.detailed_description,
            analysis.category,
            analysis.product_service or "",
            " ".join(analysis.tags),
        )

        return normalize_text(" ".join(fields)).casefold()

    def _find_highest_rule_match(
        self,
        searchable_text: str,
    ) -> tuple[str | None, str | None]:
        for priority, phrases in self.rules:
            for phrase in phrases:
                normalized_phrase = normalize_text(phrase).casefold()

                if normalized_phrase in searchable_text:
                    return priority, phrase

        return None, None

    def _higher_priority(
        self,
        first_priority: str,
        second_priority: str,
    ) -> str:
        if (
            self.priority_order[first_priority]
            >= self.priority_order[second_priority]
        ):
            return first_priority

        return second_priority

    def _validate_configuration(self) -> None:
        required_priorities = {
            "Critical",
            "High",
            "Medium",
            "Low",
        }

        configured_priorities = set(self.priority_order)

        if configured_priorities != required_priorities:
            raise PriorityAssignmentError(
                "Priority order configuration must contain exactly: "
                "Critical, High, Medium, Low."
            )

        if len(set(self.priority_order.values())) != len(
            self.priority_order
        ):
            raise PriorityAssignmentError(
                "Priority order ranks must be unique."
            )

        for priority, phrases in self.rules:
            if priority not in self.priority_order:
                raise PriorityAssignmentError(
                    f"Missing priority rank for: {priority}"
                )

            if not phrases:
                raise PriorityAssignmentError(
                    f"No business rules configured for: {priority}"
                )

            if any(
                not phrase or not phrase.strip()
                for phrase in phrases
            ):
                raise PriorityAssignmentError(
                    f"Empty business rule configured for: {priority}"
                )
