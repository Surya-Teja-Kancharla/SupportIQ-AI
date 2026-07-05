from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateWorkflowError
from app.models import WorkflowExecution
from app.repositories import WorkflowExecutionRepository
from app.schemas.email_schema import ParsedEmail
from app.schemas.ticket_analysis_schema import TicketAnalysisRequest
from app.schemas.ticket_workflow_schema import TicketProcessingResult
from app.services.llm_service import LLMService
from app.services.priority_service import PriorityService
from app.services.reply_suggestion_service import ReplySuggestionService
from app.services.routing_service import RoutingService
from app.services.ticket_analysis_normalizer import TicketAnalysisNormalizer
from app.services.ticket_service import TicketService


class WorkflowService:
    """
    Coordinates the complete ticket-processing application workflow.

    This service owns the SQLAlchemy transaction boundary for the complete
    workflow.

    Repositories and TicketService deliberately do not commit or roll back.
    """

    def __init__(
        self,
        session: Session,
        llm_service: LLMService,
        ticket_analysis_normalizer: TicketAnalysisNormalizer,
        priority_service: PriorityService,
        routing_service: RoutingService,
        reply_suggestion_service: ReplySuggestionService,
        ticket_service: TicketService,
        workflow_execution_repository: WorkflowExecutionRepository,
    ) -> None:
        self._session = session
        self._llm_service = llm_service
        self._ticket_analysis_normalizer = ticket_analysis_normalizer
        self._priority_service = priority_service
        self._routing_service = routing_service
        self._reply_suggestion_service = reply_suggestion_service
        self._ticket_service = ticket_service
        self._workflow_execution_repository = (
            workflow_execution_repository
        )

    def process_email(
        self,
        email: ParsedEmail,
    ) -> TicketProcessingResult:
        """
        Execute the complete ticket-processing workflow.

        Processing sequence:

        1. Validate Message-ID.
        2. Enforce Message-ID idempotency.
        3. Execute AI ticket analysis.
        4. Normalize AI analysis.
        5. Assign deterministic final priority.
        6. Route the ticket.
        7. Generate AI reply suggestion.
        8. Create ticket persistence aggregate.
        9. Create workflow execution record.
        10. Commit the transaction.
        11. Return immutable workflow result.

        Any failure causes transaction rollback and preserves the original
        typed exception.
        """

        try:
            self._validate_message_id(email)

            existing_execution = (
                self._workflow_execution_repository.get_by_message_id(
                    email.message_id
                )
            )

            if existing_execution is not None:
                raise DuplicateWorkflowError(
                    "An email with Message-ID "
                    f"{email.message_id!r} has already been processed."
                )

            analysis_request = self._build_analysis_request(email)

            ticket_analysis = self._llm_service.analyze_ticket(
                analysis_request
            )

            normalized_analysis = (
                self._ticket_analysis_normalizer.normalize(ticket_analysis)
            )

            priority_decision = self._priority_service.assign_priority(
                normalized_analysis
            )

            routing_decision = self._routing_service.route_ticket(
                normalized_analysis
            )

            reply_suggestion = (
                self._reply_suggestion_service.generate_suggestion(
                    email=email,
                    analysis=normalized_analysis,
                )
            )

            ticket_creation_result = self._ticket_service.create_ticket(
                email=email,
                analysis=normalized_analysis,
                priority_decision=priority_decision,
                routing_decision=routing_decision,
            )

            processed_at = datetime.now(timezone.utc)

            workflow_execution = WorkflowExecution(
                message_id=email.message_id,
                ticket_id=ticket_creation_result.ticket_id,
                status="completed",
                failure_stage=None,
                error_type=None,
                error_message=None,
                execution_metadata={
                    "ticket_number": (
                        ticket_creation_result.ticket_number
                    ),
                    "final_priority": priority_decision.final_priority,
                    "assigned_team": routing_decision.assigned_team,
                },
                started_at=processed_at,
                completed_at=processed_at,
            )

            self._workflow_execution_repository.add(
                workflow_execution
            )

            self._session.commit()

            return TicketProcessingResult(
                ticket_id=ticket_creation_result.ticket_id,
                ticket_number=ticket_creation_result.ticket_number,
                message_id=email.message_id,
                analysis=normalized_analysis,
                priority_decision=priority_decision,
                routing_decision=routing_decision,
                reply_suggestion=reply_suggestion,
                processed_at=processed_at,
            )

        except Exception:
            self._session.rollback()
            raise

    @staticmethod
    def _validate_message_id(email: ParsedEmail) -> None:
        if not email.message_id or not email.message_id.strip():
            raise ValueError(
                "Parsed email Message-ID must not be empty."
            )

    @staticmethod
    def _build_analysis_request(
        email: ParsedEmail,
    ) -> TicketAnalysisRequest:
        return TicketAnalysisRequest(
            email=email,
        )
