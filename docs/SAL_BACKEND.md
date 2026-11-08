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

- [x] **7a. Preparazione al rilascio** — CI su ogni PR, migrazioni automatiche
  senza Java con backup, primo responsabile dal primo avvio, chiave di firma per
  installazione, limite agli accessi falliti, launcher con singola istanza e
  messaggi d'errore, exe PyInstaller e installer Inno Setup.

## Da completare

- [ ] **7b. Primo rilascio** — interfaccia export/import `.arsis-save`, test
  end-to-end, build dell'installer e verifica su PC pulito secondo la
  [guida rapida al rilascio](operations/RELEASE.md).

## Lavori aperti

Aggiornato all'8 novembre 2026. Chiudere le voci qui quando vengono completate.

### Prima del primo rilascio

- [ ] **Export/import dei salvataggi dall'interfaccia.** Il formato
  `.arsis-save` esiste ([Salvataggi portabili](operations/portable-saves.md)) ma
  l'utente non può usarlo. Serve una modalità manutenzione: backup preventivo,
  blocco delle scritture, import e riavvio del runtime.
- [ ] **Test end-to-end** (Playwright) sul runtime locale, per i flussi minimi
  della specifica: primo avvio, persone e ruoli, attività con convocati e
  presenze, corsi, iscrizioni, lezioni e registro, prima nota, archivio. Oggi le
  schermate sono verificate solo dalla build.
- [ ] **Installer e collaudo su PC pulito.** Installare Inno Setup 6, generare
  l'installer e completare la checklist della guida al rilascio (installazione
  nuova, aggiornamento con backup, secondo avvio, disinstallazione).

### Qualità e manutenzione

- [ ] **Shell responsive.** Topbar e sidebar fissa da 240 px non hanno
  breakpoint comuni (vedi [Check interfaccia](CHECK_INTERFACCIA.md)).
- [ ] **Font allineati ai token.** I font importati (DM Sans, DM Mono, Fraunces)
  non coincidono con quelli dichiarati in `tokens.css`.
- [ ] **Lockfile delle dipendenze.** `uv.lock` è escluso da git: build e CI
  installano le versioni più recenti ammesse. Versionarlo, o fissare le versioni,
  rende riproducibili CI ed eseguibile.
- [ ] **Test del frontend.** Non esistono test Angular; partire da autenticazione,
  interceptor HTTP e moduli con logica (prima nota, registro presenze).
- [ ] **Aggiornamento a SQLAlchemy 2.1.** La dipendenza è limitata a `<2.1`: la
  2.1 cambia la tipizzazione dei risultati e mypy segnala errori in otto moduli.
  Da pianificare insieme a una passata completa dei test.

### Minori

- [ ] **Elenco attività oltre 100 voci.** La lista carica al massimo 100 attività
  (il calendario no, usa l'intervallo di date): aggiungere paginazione o filtro
  per anno lato server.
- [ ] **Firma dell'installer.** Senza certificato Windows mostra l'avviso
  SmartScreen al primo avvio.
- [ ] **Stile del codice.** Ruff `format` non è applicato in modo uniforme
  (26 file da riformattare): farlo in un commit dedicato, poi aggiungerlo alla CI.

### Decisioni di prodotto

- [ ] **Contabilità oltre la prima nota.** Rate, scadenze e insoluti, ricevute,
  compensi degli insegnanti e rendicontazione richiedono l'intervista prevista
  (specifica funzionale §18).

### Ambiente di sviluppo locale

- `JAVA_HOME` deve puntare a Java 17 o superiore, altrimenti `init-db.ps1` si ferma.
- Dopo l'aggiornamento di `pyproject.toml` reinstallare il backend
  (`pip install -e ".[dev]"`): un `.venv` vecchio può non avere tutte le
  dipendenze.

## Stato rapido

- Backend: API complete per autenticazione, persone, attività con convocati e
  presenze, corsi, iscrizioni, lezioni, presenze, configurazioni generali,
  contabilità e dashboard; Ruff e mypy puliti, test backend verdi all'ultimo
  controllo.
- Frontend: tutte le aree consumano le API locali; non restano dati mock.
- Runtime: `arsis-local` serve API e Angular compilato dallo stesso processo,
  applica le migrazioni all'avvio e gestisce il primo avvio; exe e installer si
  generano con `scripts/build-windows.ps1`.
- Prossimo avanzamento: punto 7b e la sezione "Prima del primo rilascio".
