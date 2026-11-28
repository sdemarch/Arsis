# Piano — Obiettivi (traguardi dei soci)

Stato: implementato sul branch `feature/obiettivi` (derivato da `feature/rimborsi-km`).

## Obiettivo

Definire **obiettivi configurabili** legati a presenze e rimborsi (es. «10 prove»,
«5 concerti», «150 € di rimborsi») e mostrare, in una nuova voce del menu principale
**Obiettivi**, le persone che li hanno raggiunti. Da quella pagina il responsabile può
**azzerare** l'obiettivo per una persona (es. dopo aver consegnato il premio o il
rimborso).

## Decisioni

| Tema | Decisione |
|---|---|
| Metriche | Presenze a prove, a concerti, a processioni, presenze totali, rimborso totale maturato (€). |
| Soglia | Intera per le presenze, in euro con due decimali per i rimborsi; sempre > 0. |
| Fonte dei dati | Le presenze registrate (`attendance = 'present'`) e lo **snapshot** dei rimborsi già salvato su di esse (RB-18): nessun ricalcolo. Stesse regole del riepilogo rimborsi. |
| Storico | Un nuovo obiettivo conta **tutto lo storico**: chi ha già superato la soglia è subito evidenziato. |
| Azzeramento | Per persona. Sottrae **una soglia** al progresso e **conserva l'eccedenza** (soglia 10, 12 presenze → riparte da 2). Chi supera più volte la soglia resta evidenziato con «×N» e può essere azzerato di nuovo. |
| Storicizzazione | Ogni azzeramento è una riga del registro `milestone_resets` con la quantità consumata: modificare la soglia non altera gli azzeramenti passati. |
| Annullamento | L'ultimo azzeramento di una persona può essere annullato (archiviato). |
| Persone | Solo persone non archiviate. |

## Regola di calcolo (RB-19)

```
totale     = somma della metrica su tutte le presenze registrate della persona
consumato  = somma di `consumed` degli azzeramenti attivi (persona, obiettivo)
progresso  = totale − consumato
raggiunto  = floor(progresso / soglia)        (≥ 1 → evidenziato)
```

L'azzeramento è consentito solo se `progresso ≥ soglia`; registra `consumed = soglia`.

## Modello dati (changeset `0011-milestones`)

- `milestones`: nome (unico tra gli attivi), `metric`, `threshold`, note, audit,
  archiviazione, versione.
- `milestone_resets`: `milestone_id`, `person_id`, `consumed`, `progress_before`,
  creazione e archiviazione (annullamento).

## API (`/api/v1/milestones`)

| Metodo | Percorso | Scopo |
|---|---|---|
| GET | `/milestones` | Elenco obiettivi (configurazione). |
| POST / PATCH / DELETE | `/milestones[/{id}]` | Crea, modifica (versione), archivia. |
| GET | `/milestones/board` | Per ogni obiettivo attivo: persone che l'hanno raggiunto e persone in corso. |
| POST | `/milestones/{id}/resets` | Azzera per una o più persone (`person_ids`). |
| DELETE | `/milestones/{id}/resets/{reset_id}` | Annulla un azzeramento. |

## Fasi

1. ✅ Changeset, codice generato, verifica dello schema.
2. ✅ Modulo backend `milestones` (repository, servizio, router) e test API.
3. ✅ Frontend: voce di menu **Obiettivi**, bacheca dei traguardi con azzeramento,
   pagina di configurazione degli obiettivi.
4. ✅ Aggiornamento di `SPECIFICA_FUNZIONALE.md` e `STATO.md`.

## Storico dei traguardi e Home (changeset `0012-milestone-achievements`)

| Tema | Decisione |
|---|---|
| Registro | `milestone_achievements`: una riga per ogni soglia coperta, con `reached_at`, progresso e stato `open` / `reset` / `revoked`. |
| Allineamento (RB-20) | Traguardi aperti = floor(progresso / soglia). Si aggiungono quando il progresso cresce, si revocano i più recenti quando cala. |
| Quando | Nella stessa transazione di presenze, ricalcolo rimborsi, archiviazione attività, creazione e modifica obiettivo, azzeramento e annullamento; le letture riallineano se serve. |
| Azzeramento | Chiude il traguardo aperto più vecchio (`reset_id`); l'annullamento lo riapre con la data originale. |
| Data | Momento della registrazione che ha fatto superare la soglia; per lo storico precedente a un obiettivo nuovo, il momento della sua creazione. |
| Audit | `milestone.reached`, `milestone.revoked`. |
| API | `GET /milestones/achievements?status=&milestone_id=&person_id=&limit=`; la bacheca espone `reached_at`. |
| Interfaccia | Obiettivi → **Storico** con filtri; card **Traguardi raggiunti** in Home, caricata a parte dal riepilogo. |

## Possibili evoluzioni

- Finestre temporali (obiettivo per anno sociale).
- Collegamento con la contabilità: generare un movimento al momento dell'azzeramento.
