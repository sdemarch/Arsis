# Rilasciare l'installer — guida rapida

Procedura passo passo per pubblicare `Arsis-Setup-<versione>.exe`.
Dettagli su dati, aggiornamenti e problemi: [Rilascio Windows](release-windows.md).

## 0. Una tantum

```powershell
winget install JRSoftware.InnoSetup   # compilatore dell'installer
gh auth login                         # per pubblicare la release su GitHub
```

Servono anche Python 3.14 e Node.js 24. Java e Liquibase non servono.

## 1. Preparare `master`

1. Unire le PR in `dev`, poi `dev` → `master`, con la **CI verde**.
2. Aggiornarsi: `git switch master; git pull`.
3. Se la release introduce changeset Liquibase, verificarli prima in sviluppo
   con `.\scripts\init-db.ps1`.

## 2. Scegliere la versione

Numerazione `MAJOR.MINOR.PATCH`:
`PATCH` per le correzioni, `MINOR` per le funzioni nuove o i nuovi changeset,
`MAJOR` per le modifiche incompatibili.

Aggiornare **entrambi** i file con lo stesso numero:

- `backend/pyproject.toml` → `version = "X.Y.Z"` (letto dallo script di build);
- `frontend/package.json` → `"version": "X.Y.Z"`.

```powershell
git commit -am "chore(release): vX.Y.Z"
git push
```

## 3. Build

Da una copia pulita, rimuovendo la build precedente:

```powershell
Remove-Item -Recurse -Force build\pyinstaller, build\installer -ErrorAction SilentlyContinue
.\scripts\build-windows.ps1
```

Risultato: `build\installer\Arsis-Setup-X.Y.Z.exe`.
Se manca, controllare che Inno Setup sia installato (lo script lo segnala).

## 4. Collaudo (obbligatorio)

Su un PC o una macchina virtuale **senza** Python né Node:

- [ ] **Installazione nuova:** si apre il browser e compare "Crea il primo
      responsabile"; dopo la creazione si accede.
- [ ] **Aggiornamento:** installare la versione precedente, inserire qualche
      dato, poi installare la nuova. I dati restano e, se ci sono changeset nuovi,
      compare un file in `%LOCALAPPDATA%\Arsis\backups\pre-migrazione-*.db`.
- [ ] **Secondo avvio:** con Arsis aperto, rilanciarlo apre solo il browser.
- [ ] **Disinstallazione:** `%LOCALAPPDATA%\Arsis` resta presente.
- [ ] In caso di problemi, leggere `%LOCALAPPDATA%\Arsis\logs\arsis.log`.

## 5. Pubblicare

```powershell
git tag vX.Y.Z
git push origin vX.Y.Z
gh release create vX.Y.Z build\installer\Arsis-Setup-X.Y.Z.exe `
  --title "Arsis X.Y.Z" --notes "Novità: ...`n`nAggiornamento: eseguire l'installer; i dati vengono conservati."
```

## 6. Comunicare agli utenti

> Scaricare `Arsis-Setup-X.Y.Z.exe` ed eseguirlo, anche sopra la versione già
> installata. Se Arsis è aperto, l'installer chiede di chiuderlo. Al primo avvio
> Arsis aggiorna da solo i dati, dopo averne fatto una copia di sicurezza.

Windows può mostrare l'avviso SmartScreen perché l'installer non è firmato:
"Ulteriori informazioni" → "Esegui comunque".

## Se qualcosa va storto

Se l'aggiornamento del database fallisce, Arsis non parte e mostra il motivo.
Per tornare alla versione precedente:

1. chiudere Arsis;
2. copiare l'ultimo `backups\pre-migrazione-*.db` sopra `%LOCALAPPDATA%\Arsis\arsis.db`;
3. reinstallare l'installer della versione precedente (dalla pagina Releases).

Non installare una versione precedente sopra un database già aggiornato:
Arsis lo rifiuta per proteggere i dati.
