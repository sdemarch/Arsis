# Arsis — Stato

_Aggiornato: 8 novembre 2026 · versione `0.1.0`, non ancora rilasciata_

Cosa c'è oggi nell'applicazione. Cosa manca è in [TODO](TODO.md); i requisiti
completi in [Specifica funzionale](SPECIFICA_FUNZIONALE.md).

## In sintesi

- Tutte le aree della topbar e Configurazioni consumano l'API locale; non restano
  dati mock.
- Backend: Ruff e mypy puliti, 74 test verdi; CI su ogni pull request.
- Runtime: `arsis-local` e `Arsis.exe` servono API e SPA da un solo processo,
  applicano le migrazioni e gestiscono il primo avvio.
- Manca il primo rilascio: test end-to-end, installer collaudato su PC pulito.

## Per area

| Area | Disponibile | Non ancora |
|---|---|---|
| **Accesso** | login, logout, refresh in cookie, primo responsabile dalla pagina di accesso, limite agli accessi falliti | recupero password |
| **Home** | persone attive per ruolo, prossime attività con convocati, lezioni del giorno, indicatori della scuola, accessi rapidi | — |
| **Soci** | anagrafica unica con ricerca e filtro per ruolo; scheda con dati personali, ruoli con date, contatti, note, storico attività; archiviazione | contatti associati, dati specifici dei ruoli (tessera, quota, strumenti del musicante), foto, riattivazione dei record archiviati, corsi e presenze lezioni nella scheda |
| **Attività** | prove, concerti, eventi; elenco filtrato per tipo e calendario mensile; convocazione automatica dei musicanti attivi; aggiunta e rimozione di partecipanti; registro presenze con compilazione rapida | elenco oltre 100 attività |
| **Scuola** | corsi con colore, insegnante e tariffa; iscrizioni; lezioni manuali; registro presenze con modello e import Excel `.xlsx`; panoramica | piano rate proposto, agevolazioni sulle iscrizioni |
| **Archivio** | apertura della cartella Google Drive configurata | — |
| **Contabilità** | prima nota Banca e Cassa, categorie configurabili con regole su persona e corso, filtri ed evidenziazione, saldi iniziali, bilancio annuale per conto e categoria | tutto ciò che va oltre la prima nota (vedi TODO) |
| **Configurazioni** | nome organizzazione, URL Drive, tema predefinito, responsabili, strumenti e sezioni, categorie contabili, salvataggi | selettore del tema per utente |

## Piattaforma

| Ambito | Stato |
|---|---|
| Database | SQLite WAL, 8 changeset (`0001`–`0008`), modelli e DTO generati dallo schema |
| API | convenzioni uniformi su errori, liste, versioni, request ID e audit ([Architettura §5](ARCHITETTURA.md#5-contratto-api)) |
| Migrazioni | automatiche all'avvio senza Java, con backup e rifiuto dei database più recenti |
| Salvataggi | export, verifica e import `.arsis-save` da Configurazioni, con modalità manutenzione e backup pre-import |
| Sicurezza | Argon2id, JWT in memoria, refresh ruotato, `secret.key` per installazione, binding loopback |
| Distribuzione | exe PyInstaller e installer Inno Setup con `scripts/build-windows.ps1`, non ancora collaudati su PC pulito |
| Qualità | CI: Ruff, mypy, pytest, schema da changelog, build Angular; nessun test frontend o end-to-end |

## Cronologia

| Fase | Contenuto |
|---|---|
| 0–1 | SQLite, backup consistente, package backend unico, Liquibase, codice generato, seed |
| 2–3 | fondamenta API (errori, paginazione, transazioni, audit, concorrenza) e autenticazione |
| 4–5 | anagrafica Persone e integrazione Angular di autenticazione, persone, attività e corsi |
| 6a–6f | attività, corsi, iscrizioni, catalogo strumenti e sezioni, lezioni, registro presenze con Excel |
| 6g–6i | percorsi dati e formato `.arsis-save`, runtime locale, configurazioni generali |
| 6j–6m | prima nota contabile, convocazione e presenze delle attività, cablaggio completo del frontend, calendario e dashboard |
| 7a | preparazione al rilascio: CI, migratore, primo avvio, chiave per installazione, limite agli accessi, launcher, exe e installer |
| 7b-1 | salvataggi dall'interfaccia |
