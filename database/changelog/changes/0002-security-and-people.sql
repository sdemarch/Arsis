--liquibase formatted sql

--changeset arsis:0002-security-and-people
--comment Users, unified people registry, roles and musical catalogues.

CREATE TABLE users (
    id TEXT PRIMARY KEY NOT NULL,
    email TEXT NOT NULL COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    last_login_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE UNIQUE INDEX ux_users_email ON users (lower(email));
CREATE INDEX ix_users_active ON users (is_active, archived_at);

CREATE TABLE refresh_sessions (
    id TEXT PRIMARY KEY NOT NULL,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    client_info TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (revoked_at IS NULL OR revoked_at >= created_at)
);

CREATE INDEX ix_refresh_sessions_user ON refresh_sessions (user_id, expires_at);
CREATE INDEX ix_refresh_sessions_expiry ON refresh_sessions (expires_at, revoked_at);

CREATE TABLE people (
    id TEXT PRIMARY KEY NOT NULL,
    first_name TEXT NOT NULL CHECK (length(trim(first_name)) > 0),
    last_name TEXT NOT NULL CHECK (length(trim(last_name)) > 0),
    birth_date TEXT,
    birth_place TEXT,
    tax_code TEXT COLLATE NOCASE,
    residence_address TEXT,
    email TEXT COLLATE NOCASE,
    phone TEXT,
    photo_key TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE INDEX ix_people_name ON people (last_name COLLATE NOCASE, first_name COLLATE NOCASE);
CREATE INDEX ix_people_tax_code ON people (tax_code) WHERE tax_code IS NOT NULL;
CREATE INDEX ix_people_email ON people (lower(email)) WHERE email IS NOT NULL;
CREATE INDEX ix_people_archived ON people (archived_at);

CREATE TABLE person_roles (
    id TEXT PRIMARY KEY NOT NULL,
    person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    role_type TEXT NOT NULL CHECK (role_type IN ('member', 'musician', 'student', 'teacher')),
    start_date TEXT NOT NULL,
    end_date TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE UNIQUE INDEX ux_person_roles_active
    ON person_roles (person_id, role_type)
    WHERE archived_at IS NULL AND status = 'active' AND end_date IS NULL;
CREATE INDEX ix_person_roles_person ON person_roles (person_id, role_type, status);
CREATE INDEX ix_person_roles_type ON person_roles (role_type, status, archived_at);

CREATE TABLE associated_contacts (
    id TEXT PRIMARY KEY NOT NULL,
    person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    contact_person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    relationship_type TEXT NOT NULL CHECK (
        relationship_type IN ('parent', 'guardian', 'family', 'reference', 'other')
    ),
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    is_payment_contact INTEGER NOT NULL DEFAULT 0 CHECK (is_payment_contact IN (0, 1)),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (person_id <> contact_person_id)
);

CREATE UNIQUE INDEX ux_associated_contacts_active
    ON associated_contacts (person_id, contact_person_id, relationship_type)
    WHERE archived_at IS NULL;
CREATE INDEX ix_associated_contacts_person ON associated_contacts (person_id, archived_at);
CREATE INDEX ix_associated_contacts_contact ON associated_contacts (contact_person_id, archived_at);

CREATE TABLE members (
    id TEXT PRIMARY KEY NOT NULL,
    person_role_id TEXT NOT NULL UNIQUE REFERENCES person_roles(id) ON DELETE RESTRICT,
    membership_number TEXT,
    membership_start_date TEXT NOT NULL,
    membership_end_date TEXT,
    annual_fee NUMERIC CHECK (annual_fee IS NULL OR annual_fee >= 0),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (membership_end_date IS NULL OR membership_end_date >= membership_start_date)
);

CREATE UNIQUE INDEX ux_membership_number_active
    ON members (membership_number COLLATE NOCASE)
    WHERE membership_number IS NOT NULL AND archived_at IS NULL;

CREATE TABLE musicians (
    id TEXT PRIMARY KEY NOT NULL,
    person_role_id TEXT NOT NULL UNIQUE REFERENCES person_roles(id) ON DELETE RESTRICT,
    joined_on TEXT NOT NULL,
    left_on TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (left_on IS NULL OR left_on >= joined_on)
);

CREATE TABLE students (
    id TEXT PRIMARY KEY NOT NULL,
    person_role_id TEXT NOT NULL UNIQUE REFERENCES person_roles(id) ON DELETE RESTRICT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE TABLE teachers (
    id TEXT PRIMARY KEY NOT NULL,
    person_role_id TEXT NOT NULL UNIQUE REFERENCES person_roles(id) ON DELETE RESTRICT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE TABLE instruments (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    display_order INTEGER NOT NULL DEFAULT 0 CHECK (display_order >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE UNIQUE INDEX ux_instruments_name_active
    ON instruments (lower(name)) WHERE is_active = 1 AND archived_at IS NULL;

CREATE TABLE sections (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    display_order INTEGER NOT NULL DEFAULT 0 CHECK (display_order >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE UNIQUE INDEX ux_sections_name_active
    ON sections (lower(name)) WHERE is_active = 1 AND archived_at IS NULL;

CREATE TABLE musician_instruments (
    id TEXT PRIMARY KEY NOT NULL,
    musician_id TEXT NOT NULL REFERENCES musicians(id) ON DELETE RESTRICT,
    instrument_id TEXT NOT NULL REFERENCES instruments(id) ON DELETE RESTRICT,
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    UNIQUE (musician_id, instrument_id)
);

CREATE UNIQUE INDEX ux_musician_primary_instrument
    ON musician_instruments (musician_id) WHERE is_primary = 1;
CREATE INDEX ix_musician_instruments_instrument ON musician_instruments (instrument_id);

CREATE TABLE musician_sections (
    id TEXT PRIMARY KEY NOT NULL,
    musician_id TEXT NOT NULL REFERENCES musicians(id) ON DELETE RESTRICT,
    section_id TEXT NOT NULL REFERENCES sections(id) ON DELETE RESTRICT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    UNIQUE (musician_id, section_id)
);

CREATE INDEX ix_musician_sections_section ON musician_sections (section_id);

CREATE TRIGGER trg_members_role_insert
BEFORE INSERT ON members
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'member'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a member role'); END;

CREATE TRIGGER trg_members_role_update
BEFORE UPDATE OF person_role_id ON members
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'member'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a member role'); END;

CREATE TRIGGER trg_musicians_role_insert
BEFORE INSERT ON musicians
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'musician'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a musician role'); END;

CREATE TRIGGER trg_musicians_role_update
BEFORE UPDATE OF person_role_id ON musicians
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'musician'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a musician role'); END;

CREATE TRIGGER trg_students_role_insert
BEFORE INSERT ON students
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'student'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a student role'); END;

CREATE TRIGGER trg_students_role_update
BEFORE UPDATE OF person_role_id ON students
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'student'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a student role'); END;

CREATE TRIGGER trg_teachers_role_insert
BEFORE INSERT ON teachers
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'teacher'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a teacher role'); END;

CREATE TRIGGER trg_teachers_role_update
BEFORE UPDATE OF person_role_id ON teachers
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1 FROM person_roles WHERE id = NEW.person_role_id AND role_type = 'teacher'
)
BEGIN SELECT RAISE(ABORT, 'person_role_id is not a teacher role'); END;

--rollback DROP TRIGGER trg_teachers_role_update;
--rollback DROP TRIGGER trg_teachers_role_insert;
--rollback DROP TRIGGER trg_students_role_update;
--rollback DROP TRIGGER trg_students_role_insert;
--rollback DROP TRIGGER trg_musicians_role_update;
--rollback DROP TRIGGER trg_musicians_role_insert;
--rollback DROP TRIGGER trg_members_role_update;
--rollback DROP TRIGGER trg_members_role_insert;
--rollback DROP TABLE musician_sections;
--rollback DROP TABLE musician_instruments;
--rollback DROP TABLE sections;
--rollback DROP TABLE instruments;
--rollback DROP TABLE teachers;
--rollback DROP TABLE students;
--rollback DROP TABLE musicians;
--rollback DROP TABLE members;
--rollback DROP TABLE associated_contacts;
--rollback DROP TABLE person_roles;
--rollback DROP TABLE people;
--rollback DROP TABLE refresh_sessions;
--rollback DROP TABLE users;
