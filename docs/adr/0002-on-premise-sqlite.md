# ADR 0002 — Distribuzione on-premise e SQLite

- Stato: accettata
- Data: 20 agosto 2026

## Contesto

Arsis verrà eseguita su un singolo PC server e usata da poche persone nella stessa rete locale, con connessioni occasionali e normalmente non simultanee. Si vuole evitare una dipendenza operativa da Docker e ridurre al minimo l'amministrazione del database.

## Decisione

- SQLite sostituisce PostgreSQL come database dell'MVP.
- Il file predefinito è `data/arsis.db` sul disco locale del server.
- Soltanto il processo FastAPI accede al file; i client comunicano via HTTP e non aprono mai il database direttamente.
- SQLite usa foreign key abilitate, journal WAL, timeout di attesa sulle scritture e transazioni brevi.
- Il backend viene eseguito inizialmente con un solo worker.
- Liquibase Community 5.0.3 resta la fonte autorevole delle migrazioni.
- Il driver SQLite JDBC è dichiarato in `database/liquibase.json` e installato localmente tramite LPM.
- Docker e PostgreSQL non fanno parte del runtime o dello sviluppo ordinario.
- In produzione Angular è precompilato e servito dal backend; `npm` non viene avviato sul server.

## Conseguenze

L'installazione non richiede un servizio database e il backup riguarda principalmente il file SQLite e le foto. Il file non deve essere collocato su OneDrive, NAS o share di rete. Prima degli aggiornamenti l'installer deve produrre un backup consistente, applicare Liquibase e avviare una sola istanza del backend.

Un ritorno a PostgreSQL richiederà una migrazione dati e nuovi changeset specifici. La scelta andrà rivalutata se aumentano scritture simultanee, istanze backend o requisiti di alta disponibilità.

