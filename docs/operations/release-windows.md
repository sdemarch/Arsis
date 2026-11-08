# Rilascio Windows

Arsis si distribuisce come cartella `Arsis\` con `Arsis.exe` (PyInstaller) e,
facoltativamente, come installer `Arsis-Setup-<versione>.exe` (Inno Setup 6).

## Build

Prerequisiti: Python 3.14, Node.js 24; per l'installer anche Inno Setup 6
(`winget install JRSoftware.InnoSetup`). Java e Liquibase **non** servono.

```powershell
.\scripts\build-windows.ps1                 # frontend + exe + installer
.\scripts\build-windows.ps1 -SkipFrontend   # riusa frontend\dist
.\scripts\build-windows.ps1 -SkipInstaller  # solo build\pyinstaller\dist\Arsis
```

La versione è quella di `backend/pyproject.toml`. Lo script usa un ambiente
isolato in `build\venv`; tutta la cartella `build\` è ignorata da git.

Il bundle contiene, in sola lettura, la build Angular (`frontend\`) e il
changelog Liquibase (`database\changelog\`). Non contiene dati utente.

## Dati dell'installazione

Tutto ciò che appartiene all'utente sta in `%LOCALAPPDATA%\Arsis`
(oppure in `ARSIS_DATA_DIR`):

| Percorso | Contenuto |
|---|---|
| `arsis.db` | database SQLite |
| `backups\pre-migrazione-*.db` | copia automatica prima di ogni aggiornamento dello schema |
| `secret.key` | chiave di firma dei token, generata al primo avvio |
| `logs\arsis.log` | output del programma (l'exe non ha console) |

Installazione, aggiornamento e disinstallazione non toccano questa cartella.

## Primo avvio

1. `Arsis.exe` crea il database applicando il changelog e apre il browser su
   `http://127.0.0.1:8765`.
2. Senza utenti, la pagina di accesso chiede di creare il **primo
   responsabile** (nome, email, password di almeno 12 caratteri).
3. Gli altri responsabili si aggiungono da Configurazioni.

`arsis-bootstrap-admin` resta disponibile per chi lavora da riga di comando.

## Aggiornamento

Eseguire l'installer della nuova versione: sostituisce i file del programma
(chiedendo di chiudere Arsis se è aperto) e lascia i dati dove sono. Al primo
avvio successivo Arsis:

1. confronta il changelog incluso con la tabella `DATABASECHANGELOG`;
2. se ci sono changeset nuovi, copia il database in `backups\`;
3. applica ogni changeset in una transazione propria.

Se un changeset fallisce, quel changeset viene annullato, Arsis mostra il
messaggio d'errore e non parte; il backup permette di tornare indietro. Un
database aggiornato da una versione **più recente** viene rifiutato: non
installare versioni precedenti sopra dati più nuovi.

Il migratore (`arsis.core.migrations`, comando `arsis-migrate`) scrive nella
stessa tabella di Liquibase: in sviluppo `scripts\init-db.ps1` continua a
funzionare sugli stessi database e completa i checksum lasciati vuoti.

## Avvio e problemi comuni

| Situazione | Comportamento |
|---|---|
| Arsis già aperto | il secondo avvio apre solo il browser sull'istanza esistente |
| Porta 8765 occupata da un altro programma | finestra di errore; avviare con `Arsis.exe --port 8877` |
| Migrazione non riuscita | finestra con il motivo e la cartella dei backup |
| Troppi accessi falliti | 5 tentativi per account o 20 per indirizzo in 15 minuti, poi attesa |

Per diagnosi: `%LOCALAPPDATA%\Arsis\logs\arsis.log`.

## Verifica prima di un rilascio

Su un PC (o una macchina virtuale) senza Python né Node:

1. installare, verificare primo avvio e creazione del responsabile;
2. inserire qualche dato, installare sopra una build con un changeset nuovo e
   controllare backup in `backups\` e dati conservati;
3. avviare due volte, e con la porta occupata;
4. disinstallare e verificare che `%LOCALAPPDATA%\Arsis` sia ancora presente.
