# Runtime locale

`arsis-local` avvia un solo processo FastAPI su `127.0.0.1:8765`, serve la SPA
Angular compilata e apre il browser predefinito. API e frontend hanno quindi la
stessa origine: non serve Node.js in esecuzione né CORS per l'installazione locale.

## Prova dal repository

Compilare Angular e avviare il comando dal package backend già installato:

```powershell
Set-Location frontend
npm run build
Set-Location ..\backend
arsis-local
```

Oppure, dalla radice: `ARSIS_MODE=runtime ./run-local.sh`.

Il frontend di sviluppo compilato è cercato in
`frontend/dist/arsis/browser`. Per non aprire il browser, oppure per scegliere una
porta, usare:

```powershell
arsis-local --port 8877 --no-browser
```

## Cosa fa all'avvio

1. Se la chiave di firma configurata è ancora quella d'esempio, usa (o crea)
   `secret.key` nella cartella dati.
2. Se sulla porta risponde già Arsis, apre solo il browser ed esce; se la porta
   è occupata da altro, segnala l'errore.
3. Applica le migrazioni mancanti al database, con backup preventivo in
   `backups\` (vedi `arsis-migrate`).
4. Serve API e frontend; il browser si apre dopo un istante.

Gli errori bloccanti compaiono in una finestra nell'exe e su stderr altrimenti.
Il binding predefinito è esclusivamente loopback.

## Layout dell'eseguibile

L'exe include in sola lettura la build Angular (`frontend\`) e il changelog
(`database\changelog\`). Il database, i backup, la chiave e i log non vengono
collocati lì: senza `ARSIS_DATA_DIR` usano `%LOCALAPPDATA%\Arsis`.
Build, installazione e aggiornamento: [Rilascio Windows](release-windows.md).

Resta da aggiungere il flusso manutenzione per esportare/importare i salvataggi
`.arsis-save` dall'interfaccia.
