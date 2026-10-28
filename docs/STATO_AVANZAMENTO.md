# Stato di avanzamento — Arsis

_Aggiornato: 26 ottobre 2026_

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
- Fondamenta API condivise per errori, request ID, paginazione, ordinamento,
  transazioni, audit e concorrenza ottimistica.
- Autenticazione backend con password Argon2id, access token JWT, refresh token
  ruotato in cookie HttpOnly, logout, profilo corrente e bootstrap monouso del
  primo responsabile.
- Frontend consolidato su **Angular**: React/Vite e i relativi componenti sono stati rimossi.
- Pagine Angular per login, home, persone, attività, scuola, archivio, contabilità e configurazioni.
- Build di produzione Angular verificata con successo il 3 settembre 2026; sviluppo locale disponibile su `http://localhost:4200`.

## Da consolidare

- **Integrazione:** login, rinnovo della sessione e flusso Persone (lista, scheda,
  creazione, modifica, archiviazione e ruoli) leggono le API locali; gli altri
  moduli usano ancora JSON mock.
- **Dominio:** le convenzioni API e l'autenticazione sono definite; mancano ancora
  gli endpoint dei moduli applicativi.

## Prossime priorità

1. Sostituire progressivamente i mock degli altri moduli.
2. Completare la CI e l'hardening di deploy (HTTPS e rate limiting).
