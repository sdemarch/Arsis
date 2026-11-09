# Arsis

Monorepo dell'MVP gestionale Arsis, organizzato come applicazione on-premise monolitica con frontend Angular, API FastAPI, database SQLite locale e migrazioni Liquibase standalone.

## Struttura

- `frontend/`: SPA Angular standalone, suddivisa per aree funzionali.
- `backend/`: API FastAPI modulare sotto `/api/v1`.
- `database/`: changelog Liquibase e dipendenze dichiarate del driver SQLite.
- `docs/`: stato, TODO, specifica, architettura e procedure operative ([indice](docs/README.md)).
- `scripts/`: comandi di supporto allo sviluppo.

## Stile dell'interfaccia

Colori, font, spaziature, raggi, ombre e transizioni si modificano in un solo punto:

`frontend/src/styles/tokens.css`

I componenti non contengono colori di brand hardcoded. La palette dei corsi è invece un dato applicativo e si trova in `frontend/src/app/core/config/course-colors.ts`.

## Avvio in sviluppo

Prerequisiti: Python 3.14, Node.js 24, Liquibase 5 e Java 17 o superiore.

1. Copiare `.env.example` in `.env`.
2. Inizializzare o aggiornare il database: `.\scripts\init-db.ps1`. Il comando applica
   Liquibase e rigenera anche modelli SQLAlchemy e DTO Pydantic.
3. Per caricare i dati dimostrativi usati dalle schermate Angular, eseguire
   `.\scripts\seed-dev.ps1`. Il comando è idempotente ed è consentito
   soltanto negli ambienti locali, di sviluppo e test.
4. Installare le dipendenze backend e frontend:

   ```powershell
   Set-Location backend
   py -3.14 -m pip install -e ".[dev]"
   Set-Location ..\frontend
   npm install
   ```

5. Dalla radice, avviare i due processi di sviluppo con hot reload:

   ```bash
   ./run-local.sh
   ```

Endpoint di controllo: `http://localhost:8000/health/live` e `http://localhost:8000/health/ready`.

Quando si aggiunge un changeset Liquibase non serve propagare manualmente colonne e
tabelle nel backend: rieseguendo `.\scripts\init-db.ps1` vengono aggiornati i file in
`backend/src/arsis/generated/`. Il controllo
`py -3.14 .\scripts\generate_backend_schema.py --check` segnala eventuali disallineamenti.

## Runtime locale

Per provare il processo unico previsto per l'installazione locale, compilare
Angular e usare il runtime integrato:

```bash
ARSIS_MODE=runtime ./run-local.sh
```

Il runtime serve API e SPA dallo stesso processo su `127.0.0.1:8765`, applica da
solo le migrazioni mancanti (con backup preventivo) e, su un database vuoto, fa
creare il primo responsabile dalla pagina di accesso. In un exe i dati non
vengono inclusi nel bundle: senza `ARSIS_DATA_DIR` usano `%LOCALAPPDATA%\Arsis`.
Il database resta sul disco locale ed è aperto esclusivamente dal backend.

`arsis-migrate` applica le stesse migrazioni senza Java né Liquibase; in
sviluppo `init-db.ps1` resta il comando di riferimento perché rigenera anche
modelli e DTO.

## Rilascio e controlli

- Eseguibile e installer Windows: `.\scripts\build-windows.ps1`, dettagli in
  [Rilascio Windows](docs/operations/rilascio.md).
- Ogni pull request esegue `.github/workflows/ci.yml`: Ruff, mypy, pytest,
  database creato dal changelog e confrontato con i modelli generati, build
  Angular.

## Documenti di riferimento

- [Indice della documentazione](docs/README.md)
- [Stato](docs/STATO.md) e [TODO](docs/TODO.md)
- [Specifica funzionale](docs/SPECIFICA_FUNZIONALE.md)
- [Architettura](docs/ARCHITETTURA.md)
- [Sviluppo locale](docs/operations/sviluppo.md)
- [Rilascio Windows](docs/operations/rilascio.md)
- [Salvataggi e backup](docs/operations/salvataggi.md)
- [Design tokens v1.1](docs/riferimenti/design-tokens.md)
