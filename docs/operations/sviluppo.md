# Sviluppo locale

## Prerequisiti

- Python 3.14 (`py -3.14`);
- Node.js 24;
- Liquibase 5 nel `PATH` e Java 17+ in `JAVA_HOME`, solo per `init-db.ps1`.

Copiare `.env.example` in `.env` nella radice: è l'unico file di configurazione,
senza segreti reali. Il database di sviluppo è `data/arsis.db`; non collocarlo in
cartelle sincronizzate o di rete.

```powershell
cd backend
py -3.14 -m pip install -e ".[dev]"
cd ..\frontend
npm install
cd ..
```

Dopo ogni modifica di `pyproject.toml` reinstallare il backend: un `.venv` vecchio
può non avere tutte le dipendenze.

## Database

```powershell
.\scripts\init-db.ps1                     # applica il changelog e rigenera arsis/generated/
.\scripts\init-db.ps1 -ValidateOnly       # verifica il changelog senza applicarlo
.\scripts\seed-dev.ps1                    # dati dimostrativi, idempotente
```

Altre opzioni di `init-db.ps1` sono in [scripts/README.md](../../scripts/README.md).

Il seed funziona solo con `APP_ENV` `local`, `development` o `test` e crea
l'utente `responsabile@arsis.it` / `arsis-demo-password`. Su un database reale
non eseguirlo: il primo responsabile si crea dalla pagina di accesso, oppure con

```powershell
cd backend
py -3.14 -m arsis.auth.bootstrap --email "responsabile@example.it" --display-name "Responsabile"
```

che chiede la password in modo interattivo e funziona solo con `users` vuota.

### Aggiungere un changeset

1. Creare `database/changelog/changes/NNNN-descrizione.sql` (formatted SQL,
   `--changeset arsis:NNNN-...`) e aggiungerlo a `db.changelog-master.yaml`.
2. Eseguire `.\scripts\init-db.ps1`: aggiorna il database e rigenera modelli e DTO.
3. Aggiornare il numero di changeset atteso in `database/tests/verify_schema.py`.
4. Verificare con `py -3.14 .\scripts\generate_backend_schema.py --check`.

Senza Java, `arsis-migrate` applica gli stessi changeset ma non rigenera il codice.

## Avvio

Dalla radice, con Bash (Git Bash, WSL o Linux):

```bash
./run-local.sh                          # backend :8000 e Angular :4200 con hot reload
BACKEND_PORT=8080 FRONTEND_PORT=4300 ./run-local.sh
ARSIS_MODE=runtime ./run-local.sh       # compila Angular e avvia arsis-local su :8765
```

Oppure in due terminali:

```powershell
cd backend; py -3.14 -m uvicorn arsis.main:app --reload --port 8000
cd frontend; npm start
```

Il server di sviluppo Angular inoltra `/api` e `/health` al backend
(`proxy.conf.json`). Controlli: `http://localhost:8000/health/live`,
`/health/ready`, documentazione API su `/docs`.

Per provare il runtime integrato senza lo script:

```powershell
cd frontend; npm run build
cd ..\backend; arsis-local --port 8877 --no-browser
```

## Controlli prima di una PR

Gli stessi della CI:

```powershell
cd backend
py -3.14 -m ruff check src tests
py -3.14 -m mypy
py -3.14 -m pytest -q
cd ..\frontend
npm run build
```

Su Windows, se i test dei backup falliscono per percorsi troppo lunghi, usare una
cartella temporanea corta: `pytest --basetemp=C:/tmp/pt`.

## Stile

- Colori, font, spaziature, raggi, ombre e transizioni stanno solo in
  `frontend/src/styles/tokens.css` ([design tokens](../riferimenti/design-tokens.md)).
- Ruff `check` è obbligatorio; `format` non è ancora applicato a tutto il codice
  (vedi [TODO](../TODO.md)): formattare solo i file nuovi.
- Messaggi di commit in stile Conventional Commits (`feat(area): …`).
