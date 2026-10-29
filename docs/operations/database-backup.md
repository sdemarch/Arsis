# Backup e ripristino SQLite

Il backend espone due funzioni in `arsis.core.database_backup`:

- `backup_database(destination)` esporta uno snapshot consistente del database;
- `restore_database(backup)` valida e reimporta uno snapshot esportato.

Entrambe restituiscono il percorso assoluto del file scritto e sollevano
`DatabaseBackupError` in caso di errore. Il backup usa l'API online di SQLite:
non bisogna copiare direttamente `arsis.db`, perché le modifiche già confermate
potrebbero trovarsi ancora nel file WAL.

## Esempio

```python
from pathlib import Path

from arsis.core.database_backup import backup_database, restore_database
from arsis.core.database import dispose_database_engine

exported = backup_database(Path("D:/backup/arsis-2026-10-14.db"))

# Il ripristino è un'operazione di manutenzione: bloccare prima le richieste.
dispose_database_engine()
restore_database(exported)
```

## Regole operative per il ripristino

1. Mettere l'applicazione in manutenzione e impedire nuove scritture.
2. Conservare separatamente un backup dello stato corrente.
3. Chiamare `dispose_database_engine()` per chiudere le connessioni del processo.
4. Eseguire `restore_database(...)`.
5. Riavviare l'applicazione e verificare `/health/ready`.

Il file importato viene controllato con `PRAGMA integrity_check` prima che il
database attivo sia sostituito. Se il controllo o la copia falliscono, il file
attivo non viene modificato.

Per un salvataggio completo e trasferibile dell'applicazione, incluso il futuro
contenuto della cartella allegati, usare invece il formato
[`.arsis-save`](portable-saves.md).
