# Stato di avanzamento — Arsis

_Aggiornato: 3 settembre 2026_

## Sintesi

Il progetto ha una base tecnica solida e un frontend Angular funzionante. Non è ancora un MVP integrato: le pagine usano dati mock e le API di dominio non sono collegate all'interfaccia.

## Completato

- Documentazione funzionale, tecnica, ADR e token di design disponibili.
- Schema SQLite gestito con Liquibase (4 changeset), con modelli SQLAlchemy e DTO Pydantic generati.
- Backend `src/arsis` con configurazione, logging, protezioni SQLite, health check e test mirati.
- Frontend consolidato su **Angular**: React/Vite e i relativi componenti sono stati rimossi.
- Pagine Angular per login, home, persone, attività, scuola, archivio, contabilità e configurazioni.
- Build di produzione Angular verificata con successo il 3 settembre 2026; sviluppo locale disponibile su `http://localhost:4200`.

## Da consolidare

- **Backend duplicato:** coesistono `backend/src/arsis` e la precedente app `backend/app`.
- **Integrazione:** il frontend legge ancora JSON mock; `src/arsis` espone per ora health check e API index, non i flussi di dominio.
- **Tooling:** Makefile e test fanno ancora riferimento alla precedente app backend, mentre README e `pyproject.toml` indicano `arsis.main` e Liquibase.
- **Qualità backend:** la suite non parte perché `tests/conftest.py` importa la vecchia app e la `.env` radice contiene chiavi incompatibili con quella configurazione.

## Prossime priorità

1. Consolidare il backend su `src/arsis` e allineare Makefile, ambiente e test.
2. Implementare le API di dominio e sostituire progressivamente i mock Angular.
3. Ripristinare CI con build frontend, test backend e verifica della generazione dello schema.
