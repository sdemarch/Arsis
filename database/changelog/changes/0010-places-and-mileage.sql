--liquibase formatted sql

--changeset arsis:0010-places-and-mileage
--comment Places with round-trip km and highway toll, drivers on attendance, mileage rules and reimbursement snapshots.

CREATE TABLE places (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    address TEXT,
    distance_km INTEGER NOT NULL DEFAULT 0 CHECK (distance_km >= 0),
    highway_cost NUMERIC NOT NULL DEFAULT 0 CHECK (highway_cost >= 0),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE UNIQUE INDEX ux_places_name_active ON places (lower(name)) WHERE archived_at IS NULL;

ALTER TABLE activities ADD COLUMN place_id INTEGER REFERENCES places(id) ON DELETE RESTRICT;

CREATE INDEX ix_activities_place ON activities (place_id);

ALTER TABLE activity_participants ADD COLUMN is_driver INTEGER NOT NULL DEFAULT 0
    CHECK (is_driver IN (0, 1));
ALTER TABLE activity_participants ADD COLUMN passenger_count INTEGER
    CHECK (passenger_count IS NULL OR passenger_count >= 0);
ALTER TABLE activity_participants ADD COLUMN refund_flat_amount NUMERIC
    CHECK (refund_flat_amount IS NULL OR refund_flat_amount >= 0);
ALTER TABLE activity_participants ADD COLUMN refund_distance_km INTEGER
    CHECK (refund_distance_km IS NULL OR refund_distance_km >= 0);
ALTER TABLE activity_participants ADD COLUMN refund_rate_per_km NUMERIC
    CHECK (refund_rate_per_km IS NULL OR refund_rate_per_km >= 0);
ALTER TABLE activity_participants ADD COLUMN refund_bonus_pct INTEGER
    CHECK (refund_bonus_pct IS NULL OR refund_bonus_pct >= 0);
ALTER TABLE activity_participants ADD COLUMN refund_mileage_amount NUMERIC
    CHECK (refund_mileage_amount IS NULL OR refund_mileage_amount >= 0);
ALTER TABLE activity_participants ADD COLUMN refund_highway_amount NUMERIC
    CHECK (refund_highway_amount IS NULL OR refund_highway_amount >= 0);

UPDATE app_settings
SET value = json_set(
        value,
        '$.mileage',
        json('{"enabled_types":["event"],"rate_per_km":"0.00","passenger_bonus_pct":0,"max_bonus_passengers":4}')
    ),
    description = 'Rimborsi per presenza registrata: importo fisso per tipo di attività e rimborso chilometrico per gli autisti'
WHERE key = 'activities.refund_rules';

-- Attendance already recorded keeps the flat amount in force today; later rule changes
-- apply only to attendance recorded afterwards.
UPDATE activity_participants
SET refund_flat_amount = (
    SELECT printf(
        '%.2f',
        CAST(json_extract(s.value, '$.' || a.type) AS REAL)
    )
    FROM activities a, app_settings s
    WHERE a.id = activity_participants.activity_id AND s.key = 'activities.refund_rules'
)
WHERE attendance = 'present';

--rollback UPDATE app_settings SET value = json_remove(value, '$.mileage'), description = 'Importo del rimborso per presenza registrata, per tipo di attività' WHERE key = 'activities.refund_rules';
--rollback ALTER TABLE activity_participants DROP COLUMN refund_highway_amount;
--rollback ALTER TABLE activity_participants DROP COLUMN refund_mileage_amount;
--rollback ALTER TABLE activity_participants DROP COLUMN refund_bonus_pct;
--rollback ALTER TABLE activity_participants DROP COLUMN refund_rate_per_km;
--rollback ALTER TABLE activity_participants DROP COLUMN refund_distance_km;
--rollback ALTER TABLE activity_participants DROP COLUMN refund_flat_amount;
--rollback ALTER TABLE activity_participants DROP COLUMN passenger_count;
--rollback ALTER TABLE activity_participants DROP COLUMN is_driver;
--rollback DROP INDEX ix_activities_place;
--rollback ALTER TABLE activities DROP COLUMN place_id;
--rollback DROP TABLE places;
