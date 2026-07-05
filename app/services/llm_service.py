from abc import ABC, abstractmethod

from app.schemas.ticket_analysis_schema import (
    TicketAnalysisRequest,
    TicketAnalysisResponse,
)


class LLMService(ABC):

    @abstractmethod
    def analyze_ticket(
        self,
        request: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:
        """Analyze a support ticket using an LLM provider."""
        raise NotImplementedError
