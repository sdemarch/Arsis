--liquibase formatted sql

--changeset arsis:0012-milestone-achievements
--comment Log of each time a person reaches a milestone, closed by a reset or revoked when progress drops.

CREATE TABLE milestone_achievements (
    id INTEGER PRIMARY KEY,
    milestone_id INTEGER NOT NULL REFERENCES milestones(id) ON DELETE RESTRICT,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    reached_at TEXT NOT NULL,
    progress NUMERIC NOT NULL CHECK (progress >= 0),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'reset', 'revoked')),
    reset_id INTEGER REFERENCES milestone_resets(id) ON DELETE RESTRICT,
    closed_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    CHECK ((status = 'open') = (closed_at IS NULL)),
    CHECK (reset_id IS NULL OR status = 'reset')
);

CREATE INDEX ix_milestone_achievements_milestone_person
    ON milestone_achievements (milestone_id, person_id, status);
CREATE INDEX ix_milestone_achievements_reached ON milestone_achievements (reached_at);

--rollback DROP INDEX ix_milestone_achievements_reached;
--rollback DROP INDEX ix_milestone_achievements_milestone_person;
--rollback DROP TABLE milestone_achievements;
