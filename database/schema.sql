-- ============================================================
-- SupportIQ AI
-- PostgreSQL Database Schema
-- Hour 17 Documentation and Deliverables
--
-- Purpose:
--   Reference SQL schema representing the current SupportIQ AI
--   persistence model.
--
-- Notes:
--   1. Alembic remains the authoritative mechanism for applying
--      schema changes to deployed databases.
--   2. This file is a documentation and deliverable artifact.
--   3. The schema reflects the current SQLAlchemy model layer.
-- ============================================================


-- ============================================================
-- TICKETS
-- ============================================================

CREATE TABLE tickets (
    id BIGSERIAL PRIMARY KEY,

    ticket_number VARCHAR(30) NOT NULL UNIQUE,

    customer_name VARCHAR(255),

    company VARCHAR(255),

    sender_email VARCHAR(255) NOT NULL,

    subject TEXT NOT NULL,

    body TEXT NOT NULL,

    summary TEXT,

    description TEXT,

    category VARCHAR(100),

    priority VARCHAR(20),

    sentiment VARCHAR(20),

    product VARCHAR(255),

    suggested_department VARCHAR(100),

    assigned_team VARCHAR(100),

    confidence_score NUMERIC(5, 2),

    status VARCHAR(30) DEFAULT 'OPEN',

    received_at TIMESTAMP NOT NULL,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    priority_reason TEXT,

    suggested_reply TEXT,

    acknowledgement_sent_at TIMESTAMPTZ
);


-- ============================================================
-- TICKET ATTACHMENTS
-- ============================================================

CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    file_name VARCHAR(255),

    file_path TEXT,

    file_type VARCHAR(100),

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ticket_attachment
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON DELETE CASCADE
);


-- ============================================================
-- TICKET AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    action VARCHAR(255) NOT NULL,

    old_value TEXT,

    new_value TEXT,

    performed_by VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ticket_audit
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON DELETE CASCADE
);


-- ============================================================
-- INTERNAL NOTES
-- ============================================================

CREATE TABLE internal_notes (
    id BIGSERIAL PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    note TEXT NOT NULL,

    created_by VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_internal_note_ticket
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON DELETE CASCADE
);


-- ============================================================
-- WORKFLOW EXECUTIONS
-- ============================================================

CREATE TABLE workflow_executions (
    id BIGSERIAL PRIMARY KEY,

    execution_id VARCHAR(36) NOT NULL,

    message_id VARCHAR(500) NOT NULL,

    ticket_id BIGINT,

    started_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    duration_ms BIGINT,

    status VARCHAR(50) NOT NULL,

    current_stage VARCHAR(100) NOT NULL,

    retry_count INTEGER NOT NULL DEFAULT 0,

    failure_stage VARCHAR(100),

    error_type VARCHAR(255),

    error_message TEXT,

    retry_exhausted BOOLEAN NOT NULL DEFAULT FALSE,

    failed_at TIMESTAMPTZ,

    parent_execution_id BIGINT,

    attempt_number INTEGER NOT NULL DEFAULT 1,

    execution_metadata JSON,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_workflow_execution_ticket
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_workflow_execution_parent
        FOREIGN KEY (parent_execution_id)
        REFERENCES workflow_executions(id)
        ON DELETE SET NULL
);


-- ============================================================
-- DEAD LETTER RECORDS
-- ============================================================

CREATE TABLE dead_letter_records (
    id SERIAL PRIMARY KEY,

    workflow_execution_id BIGINT NOT NULL UNIQUE,

    ticket_id BIGINT,

    failed_stage VARCHAR(100) NOT NULL,

    exception_type VARCHAR(255) NOT NULL,

    sanitized_error_message TEXT NOT NULL,

    retry_count INTEGER NOT NULL DEFAULT 0,

    retry_exhausted BOOLEAN NOT NULL DEFAULT FALSE,

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',

    manual_retry_count INTEGER NOT NULL DEFAULT 0,

    last_retry_execution_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_dead_letter_workflow_execution
        FOREIGN KEY (workflow_execution_id)
        REFERENCES workflow_executions(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_dead_letter_ticket
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_dead_letter_last_retry_execution
        FOREIGN KEY (last_retry_execution_id)
        REFERENCES workflow_executions(id)
        ON DELETE SET NULL
);


-- ============================================================
-- TICKET INDEXES
-- ============================================================

CREATE INDEX idx_ticket_status
    ON tickets(status);

CREATE INDEX idx_ticket_priority
    ON tickets(priority);

CREATE INDEX idx_ticket_category
    ON tickets(category);

CREATE INDEX idx_ticket_email
    ON tickets(sender_email);

CREATE INDEX idx_ticket_received
    ON tickets(received_at);


-- ============================================================
-- INTERNAL NOTE INDEXES
-- ============================================================

CREATE INDEX ix_internal_notes_ticket_id
    ON internal_notes(ticket_id);


-- ============================================================
-- WORKFLOW EXECUTION INDEXES
-- ============================================================

CREATE UNIQUE INDEX ix_workflow_executions_execution_id
    ON workflow_executions(execution_id);

CREATE INDEX ix_workflow_executions_message_id
    ON workflow_executions(message_id);

CREATE INDEX ix_workflow_executions_status
    ON workflow_executions(status);

CREATE INDEX ix_workflow_executions_started_at
    ON workflow_executions(started_at);


-- ============================================================
-- DEAD LETTER RECORD INDEXES
-- ============================================================

CREATE INDEX ix_dead_letter_records_ticket_id
    ON dead_letter_records(ticket_id);

CREATE INDEX ix_dead_letter_records_status
    ON dead_letter_records(status);

-- PostgreSQL automatically creates a unique index for the
-- UNIQUE constraint on workflow_execution_id.


-- ============================================================
-- RELATIONSHIP SUMMARY
-- ============================================================

-- tickets
--   |
--   +----< attachments
--   |
--   +----< audit_logs
--   |
--   +----< internal_notes
--   |
--   +----< workflow_executions
--   |          |
--   |          +----< workflow_executions
--   |          |       (retry lineage through parent_execution_id)
--   |          |
--   |          +---- dead_letter_records
--   |
--   +----< dead_letter_records
--
-- Delete behavior:
--
-- tickets -> attachments
--     ON DELETE CASCADE
--
-- tickets -> audit_logs
--     ON DELETE CASCADE
--
-- tickets -> internal_notes
--     ON DELETE CASCADE
--
-- tickets -> workflow_executions
--     ON DELETE SET NULL
--
-- workflow_executions -> retry child executions
--     ON DELETE SET NULL
--
-- workflow_executions -> dead_letter_records
--     ON DELETE CASCADE
--
-- tickets -> dead_letter_records
--     ON DELETE SET NULL
--
-- workflow_executions -> dead_letter_records.last_retry_execution_id
--     ON DELETE SET NULL


-- ============================================================
-- END OF SUPPORTIQ AI REFERENCE SCHEMA
-- ============================================================