from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


FinalPriority = Literal[
    "Critical",
    "High",
    "Medium",
    "Low",
]


class PriorityDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    ai_recommended_priority: FinalPriority

    final_priority: FinalPriority

    applied_rule: str = Field(
        min_length=1,
        max_length=200,
    )

    was_overridden: bool


class RoutingDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    assigned_team: str = Field(
        min_length=1,
        max_length=100,
    )

    routing_rule: str = Field(
        min_length=1,
        max_length=200,
    )


class TicketDecisionResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    priority: PriorityDecision

    routing: RoutingDecision
