# Piano — Rimborso chilometrico e Luoghi

Stato: in sviluppo sul branch `feature/rimborsi-km`.

## Obiettivo

Oltre all'importo fisso per presenza (per tipo di attività), riconoscere agli **autisti**
un rimborso carburante calcolato sui chilometri del **luogo** dell'attività, con una
maggiorazione percentuale per passeggero, più il **pedaggio autostradale** del luogo.

## Decisioni

| Tema | Decisione |
|---|---|
| Chilometri | Registrati sul luogo, sempre **andata e ritorno**, numeri interi. |
| Pedaggio | Registrato sul luogo (A/R), in euro con due decimali, sommato al rimborso di ogni autista. Non è soggetto alla maggiorazione. |
| Passeggeri | Solo il **numero**, indicato per ciascun autista presente. |
| Maggiorazione | +N% per passeggero (intero), fino a un massimo di passeggeri conteggiati (default 4). |
| Tipi ammessi | Configurabili per tipo (prova, concerto, evento); default solo evento. |
| Importo fisso | Resta e si somma al rimborso chilometrico. |
| Configurazione | Nella stessa regola `activities.refund_rules` e nella stessa pagina dei rimborsi fissi. |
| Storicizzazione | **Snapshot**: importi e parametri vengono salvati sulla presenza quando viene registrata. Le modifiche a regole e luoghi valgono solo per le registrazioni successive. Vale anche per l'importo fisso. |

## Regola di calcolo (RB-18)

```
base       = km_luogo × €/km
maggioraz. = min(passeggeri, max_passeggeri) × %_per_passeggero
autista    = arrotonda_al_centesimo(base × (1 + maggioraz./100)) + pedaggio_luogo
```

Si applica solo se il tipo di attività è abilitato, l'attività ha un luogo e l'autista è
presente. La somma dei passeggeri non può superare i presenti meno gli autisti.
Segnare un autista come assente azzera i suoi dati di guida.

## Modello dati (changeset `0010-places-and-mileage`)

- `places`: nome (unico tra gli attivi), indirizzo, `distance_km` (intero, A/R),
  `highway_cost`, note, audit, archiviazione, versione.
- `activities.place_id` (facoltativo); `location` resta come dettaglio libero.
- `activity_participants`: `is_driver`, `passenger_count` e lo snapshot
  `refund_flat_amount`, `refund_distance_km`, `refund_rate_per_km`, `refund_bonus_pct`,
  `refund_mileage_amount`, `refund_highway_amount`.
- `activities.refund_rules` esteso con
  `mileage: {enabled_types, rate_per_km, passenger_bonus_pct, max_bonus_passengers}`.
- Le presenze già registrate ricevono lo snapshot dell'importo fisso in vigore.

## Fasi

1. ✅ Changeset, codice generato, modulo `places` (`/api/v1/places`) e test.
2. Calcolatore unico dei rimborsi nel modulo attività, a parità di comportamento.
3. Regole chilometriche nelle impostazioni, autisti nel registro presenze, snapshot.
4. Frontend: configurazione Luoghi, campi km nella pagina rimborsi, selezione del luogo
   sull'attività, autista/passeggeri nel registro presenze, dettaglio importi.
5. Aggiornamento di `SPECIFICA_FUNZIONALE.md` e `STATO.md`.

## Punti aperti

- Modifica di luogo o tipo su un'attività con presenze già registrate: proposta di
  ricalcolare lo snapshot di quell'attività con le regole correnti, previa conferma
  nell'interfaccia.
- `€/km` è memorizzato con due decimali (convenzione dei campi `NUMERIC` del generatore).
