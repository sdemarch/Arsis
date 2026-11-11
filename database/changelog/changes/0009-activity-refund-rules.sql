--liquibase formatted sql

--changeset arsis:0009-activity-refund-rules
--comment Configurable reimbursement amounts for recorded activity attendance.

INSERT INTO app_settings (key, value, description)
VALUES (
    'activities.refund_rules',
    '{"rehearsal":"0.00","concert":"0.00","event":"0.00"}',
    'Importo del rimborso per presenza registrata, per tipo di attività'
);

--rollback DELETE FROM app_settings WHERE key = 'activities.refund_rules';
