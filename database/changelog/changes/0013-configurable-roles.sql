--liquibase formatted sql

--changeset arsis:0013-configurable-roles
--comment Person roles become a configurable catalogue: the four built-in roles keep their codes and behaviour, custom roles can be added.

-- Built-in roles (is_system) drive courses, enrollments, instruments and member data,
-- so they cannot be archived. Comments stay outside statements: Liquibase strips them,
-- the bundled migrator keeps them, and stored DDL must match.
CREATE TABLE role_types (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE CHECK (
        length(code) BETWEEN 1 AND 50
        AND code GLOB '[a-z]*'
        AND code NOT GLOB '*[^a-z0-9-]*'
    ),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    plural_name TEXT NOT NULL CHECK (length(trim(plural_name)) > 0),
    description TEXT,
    is_system INTEGER NOT NULL DEFAULT 0 CHECK (is_system IN (0, 1)),
    display_order INTEGER NOT NULL DEFAULT 0 CHECK (display_order >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (is_system = 0 OR archived_at IS NULL)
);

CREATE UNIQUE INDEX ux_role_types_name_active ON role_types (lower(name))
    WHERE archived_at IS NULL;

INSERT INTO role_types (code, name, plural_name, description, is_system, display_order)
VALUES
    ('member', 'Socio', 'Soci', 'Iscritto all''associazione, con tessera e quota.', 1, 10),
    ('musician', 'Musicante', 'Musicanti', 'Suona nella banda, con strumenti e sezione.', 1, 20),
    ('student', 'Allievo', 'Allievi', 'Iscritto ai corsi della scuola.', 1, 30),
    ('teacher', 'Insegnante', 'Insegnanti', 'Tiene corsi e lezioni della scuola.', 1, 40);

-- person_roles: the CHECK on role_type becomes a foreign key to role_types(code).
-- Rebuilt without renaming tables, so triggers of other tables that mention
-- person_roles stay valid; ids are preserved for the role-specific tables.
CREATE TABLE _person_roles_0013 AS SELECT * FROM person_roles;
DROP TABLE person_roles;

CREATE TABLE person_roles (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    role_type TEXT NOT NULL REFERENCES role_types(code) ON DELETE RESTRICT,
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

INSERT INTO person_roles (
    id, person_id, role_type, start_date, end_date, status, notes, created_at, created_by,
    updated_at, updated_by, archived_at, archived_by, version
)
SELECT
    id, person_id, role_type, start_date, end_date, status, notes, created_at, created_by,
    updated_at, updated_by, archived_at, archived_by, version
FROM _person_roles_0013;
DROP TABLE _person_roles_0013;

CREATE UNIQUE INDEX ux_person_roles_active
    ON person_roles (person_id, role_type)
    WHERE archived_at IS NULL AND status = 'active' AND end_date IS NULL;
CREATE INDEX ix_person_roles_person ON person_roles (person_id, role_type, status);
CREATE INDEX ix_person_roles_type ON person_roles (role_type, status, archived_at);

-- accounting_categories: any role, built-in or custom, can be required.
CREATE TABLE _accounting_categories_0013 AS SELECT * FROM accounting_categories;
DROP TABLE accounting_categories;

CREATE TABLE accounting_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    direction TEXT NOT NULL CHECK (direction IN ('income', 'expense', 'both')),
    required_person_role TEXT REFERENCES role_types(code) ON DELETE RESTRICT,
    course_required INTEGER NOT NULL DEFAULT 0 CHECK (course_required IN (0, 1)),
    color TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    display_order INTEGER NOT NULL DEFAULT 0 CHECK (display_order >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    UNIQUE (name)
);

INSERT INTO accounting_categories (
    id, name, direction, required_person_role, course_required, color, is_active,
    display_order, created_at, created_by, updated_at, updated_by, archived_at, archived_by,
    version
)
SELECT
    id, name, direction, required_person_role, course_required, color, is_active,
    display_order, created_at, created_by, updated_at, updated_by, archived_at, archived_by,
    version
FROM _accounting_categories_0013;
DROP TABLE _accounting_categories_0013;

CREATE INDEX ix_accounting_categories_active
    ON accounting_categories (is_active, archived_at, display_order, name);

-- No automatic rollback: restore the pre-migration backup to undo the table rebuilds.
