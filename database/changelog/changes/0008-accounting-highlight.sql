--liquibase formatted sql

--changeset arsis:0008-accounting-highlight
--comment Let responsible users flag first-note movements that need attention.

ALTER TABLE accounting_movements
    ADD COLUMN is_highlighted INTEGER NOT NULL DEFAULT 0 CHECK (is_highlighted IN (0, 1));

--rollback ALTER TABLE accounting_movements DROP COLUMN is_highlighted;
