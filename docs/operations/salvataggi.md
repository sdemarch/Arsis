# Salvataggi e backup

Arsis ha due livelli di copia dei dati:

| | `.arsis-save` | Snapshot SQLite |
|---|---|---|
| Contenuto | database + allegati + manifest | solo database |
| Uso | backup dell'utente, trasferimento su un altro PC | copia automatica prima di migrazioni e import |
| Modulo | `arsis.core.saves` | `arsis.core.database_backup` |

Non copiare mai `arsis.db` a mano mentre Arsis è aperto: le modifiche confermate
possono essere ancora nel file WAL. Entrambi i livelli usano l'API di backup
online di SQLite e controllano `PRAGMA integrity_check`.

## Formato `.arsis-save`

Archivio zip versionato (`format_version` 1) che contiene:

- `manifest.json`: formato, versione, data di creazione, checksum SHA-256 del
  database, numero di allegati;
- `database.sqlite`: snapshot coerente;
- `attachments/`: allegati della cartella dati.

La chiave di firma (`secret.key`) non è inclusa.

## Dall'interfaccia

Configurazioni → **Salvataggi**:

- **Esporta** scarica `arsis-AAAAMMGG-HHMM.arsis-save`.
- **Importa** verifica il file e ne mostra il contenuto (data, organizzazione,
  conteggi). Dopo la conferma con la password sostituisce **tutti** i dati; poi
  si accede con le credenziali presenti nel salvataggio.

| Metodo | Percorso | Effetto |
|---|---|---|
| `GET` | `/api/v1/maintenance/saves/export` | scarica un salvataggio dei dati attuali |
| `POST` | `/api/v1/maintenance/saves/inspect` | valida il file (multipart `file`) e lo riassume |
| `POST` | `/api/v1/maintenance/saves/import` | sostituisce i dati (multipart `file` e `password`) |

L'import, in ordine:

1. rifiuta file non validi (`INVALID_SAVE`) o creati da una versione più recente
   (`SAVE_FROM_NEWER_VERSION`) senza toccare i dati; password errata:
   `PASSWORD_MISMATCH`;
2. entra in modalità manutenzione: attende la fine delle altre richieste (30 s,
   poi `409 MAINTENANCE_BUSY`) e risponde `503 MAINTENANCE_IN_PROGRESS` alle nuove;
3. salva i dati attuali in `backups\pre-import-<data>.arsis-save`;
4. chiude le connessioni, sostituisce database e allegati, applica le migrazioni
   mancanti (salvataggi di versioni precedenti);
5. se un passo fallisce ripristina il backup e risponde `SAVE_IMPORT_FAILED`;
6. revoca token e cookie di sessione emessi prima dell'import.

Il processo non si riavvia: il motore del database si ricrea alla richiesta
successiva. La revoca dei token vive in memoria: un riavvio entro 15 minuti
dall'import la azzera, ma un token vale solo per un ID utente attivo nei nuovi dati.

## Da Python

```python
from pathlib import Path

from arsis.core.database import dispose_database_engine
from arsis.core.database_backup import backup_database
from arsis.core.saves import create_save, inspect_save, restore_save

data = Path("C:/Users/<utente>/AppData/Local/Arsis")
save = create_save(
    Path("D:/backup/arsis.arsis-save"),
    database_path=data / "arsis.db",
    attachments_dir=data / "attachments",
)
inspect_save(save)                       # manifest, dopo checksum e integrity check
backup_database(Path("D:/backup/arsis.db"), database_path=data / "arsis.db")

# Ripristino: solo ad applicazione ferma o in modalità manutenzione.
dispose_database_engine()
restore_save(save, database_path=data / "arsis.db", attachments_dir=data / "attachments")
```

`restore_save` e `restore_database` sostituiscono il file solo dopo i controlli;
se falliscono il database attivo resta invariato.
