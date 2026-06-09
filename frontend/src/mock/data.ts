import type { Allievo, Insegnante, Corso, Riga } from '../types'

// ── Insegnanti ────────────────────────────────────────────────────────────────

export const INSEGNANTI: Insegnante[] = [
  {
    id: 1, tipo: 'insegnante',
    nome: 'Marco', cognome: 'Ferretti',
    email: 'marco.ferretti@arsis.it', tel: '347 1234567',
    nato: '1985-03-14', cf: 'FRRMRC85C14F205Z',
    indirizzo: 'Via Garibaldi 12, Genova',
    stato: 'attivo', col: 'blue', corsi: [1, 2],
    stipendio: 1400,
    pagamenti: [],
  },
  {
    id: 2, tipo: 'insegnante',
    nome: 'Giulia', cognome: 'Morandi',
    email: 'giulia.morandi@arsis.it', tel: '338 9876543',
    nato: '1990-07-22', cf: 'MRNGLU90L62D969X',
    indirizzo: 'Via Roma 45, Genova',
    stato: 'attivo', col: 'rose', corsi: [3, 4],
    stipendio: 1200,
    pagamenti: [],
  },
  {
    id: 3, tipo: 'insegnante',
    nome: 'Luca', cognome: 'Bianchi',
    email: 'luca.bianchi@arsis.it', tel: '333 5556677',
    nato: '1978-11-05', cf: 'BNCLCU78S05D969Y',
    indirizzo: 'Corso Torino 8, Genova',
    stato: 'attivo', col: 'teal', corsi: [5],
    stipendio: 1600,
    pagamenti: [],
  },
]

// ── Corsi ─────────────────────────────────────────────────────────────────────

export const CORSI: Corso[] = [
  {
    id: 1, nome: 'Pianoforte Bambini',
    tipo: 'collettivo', insegnante: 'Marco Ferretti',
    giorno: 'Martedì', orario: '16:00–17:30', aula: 'Sala A',
    stato: 'attivo', color: 0, allievi: 8,
    piano: {
      mode: '3rate', quota: 480,
      rate: [
        { desc: '1ª Rata', data: '2024-10-15', importo: 160 },
        { desc: '2ª Rata', data: '2025-01-15', importo: 160 },
        { desc: '3ª Rata', data: '2025-04-15', importo: 160 },
      ],
    },
  },
  {
    id: 2, nome: 'Chitarra Classica',
    tipo: 'collettivo', insegnante: 'Marco Ferretti',
    giorno: 'Giovedì', orario: '18:00–19:30', aula: 'Sala B',
    stato: 'attivo', color: 1, allievi: 6,
    piano: {
      mode: '3rate', quota: 450,
      rate: [
        { desc: '1ª Rata', data: '2024-10-15', importo: 150 },
        { desc: '2ª Rata', data: '2025-01-15', importo: 150 },
        { desc: '3ª Rata', data: '2025-04-15', importo: 150 },
      ],
    },
  },
  {
    id: 3, nome: 'Canto Moderno',
    tipo: 'collettivo', insegnante: 'Giulia Morandi',
    giorno: 'Mercoledì', orario: '17:00–18:30', aula: 'Sala C',
    stato: 'attivo', color: 4, allievi: 10,
    piano: {
      mode: '4rate', quota: 520,
      rate: [
        { desc: '1ª Rata', data: '2024-10-01', importo: 130 },
        { desc: '2ª Rata', data: '2024-12-01', importo: 130 },
        { desc: '3ª Rata', data: '2025-02-01', importo: 130 },
        { desc: '4ª Rata', data: '2025-04-01', importo: 130 },
      ],
    },
  },
  {
    id: 4, nome: 'Violino',
    tipo: 'individuale', insegnante: 'Giulia Morandi',
    giorno: 'Venerdì', orario: '15:00–15:45', aula: 'Sala A',
    stato: 'attivo', color: 6, allievi: 3,
    piano: {
      mode: 'custom', quota: 900,
      rate: [
        { desc: 'Acconto iscrizione', data: '2024-09-01', importo: 200 },
        { desc: '1ª Rata', data: '2024-11-01', importo: 350 },
        { desc: '2ª Rata', data: '2025-03-01', importo: 350 },
      ],
    },
  },
  {
    id: 5, nome: 'Teoria Musicale',
    tipo: 'collettivo', insegnante: 'Luca Bianchi',
    giorno: 'Lunedì', orario: '19:00–20:00', aula: 'Sala B',
    stato: 'attivo', color: 5, allievi: 12,
    piano: {
      mode: '3rate', quota: 300,
      rate: [
        { desc: '1ª Rata', data: '2024-10-15', importo: 100 },
        { desc: '2ª Rata', data: '2025-01-15', importo: 100 },
        { desc: '3ª Rata', data: '2025-04-15', importo: 100 },
      ],
    },
  },
]

// ── Allievi ───────────────────────────────────────────────────────────────────

export const ALLIEVI: Allievo[] = [
  {
    id: 1, tipo: 'allievo',
    nome: 'Sofia', cognome: 'Russo',
    email: 'sofia.russo@gmail.com', tel: '347 1112233',
    nato: '2012-05-18', cf: 'RSSSFO12E58D969A',
    indirizzo: 'Via Balbi 3, Genova',
    stato: 'attivo', col: 'rose', corsi: [1, 5],
    pagamenti: [],
  },
  {
    id: 2, tipo: 'allievo',
    nome: 'Matteo', cognome: 'Conti',
    email: 'matteo.conti@gmail.com', tel: '338 4445566',
    nato: '2010-09-03', cf: 'CNTMTT10P03D969B',
    indirizzo: 'Piazza De Ferrari 1, Genova',
    stato: 'attivo', col: 'blue', corsi: [2],
    pagamenti: [],
  },
  {
    id: 3, tipo: 'allievo',
    nome: 'Chiara', cognome: 'Esposito',
    email: 'chiara.esposito@gmail.com', tel: '333 7778899',
    nato: '1998-12-22', cf: 'SPSCHI98T62D969C',
    indirizzo: 'Via San Lorenzo 7, Genova',
    stato: 'attivo', col: 'amber', corsi: [3],
    pagamenti: [],
  },
  {
    id: 4, tipo: 'allievo',
    nome: 'Davide', cognome: 'Lombardi',
    email: 'davide.lombardi@gmail.com', tel: '346 0001122',
    nato: '2005-07-11', cf: 'LMBDVD05L11D969D',
    indirizzo: 'Corso Italia 22, Genova',
    stato: 'attivo', col: 'teal', corsi: [1, 2, 5],
    pagamenti: [],
  },
  {
    id: 5, tipo: 'allievo',
    nome: 'Elena', cognome: 'Martinelli',
    email: 'elena.martinelli@gmail.com', tel: '340 3334455',
    nato: '2014-03-29', cf: 'MRTLNE14C69D969E',
    indirizzo: 'Via XX Settembre 14, Genova',
    stato: 'attivo', col: 'violet', corsi: [4],
    pagamenti: [],
  },
  {
    id: 6, tipo: 'allievo',
    nome: 'Andrea', cognome: 'Romano',
    email: 'andrea.romano@gmail.com', tel: '335 6667788',
    nato: '2001-01-15', cf: 'RMNNDR01A15D969F',
    indirizzo: 'Via Prè 9, Genova',
    stato: 'sospeso', col: 'slate', corsi: [3],
    pagamenti: [],
  },
  {
    id: 7, tipo: 'allievo',
    nome: 'Francesca', cognome: 'Ferrari',
    email: 'francesca.ferrari@gmail.com', tel: '348 9990011',
    nato: '2009-06-07', cf: 'FRRFNC09H47D969G',
    indirizzo: 'Via Sestri 5, Genova',
    stato: 'attivo', col: 'green', corsi: [1, 3],
    pagamenti: [],
  },
]

// ── Pagamenti ─────────────────────────────────────────────────────────────────

export const RIGHE: Riga[] = [
  // Allievi — pagati
  {
    id: 1, tipo: 'allievo', soggetto: 'Sofia Russo', col: 'rose',
    corso: 'Pianoforte Bambini', desc: '1ª Rata — Pianoforte Bambini',
    scadenza: '2024-10-15', totale: 160, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2024-10-10', importo: 160, metodo: 'bonifico', note: '' }],
  },
  {
    id: 2, tipo: 'allievo', soggetto: 'Sofia Russo', col: 'rose',
    corso: 'Pianoforte Bambini', desc: '2ª Rata — Pianoforte Bambini',
    scadenza: '2025-01-15', totale: 160, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2025-01-12', importo: 160, metodo: 'bonifico', note: '' }],
  },
  {
    id: 3, tipo: 'allievo', soggetto: 'Sofia Russo', col: 'rose',
    corso: 'Pianoforte Bambini', desc: '3ª Rata — Pianoforte Bambini',
    scadenza: '2025-04-15', totale: 160, stato: 'futuro', conto: 'banca',
    versamenti: [],
  },
  {
    id: 4, tipo: 'allievo', soggetto: 'Matteo Conti', col: 'blue',
    corso: 'Chitarra Classica', desc: '1ª Rata — Chitarra Classica',
    scadenza: '2024-10-15', totale: 150, stato: 'pagato', conto: 'cassa',
    versamenti: [{ data: '2024-10-08', importo: 150, metodo: 'contanti', note: '' }],
  },
  {
    id: 5, tipo: 'allievo', soggetto: 'Matteo Conti', col: 'blue',
    corso: 'Chitarra Classica', desc: '2ª Rata — Chitarra Classica',
    scadenza: '2025-01-15', totale: 150, stato: 'scaduto', conto: 'cassa',
    versamenti: [],
  },
  {
    id: 6, tipo: 'allievo', soggetto: 'Chiara Esposito', col: 'amber',
    corso: 'Canto Moderno', desc: '1ª Rata — Canto Moderno',
    scadenza: '2024-10-01', totale: 130, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2024-09-28', importo: 130, metodo: 'pos', note: '' }],
  },
  {
    id: 7, tipo: 'allievo', soggetto: 'Chiara Esposito', col: 'amber',
    corso: 'Canto Moderno', desc: '2ª Rata — Canto Moderno',
    scadenza: '2024-12-01', totale: 130, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2024-11-29', importo: 130, metodo: 'pos', note: '' }],
  },
  {
    id: 8, tipo: 'allievo', soggetto: 'Chiara Esposito', col: 'amber',
    corso: 'Canto Moderno', desc: '3ª Rata — Canto Moderno',
    scadenza: '2025-02-01', totale: 130, stato: 'scaduto', conto: 'banca',
    versamenti: [{ data: '2025-02-10', importo: 60, metodo: 'bonifico', note: 'Parziale' }],
  },
  {
    id: 9, tipo: 'allievo', soggetto: 'Elena Martinelli', col: 'violet',
    corso: 'Violino', desc: 'Acconto iscrizione — Violino',
    scadenza: '2024-09-01', totale: 200, stato: 'pagato', conto: 'cassa',
    versamenti: [{ data: '2024-08-30', importo: 200, metodo: 'contanti', note: '' }],
  },
  {
    id: 10, tipo: 'allievo', soggetto: 'Elena Martinelli', col: 'violet',
    corso: 'Violino', desc: '1ª Rata — Violino',
    scadenza: '2024-11-01', totale: 350, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2024-10-31', importo: 350, metodo: 'bonifico', note: '' }],
  },
  {
    id: 11, tipo: 'allievo', soggetto: 'Elena Martinelli', col: 'violet',
    corso: 'Violino', desc: '2ª Rata — Violino',
    scadenza: '2025-03-01', totale: 350, stato: 'in scadenza', conto: 'banca',
    versamenti: [],
  },
  {
    id: 12, tipo: 'allievo', soggetto: 'Davide Lombardi', col: 'teal',
    corso: 'Pianoforte Bambini', desc: '1ª Rata — Pianoforte Bambini',
    scadenza: '2024-10-15', totale: 160, stato: 'scaduto', conto: 'banca',
    versamenti: [],
  },
  // Stipendi insegnanti
  {
    id: 13, tipo: 'insegnante', soggetto: 'Marco Ferretti', col: 'blue',
    corso: '', desc: 'Stipendio Gennaio 2025',
    scadenza: '2025-01-31', totale: 1400, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2025-01-31', importo: 1400, metodo: 'bonifico', note: '' }],
  },
  {
    id: 14, tipo: 'insegnante', soggetto: 'Giulia Morandi', col: 'rose',
    corso: '', desc: 'Stipendio Gennaio 2025',
    scadenza: '2025-01-31', totale: 1200, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2025-01-31', importo: 1200, metodo: 'bonifico', note: '' }],
  },
  {
    id: 15, tipo: 'insegnante', soggetto: 'Marco Ferretti', col: 'blue',
    corso: '', desc: 'Stipendio Febbraio 2025',
    scadenza: '2025-02-28', totale: 1400, stato: 'in scadenza', conto: 'banca',
    versamenti: [],
  },
  // Generico
  {
    id: 16, tipo: 'generico', soggetto: '', col: 'slate',
    corso: '', categoria: 'Attrezzatura', desc: 'Acquisto pianoforte digitale',
    scadenza: '2025-01-10', totale: 850, stato: 'pagato', conto: 'banca',
    versamenti: [{ data: '2025-01-10', importo: 850, metodo: 'bonifico', note: 'Yamaha P-145' }],
  },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

export function getKpiDashboard() {
  const allievi = ALLIEVI.filter(a => a.stato === 'attivo').length
  const corsi = CORSI.filter(c => c.stato === 'attivo').length
  const incasso = RIGHE
    .filter(r => r.tipo === 'allievo')
    .reduce((s, r) => s + r.versamenti.reduce((sv, v) => sv + v.importo, 0), 0)
  const scaduto = RIGHE
    .filter(r => r.stato === 'scaduto')
    .reduce((s, r) => s + (r.totale - r.versamenti.reduce((sv, v) => sv + v.importo, 0)), 0)
  return { allievi, corsi, incasso, scaduto }
}
