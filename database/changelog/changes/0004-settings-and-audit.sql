--liquibase formatted sql

--changeset arsis:0004-settings-and-audit
--comment Complete settings metadata and normalize audit events against application users.

ALTER TABLE app_settings
    ADD COLUMN created_by TEXT REFERENCES users(id) ON DELETE RESTRICT;
ALTER TABLE app_settings
    ADD COLUMN updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT;
ALTER TABLE app_settings
    ADD COLUMN archived_at TEXT;
ALTER TABLE app_settings
    ADD COLUMN archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT;

INSERT INTO app_settings (key, value, description)
VALUES
    ('archive.google_drive_url', '""', 'URL della cartella principale Google Drive'),
    ('ui.default_theme', '"light"', 'Tema predefinito dell’interfaccia');

DROP INDEX ix_audit_events_entity;
ALTER TABLE audit_events RENAME TO audit_events_legacy;

CREATE TABLE audit_events (
    id TEXT PRIMARY KEY NOT NULL,
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT REFERENCES users(id) ON DELETE RESTRICT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    request_id TEXT,
    details TEXT NOT NULL DEFAULT '{}',
    ip_address TEXT
);

INSERT INTO audit_events (
    id,
    occurred_at,
    user_id,
    action,
    entity_type,
    entity_id,
    request_id,
    details
)
SELECT
    id,
    occurred_at,
    actor_id,
    action,
    entity_type,
    entity_id,
    request_id,
    details
FROM audit_events_legacy;

DROP TABLE audit_events_legacy;

CREATE INDEX ix_audit_events_entity
    ON audit_events (entity_type, entity_id, occurred_at DESC);
CREATE INDEX ix_audit_events_user
    ON audit_events (user_id, occurred_at DESC);
CREATE INDEX ix_audit_events_request
    ON audit_events (request_id) WHERE request_id IS NOT NULL;

--rollback DROP INDEX ix_audit_events_request;
--rollback DROP INDEX ix_audit_events_user;
--rollback DROP INDEX ix_audit_events_entity;
--rollback ALTER TABLE audit_events RENAME TO audit_events_v2;
--rollback CREATE TABLE audit_events (id TEXT PRIMARY KEY NOT NULL, occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, actor_id TEXT, action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT, request_id TEXT, details TEXT NOT NULL DEFAULT '{}');
--rollback INSERT INTO audit_events (id, occurred_at, actor_id, action, entity_type, entity_id, request_id, details) SELECT id, occurred_at, user_id, action, entity_type, entity_id, request_id, details FROM audit_events_v2;
--rollback DROP TABLE audit_events_v2;
--rollback CREATE INDEX ix_audit_events_entity ON audit_events (entity_type, entity_id, occurred_at DESC);
--rollback DELETE FROM app_settings WHERE key IN ('archive.google_drive_url', 'ui.default_theme');
--rollback ALTER TABLE app_settings DROP COLUMN archived_by;
--rollback ALTER TABLE app_settings DROP COLUMN archived_at;
--rollback ALTER TABLE app_settings DROP COLUMN updated_by;
--rollback ALTER TABLE app_settings DROP COLUMN created_by;

