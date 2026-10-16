# ADR 0003 — Convenzioni delle API HTTP

- Stato: accettata
- Data: 16 ottobre 2026

## Contesto

Il frontend Angular deve sostituire progressivamente i dati mock con API FastAPI.
Prima degli endpoint di dominio servono convenzioni uniformi per payload, errori,
liste, concorrenza e tracciamento, evitando decisioni diverse in ciascun modulo.

## Decisione

### Contratto JSON

- Gli endpoint applicativi restano sotto `/api/v1`.
- Nomi di proprietà e parametri usano `snake_case`, coerentemente con Python e
  con lo schema SQLite.
- Gli identificativi pubblici sono UUID rappresentati come stringhe.
- I timestamp sono ISO 8601 con fuso orario e vengono normalizzati in UTC; la
  forma canonica termina con `Z`.
- I DTO pubblici derivano da `ApiModel`. I DTO generati dallo schema restano un
  dettaglio di persistenza e non costituiscono automaticamente il contratto HTTP.

### Errori

Ogni errore usa la struttura:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Risorsa non trovata: Persona",
    "details": {},
    "request_id": "7d248d4f-5c50-43ff-ac23-7dc3d0909856"
  }
}
```

Gli errori inattesi restituiscono un messaggio generico; dettagli e stack trace
rimangono soltanto nei log server. Gli errori di validazione FastAPI vengono
normalizzati nello stesso envelope.

### Correlazione

Ogni risposta include `X-Request-ID`. Un identificativo client valido viene
preservato, altrimenti il backend genera un UUID. Lo stesso valore è disponibile
nei log e negli eventi di audit creati durante la richiesta.

### Liste

- `page` parte da 1 e vale 1 per impostazione predefinita.
- `page_size` vale 25 e non può superare 100.
- Le risposte contengono `items` e `meta` con pagina, dimensione, totale elementi
  e totale pagine.
- `sort=campo` indica ordine crescente; `sort=-campo` indica ordine decrescente.
- Ogni endpoint dichiara esplicitamente i campi ordinabili.

### Transazioni e concorrenza

- I servizi delimitano esplicitamente le transazioni; la dependency della sessione
  non esegue commit impliciti e annulla eventuali transazioni incomplete.
- Le scritture registrano l'audit nella stessa transazione del dato di dominio.
- Le modifiche inviano la `version` letta dal client.
- L'update SQL verifica atomicamente identificativo e versione, poi incrementa la
  versione. Un valore superato produce `409 STALE_VERSION`; un identificativo
  assente produce `404 RESOURCE_NOT_FOUND`.

### OpenAPI

Gli operation ID sono deterministici nella forma `{tag}_{nome_funzione}`. I modelli
di errore e paginazione sono riutilizzabili da tutti i router di dominio.

## Conseguenze

Il frontend può implementare una sola gestione trasversale per errori, liste e
request ID. I repository devono usare l'helper di aggiornamento versionato e i
servizi devono aprire esplicitamente la transazione. Cambiare in futuro la
convenzione JSON richiederà una nuova versione API o un layer di compatibilità.
