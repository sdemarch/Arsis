--liquibase formatted sql

--changeset arsis:0014-activity-series
--comment Recurring activities: a series holds the rule, each occurrence is an ordinary activity.

-- weekdays: ISO numbers (1 = Monday ... 7 = Sunday), comma separated and ascending,
-- used by weekly series only. Monthly series repeat on the day of month of starts_on.
CREATE TABLE activity_series (
    id INTEGER PRIMARY KEY,
    frequency TEXT NOT NULL CHECK (frequency IN ('weekly', 'monthly')),
    interval_count INTEGER NOT NULL DEFAULT 1 CHECK (interval_count BETWEEN 1 AND 12),
    weekdays TEXT CHECK (weekdays IS NULL OR weekdays GLOB '[1-7]*'),
    starts_on TEXT NOT NULL,
    ends_on TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (ends_on >= starts_on),
    CHECK ((frequency = 'weekly') = (weekdays IS NOT NULL))
);

ALTER TABLE activities ADD COLUMN series_id INTEGER
    REFERENCES activity_series(id) ON DELETE RESTRICT;

CREATE INDEX ix_activities_series ON activities (series_id, starts_at);

--rollback DROP INDEX ix_activities_series;
--rollback ALTER TABLE activities DROP COLUMN series_id;
--rollback DROP TABLE activity_series;
