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

- [ ] **4. Persone** — prima fetta verticale completa: repository, servizi,
  CRUD, ruoli, ricerca, archiviazione e test API.
- [ ] **5. Integrazione Angular** — collegare login/sessione e sostituire i mock
  della sezione Persone.
- [ ] **6. Moduli di dominio** — cataloghi, scuola, attività, contabilità,
  archivio e configurazioni, procedendo per fette verticali.
- [ ] **7. Rilascio** — test end-to-end, CI, rate limiting, HTTPS, procedure di
  installazione e aggiornamento on-premise.

## Stato rapido

- Backend: **28 test verdi**, Ruff e mypy puliti.
- Frontend: interfaccia Angular disponibile, ancora alimentata da dati mock.
- Ultimo avanzamento: commit `9e4778c`, presente su `dev` e non ancora pubblicato
  su `origin/dev`.
