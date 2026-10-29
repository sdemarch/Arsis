# SAL backend — Arsis

_Aggiornato: 29 ottobre 2026_

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
- [x] **5. Integrazione Angular** — autenticazione, Persone, Attività e Corsi
  collegati all'API; i mock restano solo nelle aree non implementate.
- [x] **6a. Attività** — CRUD, ricerca, paginazione, ordinamento, archiviazione
  e audit.
- [x] **6b. Scuola: Corsi** — CRUD, verifica dell'insegnante attivo, ricerca,
  paginazione, ordinamento, archiviazione, audit e schermate Angular.
- [ ] **6c. Moduli di dominio** — cataloghi, iscrizioni, lezioni, presenze,
  contabilità, archivio e configurazioni, procedendo per fette verticali.
- [x] **6d. Fondamenta distribuzione locale** — percorsi dati separati dal
  binario e salvataggi `.arsis-save` versionati, verificati e comprensivi di
  allegati futuri.
- [ ] **7. Rilascio** — test end-to-end, CI, rate limiting, HTTPS, procedure di
  installazione e aggiornamento on-premise.

## Stato rapido

- Backend: API complete per autenticazione, persone, attività e corsi; test della
  verticale Corsi aggiunti, Ruff e mypy puliti.
- Frontend: login, Persone, Attività e Corsi consumano le API locali; le sezioni
  rimanenti usano ancora mock.
- Prossimo avanzamento: iscrizioni ai corsi, poi lezioni e registro presenze.
