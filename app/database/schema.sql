CREATE TABLE tickets (
    id BIGSERIAL PRIMARY KEY,

    ticket_number VARCHAR(30) UNIQUE NOT NULL,

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

    confidence_score NUMERIC(5,2),

    status VARCHAR(30) DEFAULT 'OPEN',

    received_at TIMESTAMP NOT NULL,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attachments (

    id BIGSERIAL PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    file_name VARCHAR(255),

    file_path TEXT,

    file_type VARCHAR(100),

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ticket_attachment
        FOREIGN KEY(ticket_id)
        REFERENCES tickets(id)
        ON DELETE CASCADE
);

CREATE TABLE tags (

    id BIGSERIAL PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    tag_name VARCHAR(100) NOT NULL,

    CONSTRAINT fk_ticket_tag
        FOREIGN KEY(ticket_id)
        REFERENCES tickets(id)
        ON DELETE CASCADE
);

CREATE TABLE audit_logs (

    id BIGSERIAL PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    action VARCHAR(255) NOT NULL,

    old_value TEXT,

    new_value TEXT,

    performed_by VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ticket_audit
        FOREIGN KEY(ticket_id)
        REFERENCES tickets(id)
        ON DELETE CASCADE
);

CREATE TABLE internal_notes (

    id BIGSERIAL PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    note TEXT NOT NULL,

    created_by VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ticket_note
        FOREIGN KEY(ticket_id)
        REFERENCES tickets(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_ticket_status ON tickets(status);

CREATE INDEX idx_ticket_priority ON tickets(priority);

CREATE INDEX idx_ticket_category ON tickets(category);

CREATE INDEX idx_ticket_email ON tickets(sender_email);

CREATE INDEX idx_ticket_received ON tickets(received_at);