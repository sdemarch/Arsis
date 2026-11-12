# Rilascio Windows

Arsis si distribuisce come cartella `Arsis\` con `Arsis.exe` (PyInstaller) e come
installer `Arsis-Setup-<versione>.exe` (Inno Setup 6, per utente, senza diritti
di amministratore).

## Build

Prerequisiti: Python 3.14, Node.js 24 e, per l'installer, Inno Setup 6
(`winget install JRSoftware.InnoSetup`). Java e Liquibase **non** servono.

```powershell
.\scripts\build-windows.ps1                 # frontend + exe + installer
.\scripts\build-windows.ps1 -SkipFrontend   # riusa frontend\dist
.\scripts\build-windows.ps1 -SkipInstaller  # solo build\pyinstaller\dist\Arsis
```

La versione è quella di `backend/pyproject.toml`. Lo script usa un ambiente
isolato in `build\venv`; `build\` è ignorata da git. Il bundle contiene in sola
lettura la build Angular (`frontend\`) e il changelog (`database\changelog\`),
nessun dato utente. File di packaging: `packaging/launcher.py`,
`packaging/arsis.spec`, `packaging/arsis.iss`.

## Pubblicare una versione

1. **Preparare `master`.** Unire le PR in `dev`, poi `dev` → `master` con la CI
   verde; `git switch master; git pull`.
2. **Versione** `MAJOR.MINOR.PATCH`: `PATCH` per le correzioni, `MINOR` per
   funzioni nuove o changeset, `MAJOR` per modifiche incompatibili. Aggiornarla in
   `backend/pyproject.toml` **e** `frontend/package.json`, poi
   `git commit -am "chore(release): vX.Y.Z"; git push`.
3. **Build pulita locale (per il collaudo):**

   ```powershell
   Remove-Item -Recurse -Force build\pyinstaller, build\installer -ErrorAction SilentlyContinue
   .\scripts\build-windows.ps1
   ```

   Risultato: `build\installer\Arsis-Setup-X.Y.Z.exe`.
4. **Collaudo** su un PC o una macchina virtuale **senza** Python né Node:
   - [ ] installazione nuova: si apre il browser e compare "Crea il primo responsabile";
   - [ ] aggiornamento: installare la versione precedente, inserire dati, installare
         la nuova; i dati restano e, se ci sono changeset nuovi, compare
         `backups\pre-migrazione-*.db`;
   - [ ] salvataggi: esportare, modificare un dato, importare il file; il dato torna
         com'era e compare `backups\pre-import-*.arsis-save`;
   - [ ] secondo avvio con Arsis aperto: si apre solo il browser;
   - [ ] porta 8765 occupata da un altro programma: finestra d'errore;
   - [ ] disinstallazione: `%LOCALAPPDATA%\Arsis` resta presente.
5. **Pubblicare:** creare su GitHub una Release con il tag `vX.Y.Z` e le note
   della versione. Il workflow [Release Windows installer](../../.github/workflows/release.yml)
   si avvia alla creazione della Release: esegue la build su Windows e allega
   automaticamente `Arsis-Setup-X.Y.Z.exe`. Non caricare manualmente l'eseguibile
   né versionarlo nel repository.
6. **Comunicare agli utenti:**

   > Scaricare `Arsis-Setup-X.Y.Z.exe` ed eseguirlo, anche sopra la versione già
   > installata. Se Arsis è aperto, l'installer chiede di chiuderlo. Al primo avvio
   > Arsis aggiorna da solo i dati, dopo averne fatto una copia di sicurezza.

   L'installer non è firmato: Windows può mostrare SmartScreen, "Ulteriori
   informazioni" → "Esegui comunque".

## Installazione

I dati stanno in `%LOCALAPPDATA%\Arsis` (o `ARSIS_DATA_DIR`), descritti in
[Architettura §3.3](../ARCHITETTURA.md#33-cartella-dati). Installazione,
aggiornamento e disinstallazione non li toccano.

**Primo avvio:** `Arsis.exe` crea il database dal changelog e apre
`http://127.0.0.1:8765`; senza utenti la pagina di accesso chiede di creare il
primo responsabile (password di almeno 12 caratteri). Gli altri si aggiungono da
Configurazioni.

**Aggiornamento:** l'installer sostituisce i file del programma. Al primo avvio
Arsis confronta il changelog con `DATABASECHANGELOG`, copia il database in
`backups\` se ci sono changeset nuovi e li applica uno per transazione. Se uno
fallisce viene annullato, Arsis mostra il motivo e non parte.

## Problemi comuni

| Situazione | Comportamento |
|---|---|
| Arsis già aperto | il secondo avvio apre solo il browser |
| Porta 8765 occupata | finestra d'errore; avviare con `Arsis.exe --port 8877` |
| Migrazione non riuscita | finestra con il motivo e la cartella dei backup |
| Database di una versione più recente | Arsis lo rifiuta: non installare versioni precedenti sopra dati più nuovi |
| Troppi accessi falliti | 5 per account o 20 per indirizzo in 15 minuti, poi attesa |

Log: `%LOCALAPPDATA%\Arsis\logs\arsis.log`.

### Tornare alla versione precedente

1. Chiudere Arsis.
2. Copiare l'ultimo `backups\pre-migrazione-*.db` sopra `%LOCALAPPDATA%\Arsis\arsis.db`.
3. Reinstallare la versione precedente dalla pagina Releases.
