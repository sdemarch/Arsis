# Distribuzione locale — promemoria

## Obiettivo

Distribuire Arsis come applicazione Windows locale: un solo avvio per API e
frontend, database SQLite e allegati conservati fuori dal binario, con un
salvataggio trasferibile dell'intero stato dell'app.

## Basi già disponibili

- SQLite è aperto solo dal backend, con WAL, foreign key e transazioni brevi.
- I dati runtime sono separati dall'app: in un exe il percorso predefinito è
  `%LOCALAPPDATA%\Arsis`.
- Il formato `.arsis-save` contiene manifest versionato, checksum, snapshot
  SQLite consistente e cartella allegati.
- `arsis-local` serve Angular compilato e API da un solo processo loopback; lo
  script `run-local.sh` lo prova con `ARSIS_MODE=runtime`.

## Regole per lo sviluppo funzionale

- Ogni dato persistente va nel database o nella cartella dati/allegati.
- Gli allegati usano identificatori o percorsi relativi, mai path assoluti.
- Lo schema cambia solo tramite changeset Liquibase; le evoluzioni devono
  restare compatibili con salvataggi esistenti.
- Ogni nuova area con file deve essere inclusa nell'export/import `.arsis-save`.

## Lavori da chiudere prima dell'exe

1. Inizializzazione e migrazioni automatiche al primo avvio e durante gli
   aggiornamenti, con backup precedente alla migrazione.
2. Modalità manutenzione e interfaccia per esportare/importare `.arsis-save`.
   L'import deve creare un backup preventivo, fermare le scritture e riavviare
   il runtime.
3. Launcher Windows: controllo della singola istanza, apertura browser e
   messaggi chiari in caso di porta occupata o migrazione fallita.
4. Packaging e installer: includere Python/runtime, backend, build Angular e
   strumenti di migrazione; non includere dati utente nel bundle.
5. Verifica di installazione, aggiornamento, backup e ripristino su un PC pulito.

## Dopo l'MVP locale

Per un'eventuale versione online: HTTPS, reverse proxy, rate limiting, CORS
ristretto, backup lato server e possibile passaggio a PostgreSQL. Le API e i
servizi di dominio devono restare indipendenti dal tipo di database.
