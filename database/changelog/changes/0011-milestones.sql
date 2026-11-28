--liquibase formatted sql

--changeset arsis:0011-milestones
--comment Configurable milestones on attendance and reimbursements, with a ledger of per-person resets.

CREATE TABLE milestones (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    metric TEXT NOT NULL CHECK (
        metric IN (
            'rehearsal_count', 'concert_count', 'event_count',
            'attendance_count', 'reimbursement_total'
        )
    ),
    threshold NUMERIC NOT NULL CHECK (threshold > 0),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE UNIQUE INDEX ux_milestones_name_active ON milestones (lower(name))
    WHERE archived_at IS NULL;

-- Each reset consumes one threshold from a person's progress; the excess carries over.
CREATE TABLE milestone_resets (
    id INTEGER PRIMARY KEY,
    milestone_id INTEGER NOT NULL REFERENCES milestones(id) ON DELETE RESTRICT,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    consumed NUMERIC NOT NULL CHECK (consumed > 0),
    progress_before NUMERIC NOT NULL CHECK (progress_before >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX ix_milestone_resets_milestone_person
    ON milestone_resets (milestone_id, person_id, archived_at);

--rollback DROP INDEX ix_milestone_resets_milestone_person;
--rollback DROP TABLE milestone_resets;
--rollback DROP INDEX ux_milestones_name_active;
--rollback DROP TABLE milestones;
