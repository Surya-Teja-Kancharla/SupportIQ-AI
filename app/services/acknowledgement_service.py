from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config.acknowledgement_rules import (
    get_estimated_response_time,
)
from app.core.constants import AuditAction
from app.repositories.audit_repository import AuditRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.acknowledgement_schema import AcknowledgementResult
from app.schemas.smtp_schema import OutboundEmail
from app.services.smtp_service import SMTPService


class AcknowledgementService:

    def __init__(
        self,
        ticket_repository: TicketRepository | None = None,
        audit_repository: AuditRepository | None = None,
        smtp_service: SMTPService | None = None,
    ) -> None:
        self.ticket_repository = (
            ticket_repository or TicketRepository()
        )
        self.audit_repository = (
            audit_repository or AuditRepository()
        )
        self.smtp_service = smtp_service or SMTPService()

    @staticmethod
    def _build_subject(ticket_number: str) -> str:
        return (
            f"Support request received - "
            f"{ticket_number}"
        )

    @staticmethod
    def _build_body(
        *,
        ticket_number: str,
        issue_summary: str,
        status: str,
        estimated_response_time: str,
    ) -> str:
        return (
            "Hello,\n\n"
            "We have received your support request.\n\n"
            f"Ticket ID: {ticket_number}\n"
            f"Issue Summary: {issue_summary}\n"
            f"Status: {status}\n"
            f"Estimated Response Time: "
            f"{estimated_response_time}\n\n"
            "Our support team will review your request "
            "and follow up as soon as possible.\n\n"
            "Regards,\n"
            "SupportIQ Support Team"
        )

    def send_acknowledgement(
        self,
        db: Session,
        *,
        ticket_id: int,
    ) -> AcknowledgementResult:
        ticket = self.ticket_repository.get_by_id(
            db,
            ticket_id,
        )

        if ticket is None:
            raise ValueError(
                f"Ticket {ticket_id} not found"
            )

        # Idempotency guard:
        # an acknowledgement already persisted must
        # never be delivered or audited a second time.
        if ticket.acknowledgement_sent_at is not None:
            return AcknowledgementResult(
                ticket_id=ticket.id,
                sent=False,
                already_sent=True,
            )

        estimated_response_time = (
            get_estimated_response_time(ticket.priority)
        )

        subject = self._build_subject(
            ticket.ticket_number,
        )

        body = self._build_body(
            ticket_number=ticket.ticket_number,
            issue_summary=(
                ticket.summary
                or ticket.subject
                or "Support request received"
            ),
            status=ticket.status or "OPEN",
            estimated_response_time=(
                estimated_response_time
            ),
        )

        outbound_email = OutboundEmail(
            recipient_email=ticket.sender_email,
            subject=subject,
            plain_text_body=body,
        )

        # SMTP delivery occurs before persistence.
        #
        # If SMTPService raises an exception, the
        # timestamp, audit event, and commit are skipped.
        delivery_result = self.smtp_service.send_email(
            outbound_email
        )

        # Defensive check because SMTPService currently
        # returns EmailDeliveryResult(success=True) on
        # success, but the service contract exposes a
        # success field.
        if not delivery_result.success:
            raise RuntimeError(
                delivery_result.error_message
                or "Acknowledgement email delivery failed"
            )

        try:
            sent_at = datetime.now(timezone.utc)

            ticket.acknowledgement_sent_at = sent_at

            self.audit_repository.create(
                db,
                ticket_id=ticket.id,
                action=AuditAction.ACKNOWLEDGEMENT_SENT,
                old_value=None,
                new_value=ticket.sender_email,
                performed_by="system",
            )

            db.commit()
            db.refresh(ticket)

            return AcknowledgementResult(
                ticket_id=ticket.id,
                sent=True,
                already_sent=False,
            )

        except Exception:
            db.rollback()
            raise
