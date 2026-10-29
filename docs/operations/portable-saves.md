# Salvataggi portabili Arsis

Un salvataggio dell'app usa l'estensione `.arsis-save`. È un archivio versionato,
non una copia diretta del file SQLite, e contiene:

- `manifest.json`: formato, versione, data di creazione e checksum;
- `database.sqlite`: snapshot coerente del database;
- `attachments/`: eventuali allegati locali.

Il formato consente di spostare l'intero stato dell'app tra installazioni locali
compatibili. Il segreto dell'applicazione non viene incluso nel salvataggio.

## Operazioni di base

Le funzioni sono deliberate primitive di runtime: l'interfaccia utente e il futuro
launcher dovranno chiamarle, senza esporre il ripristino come endpoint HTTP.

```python
from pathlib import Path

from arsis.core.database import dispose_database_engine
from arsis.core.saves import create_save, inspect_save, restore_save

save = create_save(
    Path("D:/backup/arsis.arsis-save"),
    database_path=Path("C:/ProgramData/Arsis/arsis.db"),
    attachments_dir=Path("C:/ProgramData/Arsis/attachments"),
)
inspect_save(save)

# Prima dell'import: fermare il backend e tutte le scritture.
dispose_database_engine()
restore_save(
    save,
    database_path=Path("C:/ProgramData/Arsis/arsis.db"),
    attachments_dir=Path("C:/ProgramData/Arsis/attachments"),
)
```

L'import controlla estensione, manifest, checksum e `PRAGMA integrity_check`
prima di sostituire il database. Il launcher dovrà creare un salvataggio
pre-import, sostituire i dati in modalità manutenzione e riavviare l'app.

## Percorsi runtime

In sviluppo i dati restano in `data/` nel repository. In un eseguibile congelato,
se `ARSIS_DATA_DIR` non è impostata, Arsis usa `%LOCALAPPDATA%\Arsis`; quindi il
database non viene scritto accanto al binario sotto `Program Files`.
