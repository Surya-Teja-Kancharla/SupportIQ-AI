from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.normalized_ticket_schema import NormalizedTicketAnalysis
from app.schemas.reply_suggestion_schema import ReplySuggestionResponse
from app.schemas.ticket_decision_schema import PriorityDecision, RoutingDecision


class TicketCreationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ticket_id: int
    ticket_number: str


class TicketProcessingResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ticket_id: int
    ticket_number: str
    message_id: str
    execution_id: str | None = None

    analysis: NormalizedTicketAnalysis
    priority_decision: PriorityDecision
    routing_decision: RoutingDecision
    reply_suggestion: ReplySuggestionResponse

    processed_at: datetime
