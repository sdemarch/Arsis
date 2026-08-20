--liquibase formatted sql

--changeset arsis:0003-activities-and-school
--comment Band activities, courses, enrollments, lessons and attendance registers.

CREATE TABLE activities (
    id TEXT PRIMARY KEY NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('rehearsal', 'concert', 'event')),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    description TEXT,
    starts_at TEXT NOT NULL,
    ends_at TEXT,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'planned' CHECK (
        status IN ('planned', 'confirmed', 'cancelled', 'completed')
    ),
    reference_person_id TEXT REFERENCES people(id) ON DELETE RESTRICT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (ends_at IS NULL OR ends_at > starts_at)
);

CREATE INDEX ix_activities_starts_at ON activities (starts_at);
CREATE INDEX ix_activities_type_date ON activities (type, starts_at);
CREATE INDEX ix_activities_status_date ON activities (status, starts_at);
CREATE INDEX ix_activities_archived ON activities (archived_at);

CREATE TABLE activity_participants (
    id TEXT PRIMARY KEY NOT NULL,
    activity_id TEXT NOT NULL REFERENCES activities(id) ON DELETE RESTRICT,
    person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    source TEXT NOT NULL CHECK (source IN ('automatic', 'manual')),
    attendance TEXT CHECK (attendance IS NULL OR attendance IN ('present', 'absent')),
    attendance_recorded_at TEXT,
    attendance_recorded_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    UNIQUE (activity_id, person_id),
    CHECK (attendance IS NOT NULL OR attendance_recorded_at IS NULL)
);

CREATE INDEX ix_activity_participants_person ON activity_participants (person_id, activity_id);
CREATE INDEX ix_activity_participants_attendance ON activity_participants (activity_id, attendance);

CREATE TABLE courses (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    description TEXT,
    mode TEXT NOT NULL CHECK (mode IN ('individual', 'group')),
    category TEXT NOT NULL CHECK (category IN ('instrument', 'ensemble')),
    instrument_id TEXT REFERENCES instruments(id) ON DELETE RESTRICT,
    teacher_person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    weekday INTEGER CHECK (weekday IS NULL OR weekday BETWEEN 1 AND 7),
    start_time TEXT,
    end_time TEXT,
    annual_fee NUMERIC NOT NULL CHECK (annual_fee >= 0),
    color TEXT NOT NULL CHECK (
        color IN ('#378ADD', '#1D9E75', '#D85A30', '#BA7517',
                  '#7F77DD', '#2BA8A0', '#C2507A', '#5A6572')
    ),
    valid_from TEXT,
    valid_to TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (
        (category = 'instrument' AND instrument_id IS NOT NULL)
        OR (category = 'ensemble' AND instrument_id IS NULL)
    ),
    CHECK (end_time IS NULL OR start_time IS NULL OR end_time > start_time),
    CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from)
);

CREATE INDEX ix_courses_teacher ON courses (teacher_person_id, status, archived_at);
CREATE INDEX ix_courses_instrument ON courses (instrument_id, status);
CREATE INDEX ix_courses_status ON courses (status, archived_at);

CREATE TABLE course_installment_templates (
    id TEXT PRIMARY KEY NOT NULL,
    course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    sequence_number INTEGER NOT NULL CHECK (sequence_number > 0),
    description TEXT,
    amount NUMERIC NOT NULL CHECK (amount >= 0),
    due_month INTEGER CHECK (due_month IS NULL OR due_month BETWEEN 1 AND 12),
    due_day INTEGER CHECK (due_day IS NULL OR due_day BETWEEN 1 AND 31),
    proposed_due_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    UNIQUE (course_id, sequence_number),
    CHECK (
        proposed_due_date IS NOT NULL
        OR (due_month IS NOT NULL AND due_day IS NOT NULL)
    )
);

CREATE INDEX ix_installment_templates_course
    ON course_installment_templates (course_id, sequence_number);

CREATE TABLE enrollments (
    id TEXT PRIMARY KEY NOT NULL,
    course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    student_person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    enrolled_on TEXT NOT NULL,
    starts_on TEXT NOT NULL,
    ends_on TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (
        status IN ('active', 'completed', 'cancelled')
    ),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (ends_on IS NULL OR ends_on >= starts_on)
);

CREATE UNIQUE INDEX ux_enrollments_open_active
    ON enrollments (course_id, student_person_id)
    WHERE status = 'active' AND ends_on IS NULL AND archived_at IS NULL;
CREATE INDEX ix_enrollments_course ON enrollments (course_id, status, starts_on, ends_on);
CREATE INDEX ix_enrollments_student ON enrollments (student_person_id, status, starts_on, ends_on);

CREATE TABLE enrollment_discounts (
    id TEXT PRIMARY KEY NOT NULL,
    enrollment_id TEXT NOT NULL UNIQUE REFERENCES enrollments(id) ON DELETE RESTRICT,
    type TEXT NOT NULL CHECK (type IN ('fixed', 'percentage')),
    value NUMERIC NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (
        (type = 'percentage' AND value >= 0 AND value <= 100)
        OR (type = 'fixed' AND value >= 0)
    )
);

CREATE TABLE lessons (
    id TEXT PRIMARY KEY NOT NULL,
    course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    teacher_person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    starts_at TEXT NOT NULL,
    ends_at TEXT,
    topic TEXT,
    status TEXT NOT NULL DEFAULT 'planned' CHECK (
        status IN ('planned', 'completed', 'cancelled')
    ),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    CHECK (ends_at IS NULL OR ends_at > starts_at)
);

CREATE INDEX ix_lessons_course_date ON lessons (course_id, starts_at);
CREATE INDEX ix_lessons_teacher_date ON lessons (teacher_person_id, starts_at);
CREATE INDEX ix_lessons_status_date ON lessons (status, starts_at);
CREATE INDEX ix_lessons_archived ON lessons (archived_at);

CREATE TABLE lesson_attendances (
    id TEXT PRIMARY KEY NOT NULL,
    lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE RESTRICT,
    student_person_id TEXT NOT NULL REFERENCES people(id) ON DELETE RESTRICT,
    attendance TEXT CHECK (attendance IS NULL OR attendance IN ('present', 'absent')),
    recorded_at TEXT,
    recorded_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    archived_at TEXT,
    archived_by TEXT REFERENCES users(id) ON DELETE RESTRICT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    UNIQUE (lesson_id, student_person_id),
    CHECK (attendance IS NOT NULL OR recorded_at IS NULL)
);

CREATE INDEX ix_lesson_attendances_student
    ON lesson_attendances (student_person_id, lesson_id);
CREATE INDEX ix_lesson_attendances_status
    ON lesson_attendances (lesson_id, attendance);

CREATE TRIGGER trg_courses_teacher_insert
BEFORE INSERT ON courses
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.teacher_person_id
      AND role_type = 'teacher'
      AND status = 'active'
      AND archived_at IS NULL
      AND start_date <= COALESCE(NEW.valid_from, date('now'))
      AND (end_date IS NULL OR end_date >= COALESCE(NEW.valid_from, date('now')))
)
BEGIN SELECT RAISE(ABORT, 'teacher_person_id has no active teacher role'); END;

CREATE TRIGGER trg_courses_teacher_update
BEFORE UPDATE OF teacher_person_id, valid_from ON courses
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.teacher_person_id
      AND role_type = 'teacher'
      AND status = 'active'
      AND archived_at IS NULL
      AND start_date <= COALESCE(NEW.valid_from, date('now'))
      AND (end_date IS NULL OR end_date >= COALESCE(NEW.valid_from, date('now')))
)
BEGIN SELECT RAISE(ABORT, 'teacher_person_id has no active teacher role'); END;

CREATE TRIGGER trg_enrollments_student_insert
BEFORE INSERT ON enrollments
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.student_person_id
      AND role_type = 'student'
      AND status = 'active'
      AND archived_at IS NULL
      AND start_date <= NEW.starts_on
      AND (end_date IS NULL OR end_date >= NEW.starts_on)
)
BEGIN SELECT RAISE(ABORT, 'student_person_id has no active student role'); END;

CREATE TRIGGER trg_enrollments_student_update
BEFORE UPDATE OF student_person_id, starts_on ON enrollments
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.student_person_id
      AND role_type = 'student'
      AND status = 'active'
      AND archived_at IS NULL
      AND start_date <= NEW.starts_on
      AND (end_date IS NULL OR end_date >= NEW.starts_on)
)
BEGIN SELECT RAISE(ABORT, 'student_person_id has no active student role'); END;

CREATE TRIGGER trg_lessons_teacher_insert
BEFORE INSERT ON lessons
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.teacher_person_id
      AND role_type = 'teacher'
      AND status = 'active'
      AND archived_at IS NULL
      AND start_date <= substr(NEW.starts_at, 1, 10)
      AND (end_date IS NULL OR end_date >= substr(NEW.starts_at, 1, 10))
)
BEGIN SELECT RAISE(ABORT, 'teacher_person_id has no active teacher role'); END;

CREATE TRIGGER trg_lessons_teacher_update
BEFORE UPDATE OF teacher_person_id, starts_at ON lessons
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.teacher_person_id
      AND role_type = 'teacher'
      AND status = 'active'
      AND archived_at IS NULL
      AND start_date <= substr(NEW.starts_at, 1, 10)
      AND (end_date IS NULL OR end_date >= substr(NEW.starts_at, 1, 10))
)
BEGIN SELECT RAISE(ABORT, 'teacher_person_id has no active teacher role'); END;

CREATE TRIGGER trg_lesson_attendances_student_insert
BEFORE INSERT ON lesson_attendances
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.student_person_id
      AND role_type = 'student'
      AND archived_at IS NULL
)
BEGIN SELECT RAISE(ABORT, 'student_person_id has no student role'); END;

CREATE TRIGGER trg_lesson_attendances_student_update
BEFORE UPDATE OF student_person_id ON lesson_attendances
FOR EACH ROW WHEN NOT EXISTS (
    SELECT 1
    FROM person_roles
    WHERE person_id = NEW.student_person_id
      AND role_type = 'student'
      AND archived_at IS NULL
)
BEGIN SELECT RAISE(ABORT, 'student_person_id has no student role'); END;

--rollback DROP TRIGGER trg_lesson_attendances_student_update;
--rollback DROP TRIGGER trg_lesson_attendances_student_insert;
--rollback DROP TRIGGER trg_lessons_teacher_update;
--rollback DROP TRIGGER trg_lessons_teacher_insert;
--rollback DROP TRIGGER trg_enrollments_student_update;
--rollback DROP TRIGGER trg_enrollments_student_insert;
--rollback DROP TRIGGER trg_courses_teacher_update;
--rollback DROP TRIGGER trg_courses_teacher_insert;
--rollback DROP TABLE lesson_attendances;
--rollback DROP TABLE lessons;
--rollback DROP TABLE enrollment_discounts;
--rollback DROP TABLE enrollments;
--rollback DROP TABLE course_installment_templates;
--rollback DROP TABLE courses;
--rollback DROP TABLE activity_participants;
--rollback DROP TABLE activities;
