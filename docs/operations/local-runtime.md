# Runtime locale

`arsis-local` avvia un solo processo FastAPI su `127.0.0.1:8765`, serve la SPA
Angular compilata e apre il browser predefinito. API e frontend hanno quindi la
stessa origine: non serve Node.js in esecuzione né CORS per l'installazione locale.

## Prova dal repository

Inizializzare il database, compilare Angular e avviare il comando dal package
backend già installato:

```powershell
.\scripts\init-db.ps1
Set-Location frontend
npm run build
Set-Location ..\backend
arsis-local
```

Il frontend di sviluppo compilato è cercato in
`frontend/dist/arsis/browser`. Per non aprire il browser, oppure per scegliere una
porta, usare:

```powershell
arsis-local --port 8877 --no-browser
```

Il binding predefinito è esclusivamente loopback. Il sistema operativo impedisce
una seconda istanza sulla stessa porta; un futuro launcher mostrerà una finestra
chiara quando l'app risulta già aperta.

## Layout dell'eseguibile

Il packaging dovrà includere il contenuto della build Angular nella directory
read-only `frontend/` accanto alle risorse dell'app. Quando il programma è un exe,
il database e i salvataggi non vengono invece collocati lì: senza
`ARSIS_DATA_DIR` usano `%LOCALAPPDATA%\Arsis`.

Prima del packaging restano da aggiungere l'inizializzazione/migrazione del
database e il flusso manutenzione per l'import dei salvataggi.
