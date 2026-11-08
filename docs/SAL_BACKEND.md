# SAL sviluppo — Arsis

_Aggiornato: 8 novembre 2026_

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
- [x] **6i. Configurazioni generali** — cataloghi musicali, nome organizzazione,
  collegamento Google Drive, tema predefinito e gestione dei responsabili,
  con persistenza, audit e concorrenza ottimistica.

- [x] **6j. Contabilità: prima nota** — categorie configurabili con verso,
  ruolo della persona e corso obbligatori; movimenti Banca/Cassa con filtri per
  anno, mese, conto, categoria, ricerca ed evidenziazione; saldi iniziali per esercizio e
  bilancio annuale per conto e categoria; audit, concorrenza ottimistica, test
  API e schermate Angular (registro, bilancio, gestione categorie).

- [x] **6k. Attività: convocazione e presenze** — musicanti attivi convocati
  alla creazione, aggiunta e rimozione dei partecipanti, registro presenze con
  compilazione rapida, conteggi nelle liste e storico nella scheda persona.
- [x] **6l. Cablaggio frontend** — moduli di corsi, iscrizioni e lezioni con
  selettori al posto degli ID, archivio collegato alla cartella configurata,
  stato reale del database nella shell.
- [x] **6m. Calendario e dashboard** — calendario mensile delle attività su
  intervallo di date, date locali con fuso nelle attività, riepilogo
  `/dashboard/summary` per Home e panoramica della Scuola; rimossi tutti i
  dati mock del frontend.

## Da completare

- [ ] **7. Rilascio** — test end-to-end, CI, rate limiting, HTTPS, procedure di
  installazione e aggiornamento on-premise.

## Stato rapido

- Backend: API complete per autenticazione, persone, attività con convocati e
  presenze, corsi, iscrizioni, lezioni, presenze, configurazioni generali,
  contabilità e dashboard; Ruff e mypy puliti, test backend verdi all'ultimo
  controllo.
- Frontend: tutte le aree consumano le API locali; non restano dati mock.
- Runtime: `arsis-local` serve API e Angular compilato dallo stesso processo;
  salvataggi `.arsis-save` pronti per database e allegati.
- Prossimo avanzamento: rilascio (punto 7).
- Dopo l'MVP funzionale: migrazioni automatiche, interfaccia export/import,
  launcher e installer Windows.
