from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    __table_args__ = (
        Index(
            "ix_workflow_executions_execution_id",
            "execution_id",
            unique=True,
        ),
        Index(
            "ix_workflow_executions_status",
            "status",
        ),
        Index(
            "ix_workflow_executions_started_at",
            "started_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    execution_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )

    message_id: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    ticket_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "tickets.id",
            name="fk_workflow_execution_ticket",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_ms: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    current_stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    failure_stage: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    error_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    execution_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
