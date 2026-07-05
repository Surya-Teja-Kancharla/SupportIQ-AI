from datetime import datetime, timedelta, timezone

from app.database.session import SessionLocal
from app.repositories import (
    AttachmentRepository,
    AuditRepository,
    TicketRepository,
    WorkflowExecutionRepository,
)
from app.schemas.email_schema import ParsedEmail
from app.schemas.reply_suggestion_schema import (
    ReplySuggestionRequest,
    ReplySuggestionResponse,
)
from app.schemas.ticket_analysis_schema import (
    TicketAnalysisRequest,
    TicketAnalysisResponse,
)
from app.services.llm_service import LLMService
from app.services.priority_service import PriorityService
from app.services.reply_suggestion_service import ReplySuggestionService
from app.services.routing_service import RoutingService
from app.services.ticket_analysis_normalizer import TicketAnalysisNormalizer
from app.services.ticket_service import TicketService
from app.services.workflow_execution_service import WorkflowExecutionService
from app.services.workflow_service import WorkflowService


DEMO_MESSAGE_PREFIX = "supportiq-demo-seed"


class DeterministicDemoLLMService(LLMService):
    """
    Deterministic LLM implementation used only for local demo-data creation.

    Ticket analysis is selected using the ParsedEmail Message-ID.
    Reply suggestions are generated locally without calling an external
    AI provider.
    """

    def __init__(
        self,
        analyses: dict[str, TicketAnalysisResponse],
    ) -> None:
        self._analyses = analyses

    def analyze_ticket(
        self,
        request: TicketAnalysisRequest,
    ) -> TicketAnalysisResponse:
        message_id = request.email.message_id

        analysis = self._analyses.get(message_id)

        if analysis is None:
            raise ValueError(
                f"No deterministic demo analysis configured for {message_id}."
            )

        return analysis

    def generate_reply_suggestion(
        self,
        request: ReplySuggestionRequest,
    ) -> ReplySuggestionResponse:
        category = request.normalized_analysis.category

        replies = {
            "Technical Support": (
                "Thank you for reporting the production issue. "
                "Our technical support team is investigating the incident "
                "and will provide updates as more information becomes available."
            ),
            "Account Access": (
                "Thank you for reporting the account access problem. "
                "Our support team will review the login issue and help restore "
                "access to your account."
            ),
            "Billing": (
                "Thank you for contacting us about the billing discrepancy. "
                "Our finance team will review the invoice and payment records "
                "and follow up with the findings."
            ),
            "Feature Request": (
                "Thank you for sharing your feature suggestion. "
                "Our product team will review the request and consider it "
                "during future product planning."
            ),
            "Refund Request": (
                "Thank you for submitting your refund request. "
                "Our finance team will review the transaction details and "
                "provide an update on the request."
            ),
            "Sales Inquiry": (
                "Thank you for your interest in our services. "
                "Our sales team will review your requirements and contact you "
                "with the relevant information."
            ),
            "General Inquiry": (
                "Thank you for contacting SupportIQ. "
                "Our customer success team will review your question and "
                "provide the requested information."
            ),
        }

        return ReplySuggestionResponse(
            suggested_reply=replies[category],
        )


def build_demo_cases():
    now = datetime.now(timezone.utc)

    return [
        (
            ParsedEmail(
                message_id=(
                    f"<{DEMO_MESSAGE_PREFIX}-production-outage"
                    "@supportiq.local>"
                ),
                sender_name="Anita Rao",
                sender_email="anita.rao@example.com",
                subject="Production outage affecting all customers",
                body=(
                    "Our production service is unavailable for all customers. "
                    "This is a complete outage and business operations are "
                    "blocked. Please restore service immediately."
                ),
                received_at=now - timedelta(minutes=35),
                attachments=[],
            ),
            TicketAnalysisResponse(
                customer_name="Anita Rao",
                company="Northstar Systems",
                issue_summary=(
                    "Complete production outage affecting all customers"
                ),
                detailed_description=(
                    "The customer reports that the production service is "
                    "unavailable for all users and business operations are "
                    "blocked."
                ),
                category="Technical Support",
                priority="High",
                sentiment="Negative",
                product_service="Production Service",
                suggested_department="Technical Support",
                suggested_tags=[
                    "production outage",
                    "all customers",
                    "service unavailable",
                ],
                confidence_score=0.98,
            ),
        ),
        (
            ParsedEmail(
                message_id=(
                    f"<{DEMO_MESSAGE_PREFIX}-account-access"
                    "@supportiq.local>"
                ),
                sender_name="Rahul Mehta",
                sender_email="rahul.mehta@example.com",
                subject="Unable to access administrator account",
                body=(
                    "Our administrator cannot sign in after the password reset. "
                    "The team cannot access account administration features."
                ),
                received_at=now - timedelta(minutes=30),
                attachments=[],
            ),
            TicketAnalysisResponse(
                customer_name="Rahul Mehta",
                company="Vertex Analytics",
                issue_summary="Administrator account access failure",
                detailed_description=(
                    "The customer reports that the administrator cannot sign "
                    "in after a password reset and account administration "
                    "features are unavailable."
                ),
                category="Account Access",
                priority="High",
                sentiment="Negative",
                product_service="Customer Portal",
                suggested_department="Customer Success",
                suggested_tags=[
                    "account access",
                    "login issue",
                    "administrator",
                ],
                confidence_score=0.95,
            ),
        ),
        (
            ParsedEmail(
                message_id=(
                    f"<{DEMO_MESSAGE_PREFIX}-billing"
                    "@supportiq.local>"
                ),
                sender_name="Priya Sharma",
                sender_email="priya.sharma@example.com",
                subject="Incorrect charge on monthly invoice",
                body=(
                    "Our latest invoice contains an incorrect charge. "
                    "Please review the billing records and explain the "
                    "additional amount."
                ),
                received_at=now - timedelta(minutes=25),
                attachments=[],
            ),
            TicketAnalysisResponse(
                customer_name="Priya Sharma",
                company="BluePeak Consulting",
                issue_summary="Incorrect charge on customer invoice",
                detailed_description=(
                    "The customer reports an unexpected charge on the latest "
                    "invoice and requests review of the billing records."
                ),
                category="Billing",
                priority="Medium",
                sentiment="Negative",
                product_service="Subscription Billing",
                suggested_department="Finance",
                suggested_tags=[
                    "billing",
                    "invoice",
                    "incorrect charge",
                ],
                confidence_score=0.93,
            ),
        ),
        (
            ParsedEmail(
                message_id=(
                    f"<{DEMO_MESSAGE_PREFIX}-feature-request"
                    "@supportiq.local>"
                ),
                sender_name="Arjun Patel",
                sender_email="arjun.patel@example.com",
                subject="Feature request for scheduled report exports",
                body=(
                    "It would be useful to schedule automatic weekly report "
                    "exports. This is not urgent, but it would improve our "
                    "reporting workflow."
                ),
                received_at=now - timedelta(minutes=20),
                attachments=[],
            ),
            TicketAnalysisResponse(
                customer_name="Arjun Patel",
                company="Nimbus Retail",
                issue_summary="Request for scheduled report exports",
                detailed_description=(
                    "The customer requests the ability to schedule automatic "
                    "weekly report exports to improve reporting workflows."
                ),
                category="Feature Request",
                priority="Low",
                sentiment="Positive",
                product_service="Reporting Platform",
                suggested_department="Product Team",
                suggested_tags=[
                    "feature request",
                    "scheduled exports",
                    "reporting",
                ],
                confidence_score=0.91,
            ),
        ),
        (
            ParsedEmail(
                message_id=(
                    f"<{DEMO_MESSAGE_PREFIX}-refund"
                    "@supportiq.local>"
                ),
                sender_name="Neha Kapoor",
                sender_email="neha.kapoor@example.com",
                subject="Refund required for duplicate payment",
                body=(
                    "We were charged twice for the same transaction. "
                    "Please review the duplicate payment and process a refund."
                ),
                received_at=now - timedelta(minutes=15),
                attachments=[],
            ),
            TicketAnalysisResponse(
                customer_name="Neha Kapoor",
                company="Orion Digital",
                issue_summary="Refund request for duplicate payment",
                detailed_description=(
                    "The customer reports being charged twice for one "
                    "transaction and requests a refund of the duplicate payment."
                ),
                category="Refund Request",
                priority="High",
                sentiment="Negative",
                product_service="Payment Processing",
                suggested_department="Finance",
                suggested_tags=[
                    "refund request",
                    "duplicate payment",
                    "payment issue",
                ],
                confidence_score=0.96,
            ),
        ),
        (
            ParsedEmail(
                message_id=(
                    f"<{DEMO_MESSAGE_PREFIX}-sales"
                    "@supportiq.local>"
                ),
                sender_name="Vikram Singh",
                sender_email="vikram.singh@example.com",
                subject="Pricing inquiry for enterprise deployment",
                body=(
                    "We are evaluating the platform for an enterprise rollout. "
                    "Please provide pricing and licensing information for "
                    "approximately 500 users."
                ),
                received_at=now - timedelta(minutes=10),
                attachments=[],
            ),
            TicketAnalysisResponse(
                customer_name="Vikram Singh",
                company="Apex Manufacturing",
                issue_summary="Enterprise pricing and licensing inquiry",
                detailed_description=(
                    "The customer requests pricing and licensing information "
                    "for an enterprise deployment of approximately 500 users."
                ),
                category="Sales Inquiry",
                priority="Medium",
                sentiment="Neutral",
                product_service="Enterprise Platform",
                suggested_department="Sales",
                suggested_tags=[
                    "sales inquiry",
                    "enterprise",
                    "pricing",
                ],
                confidence_score=0.94,
            ),
        ),
        (
            ParsedEmail(
                message_id=(
                    f"<{DEMO_MESSAGE_PREFIX}-general"
                    "@supportiq.local>"
                ),
                sender_name="Kavya Iyer",
                sender_email="kavya.iyer@example.com",
                subject="Question about data export retention",
                body=(
                    "Could you explain how long generated data exports remain "
                    "available for download? We are reviewing our internal "
                    "data-retention process."
                ),
                received_at=now - timedelta(minutes=5),
                attachments=[],
            ),
            TicketAnalysisResponse(
                customer_name="Kavya Iyer",
                company="Cedar Financial",
                issue_summary="Question about data export retention",
                detailed_description=(
                    "The customer requests information about how long generated "
                    "data exports remain available for download."
                ),
                category="General Inquiry",
                priority="Low",
                sentiment="Neutral",
                product_service="Data Export",
                suggested_department="Customer Success",
                suggested_tags=[
                    "general inquiry",
                    "data export",
                    "retention",
                ],
                confidence_score=0.90,
            ),
        ),
    ]


def main():
    session = SessionLocal()

    workflow_service = None

    try:
        demo_cases = build_demo_cases()

        analyses = {
            email.message_id: analysis
            for email, analysis in demo_cases
        }

        llm_service = DeterministicDemoLLMService(analyses)

        ticket_repository = TicketRepository(session)

        ticket_service = TicketService(
            ticket_repository=ticket_repository,
            attachment_repository=AttachmentRepository(session),
            audit_repository=AuditRepository(session),
        )

        workflow_execution_service = WorkflowExecutionService(
            WorkflowExecutionRepository(session),
            session=session,
        )

        workflow_service = WorkflowService(
            session=session,
            llm_service=llm_service,
            ticket_analysis_normalizer=TicketAnalysisNormalizer(),
            priority_service=PriorityService(),
            routing_service=RoutingService(),
            reply_suggestion_service=ReplySuggestionService(
                llm_service
            ),
            ticket_service=ticket_service,
            workflow_execution_service=workflow_execution_service,
        )

        created = 0
        skipped = 0

        print()
        print("SupportIQ Demo Ticket Seeder")
        print("=" * 60)

        for email, _analysis in demo_cases:
            existing_execution = (
                workflow_execution_service.get_by_message_id(
                    email.message_id
                )
            )

            if existing_execution is not None:
                print(
                    f"SKIP    {email.message_id} "
                    "(already processed)"
                )
                skipped += 1
                continue

            result = workflow_service.process_email(email)

            persisted_ticket = ticket_repository.get_by_id(
                result.ticket_id
            )

            if persisted_ticket is None:
                raise RuntimeError(
                    "Workflow returned a ticket ID that was not persisted."
                )

            print(
                f"CREATED {result.ticket_number} | "
                f"{result.analysis.category} | "
                f"{result.priority_decision.final_priority} | "
                f"{result.routing_decision.assigned_team}"
            )

            created += 1

        total_tickets = ticket_repository.count_tickets()

        print("=" * 60)
        print(f"Created this run : {created}")
        print(f"Skipped existing : {skipped}")
        print(f"Total DB tickets : {total_tickets}")
        print()
        print(
            "Refresh http://127.0.0.1:8000/dashboard/tickets "
            "to view the demo tickets."
        )

    except Exception:
        session.rollback()
        raise

    finally:
        if workflow_service is not None:
            workflow_service.close()

        session.close()


if __name__ == "__main__":
    main()
