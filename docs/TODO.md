# Arsis — TODO

_Aggiornato: 8 novembre 2026_

Lavori aperti, in ordine di priorità. Spuntare o rimuovere le voci quando sono
completate e aggiornare [Stato](STATO.md). Le idee di prodotto non ancora
pianificate sono in `NEXT_FEATURES.md`.

## 1. Primo rilascio

- [ ] **Test end-to-end** (Playwright) sul runtime locale per i flussi di
  [Architettura §10](ARCHITETTURA.md#10-test-e-ci). Oggi le schermate sono
  verificate solo dalla build.
- [ ] **Installer e collaudo su PC pulito.** Installare Inno Setup 6, generare
  l'installer e completare la checklist di [Rilascio](operations/rilascio.md):
  installazione nuova, aggiornamento con backup, export/import di un salvataggio,
  secondo avvio, porta occupata, disinstallazione.

## 2. Requisiti MVP non ancora implementati

Previsti dalla [Specifica funzionale](SPECIFICA_FUNZIONALE.md) e dai suoi
criteri di accettazione (§17), con tabelle già presenti nello schema ma senza API
né interfaccia:

- [ ] **Contatti associati** (§8.4, criterio 4): collegare un minorenne a un
  genitore o tutore già registrato, contatto principale e responsabile pagamenti.
- [ ] **Dati dei ruoli** (§8.5–8.8): tessera e quota del socio; strumenti del
  musicante con strumento principale e sezioni dedotte (criterio 5).
- [ ] **Piano rate proposto** del corso (§10.4, criterio 10), confrontato con la
  tariffa annuale.
- [ ] **Agevolazioni** sull'iscrizione, fisse o percentuali, con prezzo agevolato
  calcolato dal backend (§10.5, criterio 11).
- [ ] **Riattivazione** dei record archiviati (RF-TR-02, criterio 15): oggi
  l'archiviazione non si annulla dall'interfaccia.
- [ ] **Scheda persona completa** (§8.3): corsi frequentati o tenuti e storico
  presenze alle lezioni, accanto allo storico attività già presente.
- [ ] **Foto della persona** (§8.3): da salvare in `attachments/`, con limiti di
  formato e dimensione; incluse automaticamente nei salvataggi.

## 3. Qualità e manutenzione

- [ ] **Shell responsive.** Topbar e sidebar fissa da 240 px non hanno breakpoint
  comuni; su schermi stretti possono comprimersi o andare in overflow.
- [ ] **Test del frontend.** Partire da autenticazione, interceptor HTTP e moduli
  con logica (prima nota, registro presenze, salvataggi).
- [ ] **Lockfile delle dipendenze.** `uv.lock` è escluso da git: CI ed exe
  installano le versioni più recenti ammesse. Versionarlo o fissare le versioni.
- [ ] **SQLAlchemy 2.1.** La dipendenza è limitata a `<2.1`: la 2.1 cambia la
  tipizzazione dei risultati e mypy segnala errori in otto moduli.
- [ ] **Stile del codice.** Ruff `format` non è uniforme (circa 26 file):
  riformattare in un commit dedicato, poi aggiungerlo alla CI.
- [ ] **Contabilità più leggibile.** Pagina, tabella e modulo restano densi:
  valutare componenti più piccoli quando si toccherà l'area.

## 4. Minori

- [ ] **Elenco attività oltre 100 voci**: la lista ne carica al massimo 100 (il
  calendario no); aggiungere paginazione o filtro per anno lato server.
- [ ] **Firma dell'installer**: senza certificato Windows mostra SmartScreen.
- [ ] **Revoca dei token dopo un import** persistente: oggi vive in memoria
  (vedi [Salvataggi](operations/salvataggi.md)).
- [ ] **Selettore del tema** per utente e persistenza della preferenza (§16.2).

## 5. Decisioni di prodotto aperte

- [ ] **Contabilità oltre la prima nota** (§18): rate generate dal piano del corso,
  pagamenti parziali, scadenze e insoluti, ricevute, compensi degli insegnanti,
  collegamento alle attività, rendicontazione. Richiede l'intervista prevista.
- [ ] **Assunzioni da confermare** (§19) con i responsabili: contatti multipli con
  uno principale, strumento principale, stati di attività, corsi e lezioni, date
  sui ruoli, contenuti della dashboard, dati dell'insegnante per la contabilità.
- [ ] **Vincolo sul codice fiscale**: univoco parziale solo se la qualità dei dati
  lo consente.

## Ambiente di sviluppo

- `JAVA_HOME` deve puntare a Java 17+, altrimenti `init-db.ps1` si ferma.
- Dopo modifiche a `pyproject.toml` reinstallare il backend (`pip install -e ".[dev]"`).
