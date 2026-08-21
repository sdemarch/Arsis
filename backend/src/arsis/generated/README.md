# Codice generato dal database

`models.py` contiene i modelli SQLAlchemy e `schemas.py` i DTO Pydantic di
persistenza. Entrambi sono generati dal database SQLite dopo l'applicazione delle
migrazioni Liquibase.

Non modificare questi file a mano e non usare `Base.metadata.create_all()`: Liquibase
è l'unico proprietario dello schema. Per introdurre una modifica:

1. aggiungere un changeset Liquibase;
2. eseguire `.\scripts\init-db.ps1` dalla radice del progetto;
3. versionare insieme changeset e file rigenerati.

Le relazioni ORM e le regole di dominio non deducibili dallo schema vanno aggiunte in
moduli applicativi separati. Allo stesso modo, i DTO esposti dalle API possono
estendere o comporre quelli generati senza modificarli.
