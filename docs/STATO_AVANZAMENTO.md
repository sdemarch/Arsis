# Stato di avanzamento — Arsis

_Aggiornato: 14 ottobre 2026_

## Sintesi

Il progetto ha una base tecnica solida e un frontend Angular funzionante. Non è ancora un MVP integrato: le pagine usano dati mock e le API di dominio non sono collegate all'interfaccia.

## Completato

- Documentazione funzionale, tecnica, ADR e token di design disponibili.
- Schema SQLite gestito con Liquibase (4 changeset), con modelli SQLAlchemy e DTO Pydantic generati.
- Backend `src/arsis` con configurazione, logging, protezioni SQLite, health check e test mirati.
- Connessione SQLite condivisa, backup e ripristino consistente del database.
- Backend consolidato sul solo package `src/arsis`; rimossi lo scaffold MySQL,
  Alembic e le configurazioni duplicate.
- Seed locale idempotente allineato agli scenari mostrati dal frontend.
- Frontend consolidato su **Angular**: React/Vite e i relativi componenti sono stati rimossi.
- Pagine Angular per login, home, persone, attività, scuola, archivio, contabilità e configurazioni.
- Build di produzione Angular verificata con successo il 3 settembre 2026; sviluppo locale disponibile su `http://localhost:4200`.

## Da consolidare

- **Integrazione:** il frontend legge ancora JSON mock; `src/arsis` espone per ora health check e API index, non i flussi di dominio.
- **Contratto API:** mancano ancora convenzioni condivise per errori, paginazione,
  concorrenza ottimistica e DTO pubblici.

## Prossime priorità

1. Definire le fondamenta comuni e il contratto delle API.
2. Implementare autenticazione e prima fetta verticale Persone.
3. Sostituire progressivamente i mock Angular e completare la CI.
