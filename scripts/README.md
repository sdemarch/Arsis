# Script

Questa cartella contiene automazioni ripetibili per sviluppo, CI e operazioni. Gli script non incorporano segreti.

## Inizializzazione database

Da PowerShell, nella radice del repository:

```powershell
.\scripts\init-db.ps1
```

Lo script crea il file SQLite locale, installa il driver JDBC nella cartella del progetto quando manca e applica tutti i changeset Liquibase ancora mancanti. Non richiede Docker, PostgreSQL o un servizio database. Comandi aggiuntivi:

```powershell
# Verifica il changelog senza applicarlo
.\scripts\init-db.ps1 -ValidateOnly

# Usa un percorso database specifico
.\scripts\init-db.ps1 -DatabasePath C:\ProgramData\Arsis\data\arsis.db

# Non tentare il download del driver se è assente
.\scripts\init-db.ps1 -SkipDriverInstall
```

`liquibase update` è idempotente: le esecuzioni successive applicano soltanto i changeset non ancora registrati.

Per controllare che tutte le tabelle attese siano presenti:

```powershell
python .\database\tests\verify_schema.py .\data\arsis.db
```
