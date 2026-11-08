--liquibase formatted sql

--changeset arsis:0007-accounting-ledger
--comment Configurable categories and a cash/bank first-note ledger.

CREATE TABLE accounting_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    direction TEXT NOT NULL CHECK (direction IN ('income', 'expense', 'both')),
    required_person_role TEXT CHECK (required_person_role IN ('student', 'teacher', 'member')),
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

CREATE INDEX ix_accounting_categories_active
    ON accounting_categories (is_active, archived_at, display_order, name);

CREATE TABLE accounting_opening_balances (
    id INTEGER PRIMARY KEY,
    fiscal_year INTEGER NOT NULL CHECK (fiscal_year BETWEEN 2000 AND 2100),
    account TEXT NOT NULL CHECK (account IN ('bank', 'cash')),
    amount NUMERIC NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    UNIQUE (fiscal_year, account)
);

CREATE TABLE accounting_movements (
    id INTEGER PRIMARY KEY,
    occurred_on TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('income', 'expense')),
    account TEXT NOT NULL CHECK (account IN ('bank', 'cash')),
    category_id INTEGER NOT NULL REFERENCES accounting_categories(id) ON DELETE RESTRICT,
    amount NUMERIC NOT NULL CHECK (amount > 0),
    subject TEXT NOT NULL CHECK (length(trim(subject)) > 0),
    person_id INTEGER REFERENCES people(id) ON DELETE RESTRICT,
    course_id INTEGER REFERENCES courses(id) ON DELETE RESTRICT,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    document_reference TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1)
);

CREATE INDEX ix_accounting_movements_date ON accounting_movements (occurred_on, id);
CREATE INDEX ix_accounting_movements_account_date ON accounting_movements (account, occurred_on, id);
CREATE INDEX ix_accounting_movements_category ON accounting_movements (category_id, occurred_on);
CREATE INDEX ix_accounting_movements_person ON accounting_movements (person_id, occurred_on);
CREATE INDEX ix_accounting_movements_course ON accounting_movements (course_id, occurred_on);

INSERT INTO accounting_categories
    (name, direction, required_person_role, course_required, color, display_order)
VALUES
    ('Retta scuola', 'income', 'student', 1, '#1D9E75', 10),
    ('Quota associativa', 'income', 'member', 0, '#378ADD', 20),
    ('Contributo o donazione', 'income', NULL, 0, '#2BA8A0', 30),
    ('Incasso evento', 'income', NULL, 0, '#7F77DD', 40),
    ('Rimborso insegnante', 'expense', 'teacher', 1, '#D85A30', 50),
    ('Acquisto materiali', 'expense', NULL, 0, '#BA7517', 60),
    ('Spesa attività', 'expense', NULL, 0, '#C2507A', 70),
    ('Commissione bancaria', 'expense', NULL, 0, '#5A6572', 80),
    ('Altro', 'both', NULL, 0, NULL, 90);

--rollback DROP TABLE accounting_movements;
--rollback DROP TABLE accounting_opening_balances;
--rollback DROP TABLE accounting_categories;
