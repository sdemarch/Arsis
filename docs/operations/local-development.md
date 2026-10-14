# Sviluppo locale

La configurazione locale parte dall'unico file `.env.example` nella radice del
repository. Copiarlo in `.env` e non inserire segreti reali nel repository.

Il backend autorevole è il package `backend/src/arsis`; non sono previsti Alembic,
un secondo file requirements o configurazioni ambiente specifiche delle singole
cartelle.

## Installazione

Prerequisiti:

- Python 3.14;
- Node.js 24;
- Liquibase 5 disponibile nel `PATH`;
- Java 17 o superiore configurato tramite `JAVA_HOME`.

```powershell
cd backend
py -3.14 -m pip install -e ".[dev]"
cd ..\frontend
npm install
cd ..
```

Le migrazioni vengono eseguite separatamente dal backend, senza Docker:

```powershell
.\scripts\init-db.ps1
```

Per inserire i dati dimostrativi coerenti con le schermate Angular:

```powershell
.\scripts\seed-dev.ps1
```

Il seed può essere eseguito più volte: usa identificativi deterministici e aggiorna
gli stessi record senza crearne duplicati. Non viene eseguito in ambienti diversi
da `local`, `development` e `test`.

Per verificare i changelog senza applicarli:

```powershell
.\scripts\init-db.ps1 -ValidateOnly
```

Il database di sviluppo predefinito è `data/arsis.db`. Non collocarlo in una cartella sincronizzata o condivisa in rete.

## Avvio

In due terminali separati:

```powershell
cd backend
py -3.14 -m uvicorn arsis.main:app --reload --port 8000
```

```powershell
cd frontend
npm start
```
