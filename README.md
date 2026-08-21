# Arsis

Monorepo dell'MVP gestionale Arsis, organizzato come applicazione on-premise monolitica con frontend Angular, API FastAPI, database SQLite locale e migrazioni Liquibase standalone.

## Struttura

- `frontend/`: SPA Angular standalone, suddivisa per aree funzionali.
- `backend/`: API FastAPI modulare sotto `/api/v1`.
- `database/`: changelog Liquibase e dipendenze dichiarate del driver SQLite.
- `docs/`: ADR, contratto API e procedure operative.
- `scripts/`: comandi di supporto allo sviluppo.

## Stile dell'interfaccia

Colori, font, spaziature, raggi, ombre e transizioni si modificano in un solo punto:

`frontend/src/styles/tokens.css`

I componenti non contengono colori di brand hardcoded. La palette dei corsi è invece un dato applicativo e si trova in `frontend/src/app/core/config/course-colors.ts`.

## Avvio locale

1. Copiare `.env.example` in `.env`.
2. Inizializzare o aggiornare il database: `.\scripts\init-db.ps1`. Il comando applica
   Liquibase e rigenera anche modelli SQLAlchemy e DTO Pydantic.
3. Backend: creare un virtualenv, quindi da `backend/` eseguire `pip install -e ".[dev]"` e `uvicorn arsis.main:app --reload`.
4. Frontend: da `frontend/` eseguire `npm install` e `npm start`.

Endpoint di controllo: `http://localhost:8000/health/live` e `http://localhost:8000/health/ready`.

Quando si aggiunge un changeset Liquibase non serve propagare manualmente colonne e
tabelle nel backend: rieseguendo `.\scripts\init-db.ps1` vengono aggiornati i file in
`backend/src/arsis/generated/`. Il controllo
`py -3.14 .\scripts\generate_backend_schema.py --check` segnala eventuali disallineamenti.

In produzione Angular viene compilato e incluso nel pacchetto: Node.js e `npm` non vengono avviati sul PC server. Il file `data/arsis.db` deve restare sul disco locale ed essere aperto esclusivamente dal backend.

## Documenti di riferimento

- [Specifica funzionale](SPECIFICA_FUNZIONALE.md)
- [Specifica tecnica](SPECIFICA_TECNICA.md)
- [Design tokens v1.1](arsis-design-tokens.md)
- [ADR stack iniziale](docs/adr/0001-stack-iniziale.md)
- [ADR distribuzione on-premise e SQLite](docs/adr/0002-on-premise-sqlite.md)
