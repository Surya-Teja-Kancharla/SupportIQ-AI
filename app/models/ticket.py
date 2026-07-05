from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    Numeric,
    String,
    Text,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.ticket_attachment import TicketAttachment
    from app.models.ticket_audit_log import TicketAuditLog


class Ticket(Base):
    __tablename__ = "tickets"

    __table_args__ = (
        Index("idx_ticket_category", "category"),
        Index("idx_ticket_email", "sender_email"),
        Index("idx_ticket_priority", "priority"),
        Index("idx_ticket_received", "received_at"),
        Index("idx_ticket_status", "status"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    ticket_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    customer_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    sender_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    sentiment: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    product: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    suggested_department: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    assigned_team: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        server_default="OPEN",
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    attachments: Mapped[list["TicketAttachment"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    audit_logs: Mapped[list["TicketAuditLog"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    priority_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    suggested_reply: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
