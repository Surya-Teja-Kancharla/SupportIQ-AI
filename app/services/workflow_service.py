import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.constants import WorkflowStage
from app.core.exceptions import DuplicateWorkflowError
from app.database.session import create_session
from app.models.workflow_execution import WorkflowExecution
from app.repositories.workflow_execution_repository import (
    WorkflowExecutionRepository,
)
from app.schemas.email_schema import ParsedEmail
from app.schemas.ticket_analysis_schema import TicketAnalysisRequest
from app.schemas.ticket_workflow_schema import TicketProcessingResult
from app.services.llm_service import LLMService
from app.services.priority_service import PriorityService
from app.services.reply_suggestion_service import ReplySuggestionService
from app.services.routing_service import RoutingService
from app.services.ticket_analysis_normalizer import TicketAnalysisNormalizer
from app.services.ticket_service import TicketService
from app.services.workflow_execution_service import (
    WorkflowExecutionService,
)


logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Coordinates the complete ticket-processing application workflow.

    This service owns the SQLAlchemy transaction boundary for the business
    workflow.

    Workflow execution telemetry is persisted independently through
    WorkflowExecutionService so monitoring state can survive business
    transaction rollbacks.

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
        workflow_execution_service: WorkflowExecutionService | None = None,
        workflow_execution_repository: WorkflowExecutionRepository | None = None,
    ) -> None:
        self._session = session
        self._llm_service = llm_service
        self._ticket_analysis_normalizer = ticket_analysis_normalizer
        self._priority_service = priority_service
        self._routing_service = routing_service
        self._reply_suggestion_service = reply_suggestion_service
        self._ticket_service = ticket_service

        self._owns_monitoring_session = False
        self._monitoring_session: Session | None = None

        if workflow_execution_service is not None:
            self._workflow_execution_service = workflow_execution_service

        elif workflow_execution_repository is not None:
            self._workflow_execution_service = WorkflowExecutionService(
                workflow_execution_repository,
            )

        else:
            self._monitoring_session = create_session()
            self._owns_monitoring_session = True

            monitoring_repository = WorkflowExecutionRepository(
                self._monitoring_session
            )

            self._workflow_execution_service = WorkflowExecutionService(
                monitoring_repository,
                session=self._monitoring_session,
            )

    def close(self) -> None:
        """
        Close the internally owned monitoring session.

        Injected WorkflowExecutionService instances remain owned by the
        caller and are therefore not closed here.
        """

        if (
            self._owns_monitoring_session
            and self._monitoring_session is not None
        ):
            self._monitoring_session.close()
            self._monitoring_session = None

    def process_email(
        self,
        email: ParsedEmail,
        workflow_execution: WorkflowExecution | None = None,
    ) -> TicketProcessingResult:
        """
        Execute the ticket-processing business workflow.

        If no workflow execution is supplied, this service creates one.

        If an existing workflow execution is supplied, the service continues
        that execution without creating a duplicate monitoring record.

        Successful processing ends at TICKET_CREATED. Completion and
        acknowledgement telemetry remain owned by EmailIngestionService.
        """

        self._validate_message_id(email)

        if workflow_execution is None:
            existing_execution = (
                self._workflow_execution_service
                .get_by_message_id(email.message_id)
            )

            if existing_execution is not None:
                raise DuplicateWorkflowError(
                    "An email with Message-ID "
                    f"{email.message_id!r} has already been processed."
                )

            workflow_execution = (
                self._workflow_execution_service.start_execution(
                    message_id=email.message_id,
                    stage=WorkflowStage.EMAIL_PARSED,
                )
            )

        elif workflow_execution.message_id != email.message_id:
            raise ValueError(
                "Workflow execution message_id does not match "
                "the parsed email message_id."
            )

        try:
            self._workflow_execution_service.advance_stage(
                workflow_execution,
                stage=WorkflowStage.AI_ANALYSIS_STARTED,
            )

            analysis_request = self._build_analysis_request(email)

            ticket_analysis = self._llm_service.analyze_ticket(
                analysis_request
            )

            self._workflow_execution_service.advance_stage(
                workflow_execution,
                stage=WorkflowStage.AI_ANALYSIS_COMPLETED,
            )

            normalized_analysis = (
                self._ticket_analysis_normalizer.normalize(
                    ticket_analysis
                )
            )

            self._workflow_execution_service.advance_stage(
                workflow_execution,
                stage=WorkflowStage.VALIDATION_COMPLETED,
            )

            priority_decision = self._priority_service.assign_priority(
                normalized_analysis
            )

            self._workflow_execution_service.advance_stage(
                workflow_execution,
                stage=WorkflowStage.PRIORITY_ASSIGNED,
            )

            routing_decision = self._routing_service.route_ticket(
                normalized_analysis
            )

            self._workflow_execution_service.advance_stage(
                workflow_execution,
                stage=WorkflowStage.TEAM_ASSIGNED,
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
                reply_suggestion=reply_suggestion,
            )

            self._session.commit()

            self._workflow_execution_service.attach_ticket(
                workflow_execution,
                ticket_id=ticket_creation_result.ticket_id,
            )

            processed_at = datetime.now(timezone.utc)

            return TicketProcessingResult(
                ticket_id=ticket_creation_result.ticket_id,
                ticket_number=ticket_creation_result.ticket_number,
                execution_id=workflow_execution.execution_id,
                message_id=email.message_id,
                analysis=normalized_analysis,
                priority_decision=priority_decision,
                routing_decision=routing_decision,
                reply_suggestion=reply_suggestion,
                processed_at=processed_at,
            )

        except Exception as exc:
            self._session.rollback()

            try:
                self._workflow_execution_service.fail_execution(
                    workflow_execution,
                    error=exc,
                )

            except Exception:
                logger.exception(
                    "Failed to persist workflow failure telemetry.",
                    extra={
                        "execution_id": (
                            workflow_execution.execution_id
                        ),
                        "message_id": email.message_id,
                    },
                )

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
