--liquibase formatted sql

--changeset arsis:0001-initial-schema
--comment Initial SQLite technical tables; domain tables will be added per feature.

CREATE TABLE app_settings (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL DEFAULT '{}',
    description TEXT,
    version integer NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_events (
    id INTEGER PRIMARY KEY,
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    request_id TEXT,
    details TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX ix_audit_events_entity ON audit_events (entity_type, entity_id, occurred_at DESC);

--rollback DROP TABLE audit_events; DROP TABLE app_settings;
