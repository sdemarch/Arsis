# SAL sviluppo — Arsis

_Aggiornato: 3 novembre 2026_

## Completato

- [x] **0. SQLite e continuità dati** — connessione condivisa, health check,
  backup consistente e ripristino da file esportato.
- [x] **1. Consolidamento backend** — unico package `src/arsis`, migrazioni
  Liquibase, modelli generati e seed locale idempotente.
- [x] **2. Fondamenta API** — errori uniformi, request ID, paginazione,
  ordinamento, transazioni, audit e concorrenza ottimistica.
- [x] **3. Autenticazione** — Argon2id, JWT, refresh token ruotato in cookie
  HttpOnly, logout, profilo corrente e bootstrap monouso del primo responsabile.
- [x] **4. Persone** — prima fetta verticale completa: repository, servizi,
  CRUD, ruoli, ricerca, archiviazione e test API, esposta anche in Angular.
- [x] **5. Integrazione Angular** — autenticazione, Persone, Attività e Corsi
  collegati all'API; i mock restano solo nelle aree non implementate.
- [x] **6a. Attività** — CRUD, ricerca, paginazione, ordinamento, archiviazione
  e audit.
- [x] **6b. Scuola: Corsi** — CRUD, verifica dell'insegnante attivo, ricerca,
  paginazione, ordinamento, archiviazione, audit e schermate Angular.
- [x] **6c. Scuola: Iscrizioni** — CRUD, verifica di corso e ruolo allievo,
  prevenzione duplicati, ricerca, archiviazione, audit e schermate Angular.
- [x] **6d. Catalogo strumenti e sezioni** — catalogo iniziale e gestione
  CRUD/archiviazione, sezione obbligatoria per strumento e sezioni dei musicanti
  inferite dagli strumenti; eliminata l'assegnazione manuale musicante–sezione.
- [x] **6e. Scuola: Lezioni** — CRUD, validazione di corso e insegnante attivi,
  intervallo orario, ricerca, archiviazione, audit e schermate Angular.
- [x] **6f. Scuola: Registro presenze** — roster dedotto dalle iscrizioni valide,
  registrazione massiva, audit, schermate Angular e import/modello Excel `.xlsx`.
- [x] **6g. Fondamenta distribuzione locale** — percorsi dati separati dal
  binario e salvataggi `.arsis-save` versionati, verificati e comprensivi di
  allegati futuri.
- [x] **6h. Runtime locale** — comando unico loopback che serve Angular compilato
  e API dallo stesso processo.

## Da completare

- [ ] **6i. Moduli di dominio rimanenti** — contabilità, archivio e
  configurazioni generali, procedendo per fette verticali.
- [ ] **7. Rilascio** — test end-to-end, CI, rate limiting, HTTPS, procedure di
  installazione e aggiornamento on-premise.

## Stato rapido

- Backend: API complete per autenticazione, persone, attività, corsi,
  iscrizioni, lezioni e presenze; Ruff e mypy puliti, test backend verdi all'ultimo controllo.
- Frontend: login, Persone, Attività, Corsi, Iscrizioni, Lezioni e Presenze consumano le
  API locali; le sezioni rimanenti usano ancora mock.
- Runtime: `arsis-local` serve API e Angular compilato dallo stesso processo;
  salvataggi `.arsis-save` pronti per database e allegati.
- Prossimo avanzamento funzionale: configurazioni generali, poi contabilità.
- Dopo l'MVP funzionale: migrazioni automatiche, interfaccia export/import,
  launcher e installer Windows.
