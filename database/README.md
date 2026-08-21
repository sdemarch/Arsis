# Database Arsis

Il database applicativo è SQLite e lo schema è gestito esclusivamente tramite
Liquibase. I changelog presenti in `database/changelog/` sono la fonte ufficiale
della struttura dati.

I modelli SQLAlchemy e i DTO Pydantic non devono essere mantenuti manualmente:
vengono generati dal database dopo l'applicazione delle migrazioni.

## Aggiornare lo schema

1. Creare un nuovo changeset Liquibase in
   `database/changelog/changes/`.
2. Registrarlo in `database/changelog/db.changelog-master.yaml`.
3. Dalla radice del progetto eseguire:

   ```powershell
   .\scripts\init-db.ps1
   ```

Il comando:

1. crea `data/arsis.db` quando non esiste;
2. installa localmente il driver JDBC SQLite quando manca;
3. esegue `liquibase update`;
4. rigenera i modelli SQLAlchemy;
5. rigenera i DTO Pydantic.

L'esecuzione è idempotente: Liquibase applica soltanto i changeset non ancora
registrati.

## Codice backend generato

I file prodotti sono:

- `backend/src/arsis/generated/models.py`: modelli SQLAlchemy;
- `backend/src/arsis/generated/schemas.py`: DTO Pydantic di creazione,
  aggiornamento e lettura;
- `backend/src/arsis/generated/__init__.py`: esportazioni comuni.

Questi file riportano un fingerprint dello schema e non vanno modificati a mano.
Le modifiche manuali verrebbero sovrascritte alla generazione successiva.

Liquibase rimane l'unico proprietario dello schema: non utilizzare
`Base.metadata.create_all()`.

I modelli generati comprendono colonne e chiavi esterne rilevabili da SQLite.
Relazioni ORM, comportamenti applicativi e regole di dominio non deducibili dal
database devono essere definiti in moduli separati.

I DTO generati rappresentano il livello di persistenza. I DTO pubblici delle API
possono comporli o estenderli, ma devono definire separatamente autorizzazioni,
campi esposti e validazioni di dominio.

## Generazione manuale

Per rigenerare il codice senza eseguire Liquibase:

```powershell
py -3.14 .\scripts\generate_backend_schema.py
```

Per usare un database differente:

```powershell
py -3.14 .\scripts\generate_backend_schema.py --database C:\ProgramData\Arsis\data\arsis.db
```

Per aggiornare il database senza rigenerare il codice:

```powershell
.\scripts\init-db.ps1 -SkipCodeGeneration
```

Questa opzione è destinata soltanto a casi operativi particolari e non al normale
flusso di sviluppo.

## Controlli

Verificare che changelog e database siano validi:

```powershell
.\scripts\init-db.ps1 -ValidateOnly
py -3.14 .\database\tests\verify_schema.py .\data\arsis.db
```

Verificare che modelli e DTO versionati siano aggiornati:

```powershell
py -3.14 .\scripts\generate_backend_schema.py --check
```

Il comando termina con un codice di errore se almeno un file generato non
corrisponde allo schema corrente, quindi può essere utilizzato anche in CI.

## Flusso da versionare

Ogni modifica strutturale deve essere committata includendo insieme:

1. il nuovo changeset Liquibase;
2. l'aggiornamento del changelog master;
3. i modelli SQLAlchemy rigenerati;
4. i DTO Pydantic rigenerati;
5. gli eventuali test interessati.
