# Piano — Attività ricorrenti

Stato: implementato sul branch `feature/attivita-ricorrenti`.

## Obiettivo

Configurare un'attività come **ricorrente** (es. la prova del martedì e del venerdì) invece
di crearla a mano ogni volta.

## Decisioni

| Tema | Decisione |
|---|---|
| Modello | Una **serie** conserva la regola; ogni ricorrenza è un'attività ordinaria collegata (`series_id`), con presenze, rimborsi e obiettivi propri. |
| Regole | **Settimanale** su uno o più giorni, ogni N settimane (1–12); **mensile** sullo stesso giorno del mese, ogni N mesi (i mesi senza quel giorno sono saltati). |
| Fine | Data di fine obbligatoria; al massimo un anno e 200 attività per serie. |
| Date e fuso | Il backend calcola le **date** (aritmetica di calendario, nessun fuso). Il browser trasforma ogni data in mezzanotte locale con il proprio scostamento (ora legale inclusa) e il backend verifica che le date coincidano con la regola. |
| Anteprima | La pagina di creazione mostra le date generate prima di salvare. |
| Modifica | Una ricorrenza si modifica da sola, oppure «anche le successive»: titolo, tipo, luogo, dettaglio, stato e note (mai la data). Il cambio di tipo o luogo chiede conferma per ricalcolare i rimborsi già registrati, come per una singola attività. |
| Interruzione | «Interrompi la serie dopo questa» archivia le ricorrenze successive **senza presenze registrate**; quelle con presenze restano. La data di fine della serie diventa l'ultima ricorrenza rimasta. |

## Regola (RB-22)

Le date di una serie sono quelle prodotte dalla regola tra la prima data e la data di fine
incluse; ogni ricorrenza è un'attività indipendente. Interrompere una serie non archivia
mai un'attività con presenze registrate.

## Modello dati (changeset `0014-activity-series`)

- `activity_series`: `frequency`, `interval_count`, `weekdays` (ISO `1`–`7`, solo
  settimanale), `starts_on`, `ends_on`, audit, versione.
- `activities.series_id` (facoltativo) con indice `(series_id, starts_at)`.
- Il generatore di codice tratta «series» come invariabile (`ActivitySeries`).

## API

| Metodo | Percorso | Scopo |
|---|---|---|
| POST | `/activities/series/preview` | Date e descrizione della regola. |
| POST | `/activities/series` | Crea la serie con un timestamp per ogni data dell'anteprima. |
| GET | `/activities/series/{id}` | Regola e ricorrenze attive. |
| PATCH | `/activities/{id}/following` | Stesse modifiche a questa ricorrenza e alle successive. |
| POST | `/activities/{id}/end-series` | Archivia le successive senza presenze. |

Ogni `ActivityResponse` riporta `series_id` e `series` (descrizione, posizione e numero di
ricorrenze).

## Verifiche

- Test unitari della regola (settimanale, intervalli, mensile con giorni mancanti, limiti)
  e test API; prova sul database migrato di una serie a cavallo del cambio dell'ora legale.

## Possibili evoluzioni

- Prolungare una serie oltre la data di fine.
- Spostare in blocco la data delle ricorrenze successive.
