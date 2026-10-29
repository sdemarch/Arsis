# Script

Questa cartella contiene automazioni ripetibili per sviluppo, CI e operazioni. Gli script non incorporano segreti.

## Inizializzazione database

Liquibase 5 richiede Java 17 o superiore. Lo script interrompe subito
l'esecuzione con un messaggio esplicito se `java` non è disponibile o se la
versione attiva è precedente.

Da PowerShell, nella radice del repository:

```powershell
.\scripts\init-db.ps1
```

Lo script crea il file SQLite locale, installa il driver JDBC nella cartella del progetto quando manca, applica tutti i changeset Liquibase ancora mancanti e rigenera i modelli SQLAlchemy e i DTO Pydantic. Non richiede Docker, PostgreSQL o un servizio database. Comandi aggiuntivi:

```powershell
# Verifica il changelog senza applicarlo
.\scripts\init-db.ps1 -ValidateOnly

# Usa un percorso database specifico
.\scripts\init-db.ps1 -DatabasePath C:\ProgramData\Arsis\data\arsis.db

# Non tentare il download del driver se è assente
.\scripts\init-db.ps1 -SkipDriverInstall

# Aggiorna il database senza rigenerare il codice backend
.\scripts\init-db.ps1 -SkipCodeGeneration
```

`liquibase update` è idempotente: le esecuzioni successive applicano soltanto i changeset non ancora registrati.

## Dati dimostrativi

Dopo avere installato il backend in modalità editable e inizializzato il database:

```powershell
.\scripts\seed-dev.ps1
```

Per usare un database di test differente:

```powershell
.\scripts\seed-dev.ps1 -DatabasePath .\data\arsis-test.db
```

Il comando inserisce o aggiorna un insieme deterministico di persone, ruoli,
cataloghi, corsi, iscrizioni, lezioni e attività coerente con i mock Angular. È
idempotente e rifiuta l'esecuzione fuori dagli ambienti di sviluppo e test.

## Modelli SQLAlchemy e DTO Pydantic

I file in `backend/src/arsis/generated/` derivano dal database migrato e non vanno
modificati a mano. Per rigenerarli separatamente:

```powershell
py -3.14 .\scripts\generate_backend_schema.py
```

Per verificare che i file versionati siano allineati senza modificarli:

```powershell
py -3.14 .\scripts\generate_backend_schema.py --check
```

Liquibase resta l'unica fonte autorizzata a creare o modificare lo schema. I modelli
generati non devono essere usati con `Base.metadata.create_all()`. Eventuali DTO API
con validazioni o campi esposti differenti vanno definiti nei rispettivi moduli
funzionali, eventualmente riutilizzando i DTO di persistenza generati.

Per controllare che tutte le tabelle attese siano presenti:

```powershell
python .\database\tests\verify_schema.py .\data\arsis.db
```
