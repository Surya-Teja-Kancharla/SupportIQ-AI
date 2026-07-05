from collections.abc import Mapping

from app.config.routing_rules import CATEGORY_TEAM_ROUTES
from app.core.exceptions import (
    RoutingConfigurationError,
    UnmappedCategoryError,
)
from app.schemas.normalized_ticket_schema import (
    NormalizedTicketAnalysis,
)
from app.schemas.ticket_decision_schema import RoutingDecision


class RoutingService:
    def __init__(
        self,
        routes: Mapping[str, str] = CATEGORY_TEAM_ROUTES,
    ) -> None:
        self.routes = dict(routes)

        self._validate_configuration()

    def route_ticket(
        self,
        analysis: NormalizedTicketAnalysis,
    ) -> RoutingDecision:
        category = analysis.category

        assigned_team = self.routes.get(category)

        if assigned_team is None:
            raise UnmappedCategoryError(
                f"No routing rule configured for category: {category}"
            )

        return RoutingDecision(
            category=category,
            assigned_team=assigned_team,
            routing_rule=(
                f"Category '{category}' routed to "
                f"'{assigned_team}'"
            ),
        )

    def _validate_configuration(self) -> None:
        if not self.routes:
            raise RoutingConfigurationError(
                "Routing configuration cannot be empty."
            )

        for category, team in self.routes.items():
            if not category or not category.strip():
                raise RoutingConfigurationError(
                    "Routing category cannot be empty."
                )

            if not team or not team.strip():
                raise RoutingConfigurationError(
                    "Routing team cannot be empty."
                )
