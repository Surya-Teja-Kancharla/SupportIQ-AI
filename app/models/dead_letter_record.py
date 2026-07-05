from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DeadLetterRecord(Base):
    __tablename__ = "dead_letter_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    workflow_execution_id: Mapped[int] = mapped_column(
        ForeignKey(
            "workflow_executions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    ticket_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "tickets.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    failed_stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    exception_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sanitized_error_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    retry_exhausted: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="OPEN",
        index=True,
    )

    manual_retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_retry_execution_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "workflow_executions.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
