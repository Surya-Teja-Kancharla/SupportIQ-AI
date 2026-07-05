from abc import ABC, abstractmethod

from app.schemas.reply_suggestion_schema import (
    ReplySuggestionRequest,
    ReplySuggestionResponse,
)
from app.schemas.ticket_analysis_schema import (
    TicketAnalysisRequest,
    TicketAnalysisResponse,
)


class LLMService(ABC):
    """
    Provider-independent contract for LLM-backed application capabilities.

    Concrete provider adapters are responsible for implementing ticket analysis
    and customer-support reply suggestion generation.
    """

    @abstractmethod
    def analyze_ticket(
        self,
        request: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:
        """
        Analyze a support ticket using an LLM provider.

        Returns a validated structured ticket-analysis response.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_reply_suggestion(
        self,
        request: ReplySuggestionRequest,
    ) -> ReplySuggestionResponse:
        """
        Generate a customer-support reply draft using an LLM provider.

        The returned reply is a suggestion for human review and must not be
        treated as automatically approved or automatically sent.
        """
        raise NotImplementedError
