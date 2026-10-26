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

Il seed configura anche l'utente dimostrativo:

- email: `responsabile@arsis.it`;
- password: `arsis-demo-password`.

Su un database reale non eseguire il seed. Dopo le migrazioni crea il primo
responsabile con il comando locale interattivo (la password non compare negli
argomenti né nella cronologia della shell):

```powershell
cd backend
py -3.14 -m arsis.auth.bootstrap `
  --email "responsabile@example.it" `
  --display-name "Responsabile"
```

Il bootstrap funziona soltanto quando la tabella `users` è vuota. Login, refresh,
logout e profilo corrente sono esposti sotto `/api/v1/auth`; il refresh token è
gestito esclusivamente tramite cookie HttpOnly.

Per verificare i changelog senza applicarli:

```powershell
.\scripts\init-db.ps1 -ValidateOnly
```

Il database di sviluppo predefinito è `data/arsis.db`. Non collocarlo in una cartella sincronizzata o condivisa in rete.

## Avvio

Con Bash (Git Bash, WSL o Linux) è disponibile uno script unico dalla radice:

```bash
chmod +x run-local.sh
./run-local.sh
```

Accetta facoltativamente `BACKEND_PORT` e `FRONTEND_PORT`, ad esempio
`BACKEND_PORT=8080 FRONTEND_PORT=4300 ./run-local.sh`.

In alternativa, avviare i due processi in terminali separati:

```powershell
cd backend
py -3.14 -m uvicorn arsis.main:app --reload --port 8000
```

```powershell
cd frontend
npm start
```
