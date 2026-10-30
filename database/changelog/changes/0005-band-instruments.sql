--liquibase formatted sql

--changeset arsis:0005-band-instruments
--comment Canonical band instrument catalogue. A musician's sections are inferred from assigned instruments.

DROP TABLE IF EXISTS musician_sections;
DROP TABLE IF EXISTS musician_instruments;
DROP TABLE IF EXISTS instruments;

CREATE TABLE instruments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    section_id INTEGER NOT NULL REFERENCES sections(id) ON DELETE RESTRICT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    display_order INTEGER NOT NULL DEFAULT 0 CHECK (display_order >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE UNIQUE INDEX ux_instruments_name_active
    ON instruments (lower(name)) WHERE is_active = 1 AND archived_at IS NULL;
CREATE INDEX ix_instruments_section ON instruments (section_id, is_active);

DELETE FROM sections;

INSERT INTO sections (name, is_active, display_order) VALUES
    ('Clarinetti', 1, 1),
    ('Trombe', 1, 2),
    ('Corni', 1, 3),
    ('Oboi', 1, 4),
    ('Flauti', 1, 5),
    ('Ottoni', 1, 6),
    ('Percussioni', 1, 7),
    ('Sax', 1, 8);

INSERT INTO instruments (name, section_id, is_active, display_order) VALUES
    ('Clarinetto', (SELECT id FROM sections WHERE name = 'Clarinetti'), 1, 1),
    ('Clarinetto Basso', (SELECT id FROM sections WHERE name = 'Clarinetti'), 1, 2),
    ('Clarinetto Piccolo', (SELECT id FROM sections WHERE name = 'Clarinetti'), 1, 3),
    ('Cornetta', (SELECT id FROM sections WHERE name = 'Trombe'), 1, 4),
    ('Corno', (SELECT id FROM sections WHERE name = 'Corni'), 1, 5),
    ('Corno Inglese', (SELECT id FROM sections WHERE name = 'Oboi'), 1, 6),
    ('Flauto Traverso', (SELECT id FROM sections WHERE name = 'Flauti'), 1, 7),
    ('Flicorno Baritono', (SELECT id FROM sections WHERE name = 'Ottoni'), 1, 8),
    ('Flicorno Contralto', (SELECT id FROM sections WHERE name = 'Corni'), 1, 9),
    ('Flicorno Soprano', (SELECT id FROM sections WHERE name = 'Ottoni'), 1, 10),
    ('Flicorno Tenore', (SELECT id FROM sections WHERE name = 'Ottoni'), 1, 11),
    ('Glockenspiel', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 12),
    ('Grancassa', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 13),
    ('Marimba', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 14),
    ('Oboe', (SELECT id FROM sections WHERE name = 'Oboi'), 1, 15),
    ('Ottavino', (SELECT id FROM sections WHERE name = 'Flauti'), 1, 16),
    ('Piatti', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 17),
    ('Rullante', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 18),
    ('Sax Baritono', (SELECT id FROM sections WHERE name = 'Sax'), 1, 19),
    ('Sax Contralto', (SELECT id FROM sections WHERE name = 'Sax'), 1, 20),
    ('Sax Soprano', (SELECT id FROM sections WHERE name = 'Sax'), 1, 21),
    ('Sax Tenore', (SELECT id FROM sections WHERE name = 'Sax'), 1, 22),
    ('Timpani', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 23),
    ('Tromba', (SELECT id FROM sections WHERE name = 'Ottoni'), 1, 24),
    ('Trombone', (SELECT id FROM sections WHERE name = 'Ottoni'), 1, 25),
    ('Tuba', (SELECT id FROM sections WHERE name = 'Ottoni'), 1, 26),
    ('Vibrafono', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 27),
    ('Xilofono', (SELECT id FROM sections WHERE name = 'Percussioni'), 1, 28);

CREATE TABLE musician_instruments (
    id INTEGER PRIMARY KEY,
    musician_id INTEGER NOT NULL REFERENCES musicians(id) ON DELETE RESTRICT,
    instrument_id INTEGER NOT NULL REFERENCES instruments(id) ON DELETE RESTRICT,
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    UNIQUE (musician_id, instrument_id)
);

CREATE UNIQUE INDEX ux_musician_primary_instrument
    ON musician_instruments (musician_id) WHERE is_primary = 1;
CREATE INDEX ix_musician_instruments_instrument ON musician_instruments (instrument_id);

--rollback DROP TABLE musician_instruments;
--rollback DROP TABLE instruments;
--rollback CREATE TABLE instruments (id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK (length(trim(name)) > 0), is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)), display_order INTEGER NOT NULL DEFAULT 0 CHECK (display_order >= 0), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT, archived_at TEXT, archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT, version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1));
--rollback CREATE UNIQUE INDEX ux_instruments_name_active ON instruments (lower(name)) WHERE is_active = 1 AND archived_at IS NULL;
--rollback CREATE TABLE musician_instruments (id INTEGER PRIMARY KEY, musician_id INTEGER NOT NULL REFERENCES musicians(id) ON DELETE RESTRICT, instrument_id INTEGER NOT NULL REFERENCES instruments(id) ON DELETE RESTRICT, is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT, UNIQUE (musician_id, instrument_id));
--rollback CREATE UNIQUE INDEX ux_musician_primary_instrument ON musician_instruments (musician_id) WHERE is_primary = 1;
--rollback CREATE INDEX ix_musician_instruments_instrument ON musician_instruments (instrument_id);
--rollback CREATE TABLE musician_sections (id INTEGER PRIMARY KEY, musician_id INTEGER NOT NULL REFERENCES musicians(id) ON DELETE RESTRICT, section_id INTEGER NOT NULL REFERENCES sections(id) ON DELETE RESTRICT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT, UNIQUE (musician_id, section_id));
