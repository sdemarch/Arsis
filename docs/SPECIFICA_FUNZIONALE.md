# Arsis — Specifica funzionale della webapp gestionale

**Versione:** 0.4  
**Stato:** bozza consolidata per MVP  
**Data:** 8 novembre 2026  
**Destinatari:** responsabili dell’associazione, progettisti e sviluppatori

Cosa è già implementato: [Stato](STATO.md). Cosa manca: [TODO](TODO.md). Come è costruita: [Architettura](ARCHITETTURA.md).

---

## 1. Scopo del documento

Questo documento descrive i requisiti funzionali dell’MVP della webapp Arsis per la gestione di una scuola di musica e delle attività della banda.

La specifica raccoglie le decisioni emerse durante l’intervista iniziale e definisce:

- perimetro e obiettivi dell’MVP;
- struttura della navigazione;
- pagine e principali flussi operativi;
- regole di business;
- modello dati concettuale;
- requisiti di sicurezza e usabilità;
- funzionalità escluse o rinviate.

La **Contabilità** dell’MVP è limitata a una prima nota di Banca e Cassa (sezione 12). Rate, pagamenti degli allievi, compensi e rendicontazione restano da definire, perché richiedono un’analisi dedicata.

### 1.1 Documenti di riferimento

- Logo e favicon ufficiali Arsis forniti con il brief iniziale.
- **Arsis — Design Tokens**, versione 1.1, giugno 2026 ([riferimenti/design-tokens.md](riferimenti/design-tokens.md)).

Il documento dei design token è la fonte di riferimento per colori, tipografia, spaziatura, raggi, ombre e transizioni dell’interfaccia. In caso di divergenza, i requisiti funzionali di questa specifica definiscono il comportamento, mentre i design token definiscono la presentazione.

## 2. Obiettivi del prodotto

La webapp deve offrire ai responsabili un unico punto di accesso per:

1. gestire l’anagrafica comune di allievi, insegnanti, musicanti e soci;
2. organizzare prove, concerti e processioni della banda;
3. configurare corsi, iscrizioni, lezioni e presenze della scuola;
4. accedere rapidamente all’archivio documentale su Google Drive;
5. registrare entrate e uscite in una prima nota di Banca e Cassa.

## 3. Perimetro dell’MVP

### 3.1 Funzionalità incluse

- Login con email e password.
- Accesso riservato ai responsabili.
- Anagrafica unica delle persone.
- Assegnazione di più ruoli alla stessa persona.
- Gestione dei contatti associati tra persone registrate.
- Gestione di soci, musicanti, strumenti e sezioni.
- Gestione di prove, concerti e processioni.
- Registro presenze aperto a tutte le persone attive.
- Rilevazione delle presenze alle attività.
- Gestione di corsi individuali e collettivi.
- Gestione delle iscrizioni degli allievi ai corsi.
- Tariffe annuali per corso e agevolazioni individuali.
- Inserimento manuale delle lezioni.
- Registro delle presenze alle lezioni.
- Collegamento a una cartella Google Drive.
- Archiviazione logica dei dati, senza cancellazione definitiva.
- Importazione delle presenze di una lezione da un modello Excel `.xlsx`.
- Prima nota contabile di Banca e Cassa con categorie configurabili, saldi iniziali e bilancio annuale.
- Dashboard Home essenziale.

### 3.2 Funzionalità escluse o rinviate

- Contabilità di rate, scadenze, insoluti, ricevute e compensi calcolati: **TBD**.
- Importazione Excel massiva delle lezioni: rinviata.
- Collegamento di documenti Drive a persone, corsi o attività.
- Gestione delle spese associate alle attività (i rimborsi ai partecipanti sono descritti in 9.6).
- Portale dedicato ad allievi, genitori o insegnanti.
- Ottimizzazione specifica per smartphone e tablet.

## 4. Utenti e autorizzazioni

### 4.1 Profilo utente

Nell’MVP è previsto un solo profilo applicativo:

- **Responsabile:** può consultare, creare e modificare tutti i dati disponibili nell’applicazione.

Non sono previsti accessi per allievi, genitori, insegnanti o musicanti.

### 4.2 Autenticazione

- Accesso tramite email e password.
- Le password non devono essere memorizzate in chiaro.
- L’utente autenticato deve poter effettuare il logout.
- Gli utenti disabilitati non devono poter accedere.

### 4.3 Tracciamento minimo

Per le entità principali è opportuno registrare:

- data e autore della creazione;
- data e autore dell’ultima modifica;
- data e autore dell’archiviazione.

## 5. Architettura della navigazione

L’interfaccia è progettata principalmente per l’uso da PC.

### 5.1 Topbar

La topbar contiene le aree principali:

1. **Home**
2. **Soci**
3. **Attività**
4. **Obiettivi**
5. **Scuola**
6. **Archivio**
7. **Contabilità**

La selezione di un’area aggiorna il contenuto della sidebar sinistra.

### 5.2 Sidebar per area

| Area | Voci della sidebar |
|---|---|
| Home | Dashboard |
| Soci | Tutte le persone; Soci; Musicanti; Allievi; Insegnanti |
| Attività | Calendario; Tutte le attività; Prove; Concerti; Processioni; Presenze |
| Obiettivi | Traguardi; Configura obiettivi |
| Scuola | Corsi; Iscrizioni; Lezioni; Registro presenze |
| Archivio | Apri Google Drive |
| Contabilità | Registro contabile; Bilancio |

Le liste di Soci, Musicanti, Allievi e Insegnanti sono viste filtrate della stessa anagrafica e non archivi separati.

## 6. Requisiti funzionali trasversali

### RF-TR-01 — Ricerca e filtri

Le liste principali devono consentire almeno:

- ricerca testuale;
- filtro per stato attivo/archiviato;
- filtri specifici dell’area;
- ordinamento delle colonne principali;
- azzeramento dei filtri.

### RF-TR-02 — Stati e archiviazione

- Persone, ruoli, corsi e attività non devono essere eliminati definitivamente dall’interfaccia.
- L’azione di rimozione deve tradursi in archiviazione o disattivazione.
- I dati archiviati devono essere esclusi dalle viste operative predefinite.
- Lo storico deve rimanere consultabile.

### RF-TR-03 — Organizzazione temporale

- L’applicazione utilizza l’anno solare, da gennaio a dicembre, come periodo di riferimento predefinito.
- L’anno non costituisce una separazione rigida dei dati.
- Liste, dashboard e registri possono essere filtrati per anno.
- I record mantengono le proprie date effettive e possono attraversare più anni quando il dominio lo richiede.

### RF-TR-04 — Conferme e validazioni

- Le operazioni di archiviazione devono richiedere conferma.
- I campi obbligatori devono essere chiaramente identificati.
- Gli errori di validazione devono apparire vicino al campo interessato.
- I riferimenti a record archiviati devono rimanere visibili nello storico.

## 7. Area Home

### 7.1 Dashboard

La Home presenta una dashboard essenziale, pensata come punto di ingresso e da rifinire in una fase successiva.

Contenuti iniziali suggeriti:

- prossime attività della banda;
- prossime lezioni registrate;
- conteggio delle persone attive per ruolo;
- accessi rapidi a “Nuova persona”, “Nuova attività” e “Nuova lezione”;
- **traguardi raggiunti**: le persone con un obiettivo raggiunto e non ancora azzerato, dalla più recente, con il rimando all’area Obiettivi (§9.7);
- pulsante per aprire l’archivio Google Drive.

I widget devono privilegiare informazioni immediatamente operative ed evitare, nell’MVP, indicatori contabili.

## 8. Area Soci e anagrafica

### 8.1 Principio dell’anagrafica unica

Ogni individuo è registrato una sola volta come **Persona**. Alla persona possono essere assegnati uno o più ruoli tra:

- Socio;
- Musicante;
- Allievo;
- Insegnante.

Esempio: una persona può essere contemporaneamente insegnante, socio e musicante.

### 8.2 Elenco persone

La pagina deve mostrare almeno:

- nome e cognome;
- contatti principali;
- ruoli attivi;
- stato;
- data dell’ultima modifica.

Azioni principali:

- creare una persona;
- aprire la scheda personale;
- modificare i dati;
- archiviare o riattivare la persona;
- filtrare per ruolo.

### 8.3 Scheda persona

La scheda è suddivisa nelle seguenti tab:

1. **Dati personali**
2. **Ruoli**
3. **Contatti associati**
4. **Corsi**
5. **Storico presenze**

#### Dati personali

Campi previsti:

- nome;
- cognome;
- data di nascita;
- luogo di nascita;
- codice fiscale;
- indirizzo di residenza;
- email;
- telefono;
- foto;
- note;
- stato attivo/archiviato.

Nome e cognome sono obbligatori. Gli altri campi possono essere valorizzati in base alle informazioni disponibili.

### 8.4 Contatti associati

Un contatto associato deve essere selezionato tra le persone già registrate. Il sistema non deve duplicarne nome, telefono o email.

La relazione può rappresentare, per esempio:

- genitore;
- tutore;
- familiare;
- referente;
- altro.

La relazione può indicare facoltativamente il contatto principale e il responsabile dei pagamenti. Queste informazioni preparano l’integrazione futura con la Contabilità.

Regole:

- una persona non può essere associata a se stessa;
- una persona può avere più contatti associati;
- l’archiviazione di una persona non cancella le relazioni storiche;
- il sistema deve evitare duplicati identici tra le stesse persone.

### 8.5 Ruolo Socio

Dati specifici:

- numero tessera;
- data di iscrizione;
- eventuale data di cessazione;
- stato attivo/inattivo;
- quota associativa annuale prevista;
- note.

Nell’MVP la quota è un dato informativo. Il relativo pagamento non viene gestito.

### 8.6 Ruolo Musicante

Dati specifici:

- data di ingresso;
- eventuale data di uscita;
- stato attivo/inattivo;
- uno o più strumenti;
- una o più sezioni inferite dagli strumenti;
- eventuale indicazione dello strumento principale;
- note.

Ogni strumento appartiene a una sezione del catalogo; la sezione non viene
assegnata manualmente al musicante.

### 8.7 Ruolo Allievo

Dati specifici:

- stato attivo/inattivo;
- data di inizio;
- eventuale data di cessazione;
- iscrizioni ai corsi;
- contatti associati;
- note.

### 8.8 Ruolo Insegnante

Dati specifici:

- stato attivo/inattivo;
- data di inizio;
- eventuale data di cessazione;
- corsi assegnati;
- dati utili ai futuri pagamenti, da dettagliare con la Contabilità;
- note.

## 9. Area Attività

### 9.1 Tipologie

L’MVP gestisce tre tipologie di attività:

- prova;
- concerto;
- processione.

### 9.2 Elenco e calendario

Le attività devono essere consultabili:

- come elenco cronologico;
- come calendario;
- tramite viste filtrate per tipologia;
- tramite filtro per anno solare.

### 9.3 Scheda attività

Campi previsti:

- titolo;
- tipologia;
- data;
- ora di inizio e fine;
- luogo, scelto tra quelli configurati (sezione 13), e dettaglio libero del luogo;
- descrizione;
- stato;
- referente facoltativo;
- note;
- stato delle presenze.

Stati suggeriti:

- pianificata;
- confermata;
- annullata;
- conclusa.

### 9.4 Chi può essere presente

Non esiste una convocazione: tutte le persone attive in anagrafica, con qualunque ruolo, possono essere segnate presenti o assenti a qualsiasi attività. Il registro mostra l’elenco completo con una ricerca per nome e il filtro “Solo registrate”.

La presenza registrata viene salvata sull’attività: se in seguito una persona viene archiviata, la sua presenza resta visibile nel registro di quell’attività.

### 9.5 Presenze alle attività

Per ciascuna persona sono ammessi due soli valori:

- presente;
- assente.

Prima della rilevazione, la presenza può rimanere non compilata. Il sistema deve distinguere “non registrata” da “assente”.

Azioni principali:

- compilazione rapida dell’intero elenco;
- impostazione individuale presente/assente;
- salvataggio e modifica successiva;
- consultazione del totale dei rimborsi, con il dettaglio di presenze, chilometri e pedaggi, nella scheda della persona.

Per ciascuna persona presente si può indicare se ha **guidato** e quanti **passeggeri** ha trasportato (solo il numero). Chi è assente o non registrato non può essere autista.

### 9.6 Rimborsi delle attività

Ogni presenza registrata matura:

- l’**importo fisso** previsto per la tipologia di attività;
- per gli **autisti**, se la tipologia ha il rimborso chilometrico attivo e l’attività ha un luogo, il **rimborso chilometrico** (RB-18) più il **pedaggio autostradale** del luogo.

Gli importi sono **registrati sulla presenza al momento della registrazione**, insieme ai parametri usati (km, tariffa, maggiorazione). Le modifiche successive alle regole o ai luoghi valgono solo per le presenze registrate da quel momento. Se si cambiano tipologia o luogo di un’attività con presenze già registrate, l’applicazione chiede conferma e ricalcola i rimborsi di quell’attività con le regole correnti.

La scheda attività mostra il totale suddiviso tra presenze, chilometri e pedaggi, con il numero di autisti e passeggeri; il riepilogo rimborsi lo mostra per persona. I rimborsi sono informativi e non generano movimenti nella prima nota.

Le spese sostenute per le attività restano escluse dall’MVP.

### 9.7 Obiettivi

Il responsabile configura **obiettivi** su presenze e rimborsi: presenze alle prove, ai concerti, alle processioni, presenze totali oppure rimborso totale maturato in euro, ciascuno con una **soglia** (intera per le presenze, in euro per i rimborsi). Un nuovo obiettivo conta tutto lo storico delle presenze registrate.

L’area **Obiettivi** mostra per ogni obiettivo le persone che l’hanno raggiunto, evidenziate e con l’indicazione «×N» se hanno coperto la soglia più volte, e quelle in corso con quanto manca. Da qui il responsabile **azzera** l’obiettivo per una persona o per tutte quelle che l’hanno raggiunto, ad esempio dopo aver consegnato un premio. L’azzeramento sottrae una soglia e conserva l’eccedenza (RB-19); l’ultimo azzeramento può essere annullato. Gli obiettivi sono informativi e non generano movimenti nella prima nota.

Ogni raggiungimento è **registrato nello storico** (Obiettivi → Storico) con data, persona, obiettivo e progresso (RB-20). Il traguardo resta *raggiunto* finché un azzeramento non lo chiude (*azzerato*); se il progresso scende sotto la soglia, per una presenza tolta, un’attività archiviata o una soglia alzata, viene *revocato*. Annullare un azzeramento riapre il traguardo con la sua data originale. Ogni registrazione compare anche nel tracciamento delle operazioni.

## 10. Area Scuola

### 10.1 Tipologie e categorie di corso

Ogni corso ha:

- una modalità: **individuale** o **collettivo**;
- una categoria: **strumento** o **musica d’insieme**.

### 10.2 Elenco corsi

La pagina deve mostrare almeno:

- nome del corso;
- modalità e categoria;
- insegnante;
- numero di allievi iscritti;
- giorno e orario, quando presenti;
- tariffa annuale;
- stato.

Azioni principali:

- creare un corso;
- modificare un corso;
- consultare iscritti e lezioni;
- archiviare o riattivare un corso.

### 10.3 Scheda corso

Campi previsti:

- denominazione;
- descrizione facoltativa;
- modalità;
- categoria;
- strumento, se applicabile;
- insegnante;
- giorno della settimana facoltativo;
- orario facoltativo;
- tariffa annuale;
- colore identificativo;
- piano di rate proposto;
- data di inizio e fine facoltative;
- stato attivo/archiviato;
- note.

Il giorno e l’orario hanno valore informativo e non generano automaticamente le lezioni.

### 10.4 Piano rate proposto

Il corso può definire un piano rate teorico composto da una o più rate, ciascuna con:

- numero progressivo;
- descrizione facoltativa;
- importo proposto;
- scadenza proposta.

Nell’MVP il piano non registra incassi, insoluti o ricevute. Tali funzioni appartengono alla futura area Contabilità.

### 10.5 Iscrizioni

L’iscrizione collega un allievo a un corso.

Dati previsti:

- allievo;
- corso;
- data di iscrizione;
- data di inizio;
- eventuale data di fine;
- stato;
- agevolazione applicata;
- note.

Regole:

- la tariffa base deriva dal corso ed è uguale per tutti gli iscritti;
- l’iscrizione può applicare un’agevolazione;
- l’agevolazione può essere espressa come importo fisso o percentuale;
- la motivazione può indicare casi come fratelli o accordi specifici;
- il totale agevolato deve essere mostrato, ma non costituisce ancora un credito contabile;
- lo stesso allievo non può avere due iscrizioni attive duplicate allo stesso corso e nello stesso periodo.

### 10.6 Lezioni

Le lezioni vengono create esclusivamente in modo manuale.

Campi previsti:

- corso;
- data;
- ora di inizio e fine facoltative;
- insegnante, inizialmente proposto dal corso;
- argomento o descrizione facoltativa;
- note;
- stato.

Stati suggeriti:

- pianificata;
- svolta;
- annullata.

### 10.7 Registro presenze delle lezioni

Per ciascuna lezione il sistema propone gli allievi con iscrizione attiva al corso alla data della lezione.

Per ogni allievo sono ammessi due soli valori:

- presente;
- assente.

Prima della compilazione, la presenza può rimanere non registrata.

Il registro deve consentire:

- compilazione rapida per lezione;
- modifica successiva;
- filtro per corso, allievo, data e anno;
- visualizzazione dello storico nella scheda persona;
- conteggio delle presenze e delle assenze.

### 10.8 Importazione Excel

Dal registro presenze di una lezione il responsabile può scaricare un modello `.xlsx` con gli allievi iscritti e reimportarlo compilato. L’importazione aggiorna solo le presenze della lezione aperta.

L’importazione massiva delle lezioni resta un requisito futuro. Il modello dati deve comunque permetterla senza cambiare le entità Lezione e Presenza lezione.

## 11. Area Archivio

L’Archivio è volutamente essenziale.

### RF-AR-01 — Cartella Drive

- L’applicazione memorizza l’URL di una cartella principale Google Drive.
- La pagina mostra un pulsante chiaramente identificabile, per esempio “Apri archivio su Google Drive”.
- Il collegamento si apre in una nuova scheda del browser.
- L’app non replica l’alberatura dei file e non importa metadati da Drive.
- Non sono previste associazioni tra documenti e record applicativi.

L’accesso effettivo ai file dipende dai permessi configurati su Google Drive.

## 12. Area Contabilità

L’area Contabilità è una **prima nota**: registra le entrate e le uscite effettive di due conti, **Banca** e **Cassa**, e ne ricava i saldi. Non genera movimenti in automatico da corsi, iscrizioni o attività.

### RF-CO-01 — Categorie contabili

Ogni movimento appartiene a una categoria configurabile da **Configurazioni → Categorie contabili**. Una categoria definisce:

- nome univoco;
- verso ammesso: entrata, uscita oppure entrambi;
- ruolo richiesto alla persona collegata, facoltativo: allievo, insegnante o socio;
- corso obbligatorio, sì o no;
- colore e ordine di visualizzazione.

Le categorie usate non si cancellano: vengono archiviate e restano visibili sui movimenti già registrati. All’installazione sono proposte, tra le altre, Retta scuola, Quota associativa, Contributo o donazione, Rimborso insegnante e Commissione bancaria.

### RF-CO-02 — Registro dei movimenti

Il registro mostra i movimenti dell’esercizio selezionato, dal più recente, con data, soggetto, categoria, conto, descrizione, riferimento documento e importo. È possibile filtrare per mese, conto e categoria e cercare in soggetto, descrizione e riferimento.

Un movimento contiene: data, verso, conto, categoria, importo positivo, soggetto, descrizione, persona e corso collegati quando richiesti, riferimento documento facoltativo.

Quando la categoria richiede una persona, il modulo propone solo le persone con quel ruolo e compila il soggetto con il loro nome. Quando richiede un corso, il corso è obbligatorio; per un insegnante sono proposti solo i suoi corsi.

Un movimento può essere **evidenziato** (⚑) per segnalarlo come da verificare: la riga viene messa in risalto e il filtro “Solo evidenziati” mostra solo quei movimenti. L’evidenziazione si attiva o rimuove con un clic dalla riga o dal modulo, anche se la categoria del movimento è stata nel frattempo archiviata.

I movimenti si possono modificare ed eliminare. L’eliminazione chiede conferma ed è tracciata nell’audit.

### RF-CO-03 — Saldi iniziali e bilancio

Per ogni esercizio il responsabile inserisce il saldo iniziale di Banca e di Cassa. La vista **Bilancio** mostra per ciascun conto saldo iniziale, entrate, uscite e saldo finale, il totale disponibile e i totali di entrate e uscite per categoria.

### RF-CO-04 — Fuori perimetro

Restano da definire con un’intervista dedicata (sezione 18): generazione delle rate, scadenze e insoluti, ricevute, compensi calcolati degli insegnanti e report di rendicontazione. Il piano rate dei corsi e le agevolazioni restano dati organizzativi e non producono movimenti.

## 13. Configurazione

Le configurazioni possono essere accessibili dal menu utente o da un’icona dedicata, senza aggiungere una sesta area funzionale alla topbar.

Configurazioni minime:

- catalogo strumenti;
- catalogo sezioni;
- URL della cartella Google Drive;
- categorie contabili (sezione 12);
- rimborsi delle attività: importo per presenza per tipologia e, nella stessa pagina, rimborso chilometrico (tipologie abilitate, € per km, % di maggiorazione per passeggero, numero massimo di passeggeri conteggiati);
- luoghi delle attività: nome, indirizzo, km di andata e ritorno (interi), pedaggio autostradale di andata e ritorno, note. I luoghi non si cancellano: si archiviano e restano visibili sulle attività già collegate;
- gestione degli utenti responsabili;
- salvataggi: esportazione di tutti i dati in un file `.arsis-save` e ripristino da un salvataggio;
- eventuali valori predefiniti dell’applicazione.

Gli strumenti o le sezioni già utilizzati non devono essere cancellati definitivamente, ma disattivati.

## 14. Modello dati concettuale

```mermaid
erDiagram
    UTENTE {
        int id PK
        string email
        string password_hash
        boolean attivo
    }

    PERSONA {
        int id PK
        string nome
        string cognome
        date data_nascita
        string codice_fiscale
        string email
        string telefono
        string stato
    }

    RUOLO_PERSONA {
        int id PK
        int persona_id FK
        string tipo_ruolo
        date data_inizio
        date data_fine
        string stato
    }

    CONTATTO_ASSOCIATO {
        int id PK
        int persona_id FK
        int contatto_id FK
        string tipo_relazione
        boolean principale
        boolean responsabile_pagamenti
    }

    STRUMENTO {
        int id PK
        string nome
        int sezione_id FK
        boolean attivo
    }

    SEZIONE {
        int id PK
        string nome
        boolean attivo
    }

    MUSICANTE_STRUMENTO {
        int musicante_ruolo_id FK
        int strumento_id FK
        boolean principale
    }

    ATTIVITA {
        int id PK
        string tipo
        string titolo
        datetime inizio
        datetime fine
        int luogo_id FK
        string dettaglio_luogo
        string stato
    }

    LUOGO {
        int id PK
        string nome
        string indirizzo
        int km_andata_ritorno
        decimal pedaggio_andata_ritorno
    }

    PARTECIPAZIONE_ATTIVITA {
        int id PK
        int attivita_id FK
        int persona_id FK
        string presenza
    }

    CORSO {
        int id PK
        string nome
        string modalita
        string categoria
        int insegnante_id FK
        decimal tariffa_annuale
        string colore
        string stato
    }

    RATA_PROPOSTA {
        int id PK
        int corso_id FK
        int numero
        decimal importo
        date scadenza
    }

    ISCRIZIONE {
        int id PK
        int corso_id FK
        int allievo_id FK
        date data_inizio
        date data_fine
        string stato
    }

    AGEVOLAZIONE {
        int id PK
        int iscrizione_id FK
        string tipo
        decimal valore
        string motivazione
    }

    LEZIONE {
        int id PK
        int corso_id FK
        int insegnante_id FK
        datetime inizio
        datetime fine
        string stato
    }

    PRESENZA_LEZIONE {
        int id PK
        int lezione_id FK
        int allievo_id FK
        string presenza
    }

    PERSONA ||--o{ RUOLO_PERSONA : possiede
    PERSONA ||--o{ CONTATTO_ASSOCIATO : ha
    PERSONA ||--o{ CONTATTO_ASSOCIATO : viene_associata
    RUOLO_PERSONA ||--o{ MUSICANTE_STRUMENTO : utilizza
    STRUMENTO ||--o{ MUSICANTE_STRUMENTO : classifica
    SEZIONE ||--o{ STRUMENTO : raggruppa
    ATTIVITA ||--o{ PARTECIPAZIONE_ATTIVITA : include
    PERSONA ||--o{ PARTECIPAZIONE_ATTIVITA : partecipa
    PERSONA ||--o{ CORSO : insegna
    CORSO ||--o{ RATA_PROPOSTA : propone
    CORSO ||--o{ ISCRIZIONE : riceve
    PERSONA ||--o{ ISCRIZIONE : frequenta
    ISCRIZIONE ||--o| AGEVOLAZIONE : applica
    CORSO ||--o{ LEZIONE : comprende
    PERSONA ||--o{ LEZIONE : tiene
    LEZIONE ||--o{ PRESENZA_LEZIONE : registra
    PERSONA ||--o{ PRESENZA_LEZIONE : riguarda
```

### 14.1 Note sul modello

- `RUOLO_PERSONA` consente ruoli multipli e conserva le date di validità.
- I dati specifici dei ruoli possono essere implementati in tabelle dedicate collegate a `RUOLO_PERSONA`; il diagramma mostra il livello concettuale.
- Le presenze usano tre condizioni tecniche: non registrata, presente e assente. Nell’interfaccia operativa gli stati selezionabili sono solo presente e assente.
- Una partecipazione viene creata alla prima registrazione della presenza di una persona e conserva presenza e rimborsi registrati.
- Tariffe, rate proposte e agevolazioni sono dati organizzativi, non movimenti contabili.
- I movimenti contabili sono registrati a mano nella prima nota; il collegamento a persona e corso serve a verificarne la coerenza, non a calcolare crediti.
- Tutte le entità principali includono metadati di creazione, modifica e archiviazione anche quando non riportati nel diagramma.

## 15. Regole di business riepilogative

| Codice | Regola |
|---|---|
| RB-01 | Una persona viene registrata una sola volta e può avere più ruoli contemporanei. |
| RB-02 | Un contatto associato deve essere una persona già presente nell’anagrafica. |
| RB-03 | Un musicante può essere collegato a più strumenti; le sue sezioni sono dedotte dalle sezioni degli strumenti assegnati. |
| RB-04 | Ogni persona attiva può essere segnata presente o assente a qualsiasi attività, senza convocazione. |
| RB-05 | Le presenze alle attività e alle lezioni sono presente/assente; il valore può restare inizialmente non registrato. |
| RB-06 | La tariffa annuale è definita sul corso ed è comune agli iscritti. |
| RB-07 | Le agevolazioni sono applicate alla singola iscrizione come percentuale o importo fisso. |
| RB-08 | Giorno e orario del corso sono facoltativi e non generano lezioni. |
| RB-09 | Le lezioni vengono create manualmente. |
| RB-10 | Non è previsto hard delete; i record vengono archiviati o disattivati. |
| RB-11 | L’anno solare è un filtro operativo, non un contenitore rigido dei dati. |
| RB-12 | Il collegamento all’archivio apre Google Drive in una nuova scheda. |
| RB-13 | Piano rate e quote non producono movimenti contabili nell’MVP; i movimenti si registrano a mano nella prima nota. |
| RB-14 | Il colore del corso deve essere scelto dalla palette applicativa prevista dai design token. |
| RB-15 | Il verso di un movimento deve essere ammesso dalla sua categoria. |
| RB-16 | Se la categoria richiede un ruolo, la persona collegata deve averlo attivo alla data del movimento; per le rette l’allievo deve essere iscritto al corso a quella data, per i rimborsi l’insegnante deve essere assegnato al corso. |
| RB-17 | Il saldo finale di un conto è saldo iniziale + entrate − uscite dell’esercizio. Gli importi sono espressi in euro con due decimali. |
| RB-18 | Rimborso dell’autista = arrotondamento al centesimo di (km A/R del luogo × € per km) × (1 + min(passeggeri, massimo conteggiato) × % per passeggero), più il pedaggio A/R del luogo; si somma all’importo fisso della presenza. I passeggeri indicati non possono superare i presenti che non guidano. Gli importi si fissano alla registrazione della presenza. |
| RB-19 | Progresso di una persona su un obiettivo = totale della metrica sulle presenze registrate − somma delle soglie consumate dagli azzeramenti attivi; l’obiettivo è raggiunto floor(progresso / soglia) volte. L’azzeramento è ammesso solo con progresso ≥ soglia e consuma la soglia in vigore in quel momento. |
| RB-20 | Per ogni persona e obiettivo i traguardi aperti sono sempre floor(progresso / soglia): quando il progresso copre una soglia in più si registra un traguardo con la data del momento; quando ne copre meno si revocano i più recenti. L’azzeramento chiude il traguardo aperto più vecchio. |

## 16. Requisiti non funzionali

### 16.1 Usabilità

- Interfaccia desktop-first.
- Navigazione coerente tra topbar e sidebar.
- Azioni principali chiaramente visibili.
- Moduli suddivisi in sezioni brevi e comprensibili.
- Liste con paginazione o caricamento progressivo quando necessario.
- Messaggi di conferma ed errore espressi in linguaggio semplice.

### 16.2 Identità visiva

- Utilizzo del logo Arsis fornito.
- Verde Arsis `#1D9E75` come colore primario.
- Stile pulito, contemporaneo e leggibile.
- Contrasto sufficiente per testi, pulsanti e stati interattivi.
- Il favicon fornito deve essere utilizzato nel browser.

#### Design system di riferimento

L’interfaccia deve consumare i token definiti in **Arsis — Design Tokens v1.1**, evitando colori, spaziature e raggi inseriti arbitrariamente nei componenti.

Principi vincolanti:

- i token sono esposti come CSS custom properties;
- il colore accent principale è `--color-accent: #1D9E75` in modalità chiara;
- hover e sidebar utilizzano i verdi profondi della palette, in particolare `#0F6E56` e `#085041` come riferimenti cromatici;
- superfici, bordi e testi usano i rispettivi token semantici e non valori locali;
- success, warning e danger devono rimanere semanticamente distinti dall’accent del brand;
- la griglia di spaziatura ha base 4 px;
- i raggi standard sono 4, 8, 12 e 18 px, oltre al raggio pieno per badge e avatar;
- ombre e transizioni devono usare esclusivamente i token previsti;
- i componenti devono mantenere un comportamento coerente nei diversi stati: default, hover, focus, disabled ed errore.

#### Tipografia

| Ruolo | Font | Utilizzo |
|---|---|---|
| UI | Source Sans 3 | Corpo, navigazione, label, input e pulsanti |
| Display | Newsreader | Titoli pagina, saluto Home e metriche principali |
| Dati | IBM Plex Mono | Date, codici fiscali, percentuali e futuri valori monetari |

La scala tipografica di riferimento va da `.75rem` a `2.5rem` secondo i token `--text-xs` … `--text-3xl`, con una radice al 112,5% per aumentare la leggibilità in modo proporzionale. Il peso massimo ordinario è 600, per mantenere un’interfaccia nitida e non eccessivamente pesante.

#### Tema chiaro e scuro

- Il tema chiaro è il tema predefinito dell’MVP.
- L’architettura CSS deve usare i token in modo da non impedire il tema scuro.
- Il tema scuro utilizza gli override `[data-theme="dark"]` definiti nel documento dei design token.
- Il selettore utente e la persistenza della preferenza dark mode sono evoluzioni non bloccanti per l’accettazione dell’MVP, salvo successiva conferma.

#### Colori dei corsi

Ogni corso può ricevere un colore identificativo scelto dal responsabile dalla palette applicativa definita nel riferimento:

| Nome | Colore | Sfondo chiaro |
|---|---|---|
| Blu | `#378ADD` | `#EBF3FC` |
| Verde | `#1D9E75` | `#E6F6F0` |
| Arancio | `#D85A30` | `#FAEEE9` |
| Ambra | `#BA7517` | `#F7EDD9` |
| Viola | `#7F77DD` | `#EEEDF9` |
| Teal | `#2BA8A0` | `#E4F4F3` |
| Rosa | `#C2507A` | `#F7E8EF` |
| Grafite | `#5A6572` | `#EAEEF1` |

Il colore è un dato del corso e viene usato in calendario, card, badge e registro lezioni; non è un token del tema.

#### Avatar

In assenza di foto, la persona è rappresentata da un avatar con iniziali. Il colore proviene dalle classi predefinite `av-blue`, `av-green`, `av-amber`, `av-rose`, `av-violet`, `av-teal`, `av-orange` e `av-slate`, assegnato in modo stabile alla persona.

### 16.3 Sicurezza e privacy

- Accesso consentito solo a utenti autenticati e attivi.
- Password memorizzate tramite hashing sicuro.
- Accesso solo dal PC dell’installazione; connessione HTTPS se l’applicazione viene pubblicata in rete.
- Protezione dei dati personali secondo i principi di minimizzazione e necessità.
- Nessuna esposizione pubblica delle anagrafiche.
- Validazione degli input lato client e lato server.

### 16.4 Affidabilità

- Le modifiche devono essere persistite in modo atomico.
- Gli errori non devono lasciare record parziali o incoerenti.
- Devono essere previsti salvataggi completi esportabili e una copia automatica dei dati prima di aggiornamenti e ripristini.
- Le relazioni storiche devono sopravvivere all’archiviazione dei record collegati.

## 17. Criteri di accettazione dell’MVP

L’MVP può essere considerato funzionalmente accettabile quando un responsabile riesce a:

1. accedere con email e password;
2. creare una persona con tutti i dati personali disponibili;
3. assegnare più ruoli alla stessa persona;
4. collegare un minorenne a un contatto già registrato;
5. associare più strumenti a un musicante e verificarne le sezioni inferite;
6. creare una prova, un concerto o una processione;
7. ottenere automaticamente l’elenco dei musicanti attivi e modificarlo;
8. registrare presenti e assenti a un’attività;
9. creare corsi individuali e collettivi e assegnare loro un colore identificativo;
10. definire tariffa annuale e rate proposte di un corso;
11. iscrivere un allievo e applicare un’agevolazione;
12. inserire manualmente una lezione;
13. registrare presenti e assenti alla lezione;
14. consultare corsi e presenze dalla scheda della persona;
15. archiviare e riattivare record senza perdita dello storico;
16. aprire la cartella Google Drive in una nuova scheda;
17. registrare entrate e uscite di Banca e Cassa e consultarne il bilancio annuale;
18. importare le presenze di una lezione da un file Excel.

## 18. Decisioni aperte per le fasi successive

### Contabilità

La prima nota di Banca e Cassa è disponibile (sezione 12). Da approfondire tramite intervista dedicata:

- generazione e gestione delle rate a partire dal piano del corso;
- pagamenti parziali, scadenze e insoluti;
- ricevute e metodi di pagamento;
- calcolo dei compensi degli insegnanti dalle lezioni;
- collegamento dei movimenti alle attività;
- report e rendicontazione.

### Evoluzioni possibili

- importazione Excel massiva delle lezioni;
- ruoli e permessi differenziati tra responsabili;
- portale per insegnanti, allievi e contatti associati;
- notifiche e promemoria;
- integrazione più profonda con Google Drive;
- reportistica avanzata;
- ottimizzazione completa per dispositivi mobili.

## 19. Assunzioni da validare durante la progettazione esecutiva

Le seguenti scelte sono coerenti con i requisiti raccolti, ma potranno essere rifinite durante la progettazione delle schermate:

- possibilità di indicare più contatti associati e uno principale;
- possibilità di indicare lo strumento principale del musicante;
- stati operativi proposti per attività, corsi e lezioni;
- presenza di data inizio/fine sui ruoli per conservarne lo storico;
- contenuti esatti dei widget della dashboard;
- posizione dell’area Configurazione nel menu utente;
- dettaglio dei dati dell’insegnante necessari alla futura Contabilità.

Queste assunzioni non modificano l’architettura fondamentale dell’MVP e possono essere confermate attraverso wireframe e prototipi.
