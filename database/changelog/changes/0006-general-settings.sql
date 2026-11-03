--liquibase formatted sql

--changeset arsis:0006-general-settings
--comment Default organization metadata managed from the general settings screen.

INSERT INTO app_settings (key, value, description)
VALUES
    ('organization.name', '"Società Filarmonica G. Rossini"', 'Denominazione visualizzata dell’organizzazione');

--rollback DELETE FROM app_settings WHERE key = 'organization.name';
