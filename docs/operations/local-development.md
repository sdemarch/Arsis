# Sviluppo locale

La configurazione locale parte da `.env.example`. Non inserire segreti reali nel repository.

Le migrazioni vengono eseguite separatamente dal backend, senza Docker:

```powershell
.\scripts\init-db.ps1
```

Per verificare i changelog senza applicarli:

```powershell
.\scripts\init-db.ps1 -ValidateOnly
```

Il database di sviluppo predefinito è `data/arsis.db`. Non collocarlo in una cartella sincronizzata o condivisa in rete.
