# Database Schema

## Overview

SupportIQ-AI uses a relational database to persist users, support tickets, ticket messages, AI-generated classifications, reply suggestions, audit events, and background job execution records.

The schema is designed around the following principles:

* Clear separation between authentication, ticketing, AI, auditing, and job-processing data.
* Referential integrity through foreign keys.
* Database-level constraints for important invariants.
* Indexes for frequently queried columns.
* UTC timestamps for consistent time handling.
* Compatibility with SQLAlchemy ORM models and Alembic migrations.
* Support for PostgreSQL in production environments.

---

## Entity Relationship Overview

```text
users
  |
  | 1
  |
  | N
tickets
  |
  +----------------------+
  |                      |
  | 1                    | 1
  |                      |
  | N                    | N
ticket_messages     ticket_classifications
  |
  | 1
  |
  | N
reply_suggestions


users
  |
  | 1
  |
  | N
audit_logs


background_jobs
```

---

## Tables

### 1. `users`

Stores authenticated SupportIQ-AI users.

| Column          | Type                     | Constraints      | Description                    |
| --------------- | ------------------------ | ---------------- | ------------------------------ |
| `id`            | BIGINT                   | PRIMARY KEY      | Unique user identifier         |
| `email`         | VARCHAR(255)             | UNIQUE, NOT NULL | User email address             |
| `password_hash` | VARCHAR(255)             | NOT NULL         | Secure password hash           |
| `full_name`     | VARCHAR(255)             | NULL             | User display name              |
| `role`          | VARCHAR(50)              | NOT NULL         | Authorization role             |
| `is_active`     | BOOLEAN                  | NOT NULL         | Whether the account is enabled |
| `created_at`    | TIMESTAMP WITH TIME ZONE | NOT NULL         | Creation timestamp             |
| `updated_at`    | TIMESTAMP WITH TIME ZONE | NOT NULL         | Last update timestamp          |

Recommended roles:

```text
admin
agent
viewer
```

---

### 2. `tickets`

Stores customer support tickets.

| Column             | Type                     | Constraints       | Description                         |
| ------------------ | ------------------------ | ----------------- | ----------------------------------- |
| `id`               | BIGINT                   | PRIMARY KEY       | Internal ticket identifier          |
| `external_id`      | VARCHAR(255)             | UNIQUE, NULL      | External provider ticket identifier |
| `subject`          | VARCHAR(500)             | NOT NULL          | Ticket subject                      |
| `customer_email`   | VARCHAR(255)             | NOT NULL          | Customer email                      |
| `status`           | VARCHAR(50)              | NOT NULL          | Ticket lifecycle status             |
| `priority`         | VARCHAR(50)              | NOT NULL          | Ticket priority                     |
| `assigned_user_id` | BIGINT                   | FOREIGN KEY, NULL | Assigned support agent              |
| `source`           | VARCHAR(50)              | NOT NULL          | Ticket ingestion source             |
| `created_at`       | TIMESTAMP WITH TIME ZONE | NOT NULL          | Ticket creation timestamp           |
| `updated_at`       | TIMESTAMP WITH TIME ZONE | NOT NULL          | Last ticket update                  |

Recommended ticket statuses:

```text
open
in_progress
resolved
closed
```

Recommended priorities:

```text
low
medium
high
urgent
```

---

### 3. `ticket_messages`

Stores individual customer and support-agent messages associated with tickets.

| Column                | Type                     | Constraints           | Description                          |
| --------------------- | ------------------------ | --------------------- | ------------------------------------ |
| `id`                  | BIGINT                   | PRIMARY KEY           | Message identifier                   |
| `ticket_id`           | BIGINT                   | FOREIGN KEY, NOT NULL | Parent ticket                        |
| `sender_email`        | VARCHAR(255)             | NOT NULL              | Message sender                       |
| `message_body`        | TEXT                     | NOT NULL              | Message content                      |
| `message_type`        | VARCHAR(50)              | NOT NULL              | Customer or agent message            |
| `external_message_id` | VARCHAR(255)             | UNIQUE, NULL          | External provider message identifier |
| `received_at`         | TIMESTAMP WITH TIME ZONE | NOT NULL              | Message reception timestamp          |
| `created_at`          | TIMESTAMP WITH TIME ZONE | NOT NULL              | Database creation timestamp          |

Recommended message types:

```text
customer
agent
system
```

---

### 4. `ticket_classifications`

Stores AI-generated ticket classifications.

| Column             | Type                     | Constraints           | Description                  |
| ------------------ | ------------------------ | --------------------- | ---------------------------- |
| `id`               | BIGINT                   | PRIMARY KEY           | Classification identifier    |
| `ticket_id`        | BIGINT                   | FOREIGN KEY, NOT NULL | Classified ticket            |
| `category`         | VARCHAR(100)             | NOT NULL              | Predicted ticket category    |
| `priority`         | VARCHAR(50)              | NOT NULL              | Predicted priority           |
| `sentiment`        | VARCHAR(50)              | NULL                  | Predicted customer sentiment |
| `confidence_score` | NUMERIC(5,4)             | NULL                  | Classification confidence    |
| `model_name`       | VARCHAR(255)             | NULL                  | AI model identifier          |
| `created_at`       | TIMESTAMP WITH TIME ZONE | NOT NULL              | Classification timestamp     |

Multiple classification records may exist for the same ticket to preserve classification history.

---

### 5. `reply_suggestions`

Stores AI-generated support reply suggestions.

| Column            | Type                     | Constraints           | Description                          |
| ----------------- | ------------------------ | --------------------- | ------------------------------------ |
| `id`              | BIGINT                   | PRIMARY KEY           | Suggestion identifier                |
| `ticket_id`       | BIGINT                   | FOREIGN KEY, NOT NULL | Parent ticket                        |
| `message_id`      | BIGINT                   | FOREIGN KEY, NULL     | Message used to generate suggestion  |
| `suggested_reply` | TEXT                     | NOT NULL              | AI-generated reply                   |
| `model_name`      | VARCHAR(255)             | NULL                  | AI model identifier                  |
| `was_used`        | BOOLEAN                  | NOT NULL              | Whether an agent used the suggestion |
| `created_at`      | TIMESTAMP WITH TIME ZONE | NOT NULL              | Suggestion generation timestamp      |

---

### 6. `audit_logs`

Stores security-sensitive and operational audit events.

| Column          | Type                     | Constraints       | Description                          |
| --------------- | ------------------------ | ----------------- | ------------------------------------ |
| `id`            | BIGINT                   | PRIMARY KEY       | Audit event identifier               |
| `user_id`       | BIGINT                   | FOREIGN KEY, NULL | User responsible for the event       |
| `event_type`    | VARCHAR(100)             | NOT NULL          | Audit event category                 |
| `resource_type` | VARCHAR(100)             | NULL              | Affected resource type               |
| `resource_id`   | VARCHAR(255)             | NULL              | Affected resource identifier         |
| `ip_address`    | VARCHAR(45)              | NULL              | Request source IP                    |
| `details`       | JSON                     | NULL              | Additional structured event metadata |
| `created_at`    | TIMESTAMP WITH TIME ZONE | NOT NULL          | Event timestamp                      |

Audit logs should be treated as append-only records.

---

### 7. `background_jobs`

Stores background job execution metadata.

| Column          | Type                     | Constraints | Description                    |
| --------------- | ------------------------ | ----------- | ------------------------------ |
| `id`            | BIGINT                   | PRIMARY KEY | Job identifier                 |
| `job_type`      | VARCHAR(100)             | NOT NULL    | Background job category        |
| `status`        | VARCHAR(50)              | NOT NULL    | Current execution state        |
| `payload`       | JSON                     | NULL        | Job input metadata             |
| `result`        | JSON                     | NULL        | Job execution result           |
| `error_message` | TEXT                     | NULL        | Failure information            |
| `retry_count`   | INTEGER                  | NOT NULL    | Number of retry attempts       |
| `started_at`    | TIMESTAMP WITH TIME ZONE | NULL        | Execution start timestamp      |
| `completed_at`  | TIMESTAMP WITH TIME ZONE | NULL        | Execution completion timestamp |
| `created_at`    | TIMESTAMP WITH TIME ZONE | NOT NULL    | Job creation timestamp         |
| `updated_at`    | TIMESTAMP WITH TIME ZONE | NOT NULL    | Last job update timestamp      |

Recommended job statuses:

```text
pending
running
completed
failed
retrying
```

---

## Foreign-Key Relationships

```text
tickets.assigned_user_id
    -> users.id

ticket_messages.ticket_id
    -> tickets.id

ticket_classifications.ticket_id
    -> tickets.id

reply_suggestions.ticket_id
    -> tickets.id

reply_suggestions.message_id
    -> ticket_messages.id

audit_logs.user_id
    -> users.id
```

---

## Indexing Strategy

Indexes should be created for frequently filtered, sorted, and joined columns.

Recommended indexes include:

```text
users.email

tickets.external_id
tickets.status
tickets.priority
tickets.assigned_user_id
tickets.created_at

ticket_messages.ticket_id
ticket_messages.received_at

ticket_classifications.ticket_id
ticket_classifications.category
ticket_classifications.created_at

reply_suggestions.ticket_id
reply_suggestions.created_at

audit_logs.user_id
audit_logs.event_type
audit_logs.created_at

background_jobs.status
background_jobs.job_type
background_jobs.created_at
```

Composite indexes may be introduced after profiling production query patterns.

Examples:

```text
tickets(status, created_at)

tickets(priority, created_at)

audit_logs(event_type, created_at)

background_jobs(status, created_at)
```

---

## Timestamp Policy

All timestamps must be stored in UTC.

Application code should use timezone-aware datetime values.

Example:

```python
datetime.now(timezone.utc)
```

Timezone conversion should occur only when presenting data to users.

---

## Deletion Policy

The schema should avoid unnecessary cascading deletes for security-sensitive and historical records.

Recommended behavior:

```text
Deleting a user:
    tickets.assigned_user_id -> SET NULL
    audit_logs.user_id       -> SET NULL

Deleting a ticket:
    ticket_messages          -> CASCADE
    ticket_classifications   -> CASCADE
    reply_suggestions        -> CASCADE
```

Audit logs should not be automatically deleted.

---

## Migration Policy

All database schema changes must be managed through Alembic migrations.

Developers should not manually modify production database schemas.

Typical migration workflow:

```bash
alembic revision --autogenerate -m "describe schema change"

alembic upgrade head
```

Before deployment:

```bash
alembic current

alembic heads

alembic check
```

---

## Schema Validation Checklist

Before considering a database migration complete:

* SQLAlchemy models reflect the intended schema.
* Alembic migration generation succeeds.
* Migration upgrade succeeds.
* Migration downgrade succeeds when supported.
* Foreign keys enforce valid relationships.
* Unique constraints prevent duplicate external identifiers.
* Required columns reject null values.
* Indexes exist for common query paths.
* UTC-aware timestamps are used.
* Database tests pass.
