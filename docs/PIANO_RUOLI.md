# Piano — Ruoli configurabili

Stato: implementato sul branch `feature/obiettivi-storico`.

## Obiettivo

I ruoli delle persone erano fissi (Socio, Musicante, Allievo, Insegnante), cablati come
`CHECK` nel database e come elenchi nel codice. Diventano un **catalogo configurabile**
da Configurazioni → **Ruoli**.

## Decisioni

| Tema | Decisione |
|---|---|
| Ruoli predefiniti | I quattro ruoli esistenti restano, con codice fisso (`member`, `musician`, `student`, `teacher`): corsi, iscrizioni, lezioni, strumenti e dati del socio dipendono da loro. Si possono **rinominare** (singolare, plurale, descrizione) e riordinare, non archiviare. |
| Ruoli personalizzati | Nome, plurale, descrizione, ordine. Si assegnano con date come gli altri, compaiono nei filtri e nel menu di Soci, possono essere richiesti da una categoria contabile e si importano da Excel per nome. Non hanno comportamenti speciali. |
| Codice | Generato dal nome (`Maestro di Banda` → `maestro-di-banda`), unico anche tra gli archiviati, mai modificato: assegnazioni e categorie vi fanno riferimento. |
| Archiviazione | Solo per i ruoli personalizzati, quando nessuno lo ricopre (ruolo attivo e non concluso) e nessuna categoria contabile attiva lo richiede. Le assegnazioni passate restano nello storico con il loro nome. |
| Assegnazione | Solo ruoli attivi. Le date di un'assegnazione esistente restano modificabili anche se il ruolo viene poi archiviato. |
| Errori | Ruolo inesistente o archiviato: 422 `INVALID_PERSON_ROLE` (prima l'eccezione non era gestita e dava 500). |
| Ruoli degli utenti | Fuori perimetro: i responsabili hanno tutti gli stessi permessi (vedi §18 della specifica). |

## Regola (RB-21)

Il ruolo assegnato a una persona o richiesto da una categoria contabile deve esistere nel
catalogo ed essere attivo. I ruoli predefiniti non si archiviano; un ruolo personalizzato si
archivia solo se non è ricoperto e non è richiesto da categorie attive.

## Modello dati (changeset `0013-configurable-roles`)

- `role_types`: `code` (unico, `[a-z][a-z0-9-]*`), `name` (unico tra gli attivi),
  `plural_name`, `description`, `is_system`, `display_order`, audit, archiviazione,
  versione; i quattro ruoli predefiniti inseriti dal changeset.
- `person_roles.role_type` e `accounting_categories.required_person_role`: il `CHECK` sui
  valori ammessi diventa una chiave esterna verso `role_types(code)`.
- SQLite non permette di togliere un `CHECK`: le due tabelle vengono **ricostruite**
  (copia, `DROP`, `CREATE`, reinserimento con gli stessi id). Niente `ALTER TABLE … RENAME`:
  i trigger di altre tabelle che citano `person_roles` restano validi.
- I commenti stanno fuori dalle istruzioni: Liquibase li toglie, il migratore integrato li
  conserva, e il DDL salvato deve coincidere (verificato dal test di migrazione).

## Verifiche

- Prova della migrazione su una copia del database reale: stesse righe, stessi id, stessi
  trigger, `foreign_key_check` e `integrity_check` puliti, trigger tra tabelle funzionanti.
- Test API `tests/api/test_roles.py`; prova sul database migrato con chiavi esterne attive.

## API (`/api/v1/role-types`)

| Metodo | Percorso | Scopo |
|---|---|---|
| GET | `/role-types?include_archived=` | Catalogo in ordine, con il numero di persone che ricoprono ciascun ruolo. |
| POST / PATCH / DELETE | `/role-types[/{id}]` | Crea, modifica (versione), archivia. |

## Interfaccia

- Configurazioni → **Ruoli**: elenco con riordino, modifica, archiviazione.
- Etichette e opzioni dei ruoli lette dal catalogo in: elenco e scheda persona, nuova
  persona, categorie contabili, movimento contabile, menu laterale di Soci (una voce per
  ruolo, con il nome al plurale).
