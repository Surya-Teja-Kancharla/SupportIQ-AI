from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.ticket import Ticket


class TicketAttachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    ticket_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "tickets.id",
            name="fk_ticket_attachment",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    uploaded_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    ticket: Mapped["Ticket"] = relationship(
        back_populates="attachments",
    )
