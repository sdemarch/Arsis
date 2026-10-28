# SAL backend — Arsis

_Aggiornato: 26 ottobre 2026_

## Chiusi

- [x] **0. SQLite e continuità dati** — connessione condivisa, health check,
  backup consistente e ripristino da file esportato.
- [x] **1. Consolidamento backend** — unico package `src/arsis`, migrazioni
  Liquibase, modelli generati e seed locale idempotente.
- [x] **2. Fondamenta API** — errori uniformi, request ID, paginazione,
  ordinamento, transazioni, audit e concorrenza ottimistica.
- [x] **3. Autenticazione** — Argon2id, JWT, refresh token ruotato in cookie
  HttpOnly, logout, profilo corrente e bootstrap monouso del primo responsabile.

## Aperti

- [x] **4. Persone** — prima fetta verticale completa: repository, servizi,
  CRUD, ruoli, ricerca, archiviazione e test API, esposta anche in Angular.
- [ ] **5. Integrazione Angular** — autenticazione e flusso Persone completi;
  restano da collegare gli altri moduli.
- [ ] **6. Moduli di dominio** — cataloghi, scuola, attività, contabilità,
  archivio e configurazioni, procedendo per fette verticali.
- [ ] **7. Rilascio** — test end-to-end, CI, rate limiting, HTTPS, procedure di
  installazione e aggiornamento on-premise.

## Stato rapido

- Backend: API di autenticazione e Persone disponibili; test, Ruff e mypy puliti
  all'ultimo controllo backend.
- Frontend: login, rinnovo sessione e flusso Persone (lista, creazione, modifica,
  archiviazione e ruoli) usano le API locali; gli altri moduli usano ancora mock.
