# Check di coerenza dell'interfaccia — Arsis

_Aggiornato: 3 settembre 2026_

## Esito

L'interfaccia Angular è ora l'unica implementazione frontend e la sua build è verificata. Il design system è coerente tra login, home, persone, attività, scuola, archivio, contabilità e configurazioni.

## Elementi coerenti

- Token condivisi per colori, spaziature, superfici, raggi e tema chiaro/scuro.
- Shell, intestazioni, bottoni, card, tabelle e filtri con linguaggio visivo uniforme.
- Pagine di dettaglio basate su componenti e fogli stile condivisi.
- Stati hover/focus e supporto della preferenza di riduzione del movimento.

## Rischi da risolvere

1. **Alta — shell non responsive.** Topbar, sidebar fissa da 240 px e contenuto non hanno breakpoint comuni; su mobile possono comprimersi o produrre overflow.
2. **Alta — font non allineati.** I font importati (DM Sans, DM Mono e Fraunces) non coincidono con quelli dichiarati dai token (Source Sans Pro, Libre Baskerville e Space Mono); la resa dipende dai fallback di sistema.
3. **Media — contabilità più densa.** Layout, tabella, modale e stili sono concentrati in un solo componente, rendendo più onerosa la manutenzione visiva.
4. **Media — stato database statico.** La shell mostra “Database locale — Connesso” senza collegamento allo stato reale del backend.

## Priorità

Definire la responsività della shell, allineare la tipografia e ripetere il controllo renderizzato su desktop e mobile.
