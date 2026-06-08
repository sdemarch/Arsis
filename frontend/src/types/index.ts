export type AvatarColor = 'blue' | 'green' | 'amber' | 'rose' | 'violet' | 'teal' | 'orange' | 'slate'
export type ContoType = 'banca' | 'cassa'
export type TipoTransazione = 'allievo' | 'insegnante' | 'generico'
export type StatoPagamento = 'pagato' | 'in scadenza' | 'scaduto' | 'futuro'
export type StatoPersona = 'attivo' | 'sospeso'
export type RateMode = '3rate' | '4rate' | 'custom'
export type PersonType = 'allievo' | 'insegnante'

export interface Rata {
  desc: string
  data: string // ISO date
  importo: number
}

export interface PianoRate {
  mode: RateMode
  quota: number
  rate: Rata[]
}

export interface Corso {
  id: number
  nome: string
  tipo: 'collettivo' | 'individuale'
  insegnante: string
  giorno: string
  orario: string
  aula: string
  stato: 'attivo' | 'sospeso' | 'concluso'
  color: number // indice in COURSE_COLORS
  allievi: number
  piano: PianoRate
}

export interface Persona {
  id: number
  nome: string
  email: string
  tel: string
  nato: string
  cf: string
  indirizzo: string
  stato: StatoPersona
  col: AvatarColor
  corsi: number[] // array di Corso.id
}

export interface Allievo extends Persona {
  tipo: 'allievo'
  pagamenti: Riga[]
}

export interface Insegnante extends Persona {
  tipo: 'insegnante'
  stipendio: number
  pagamenti: Riga[]
}

export interface Versamento {
  data: string
  importo: number
  metodo: string
  note: string
}

export interface Riga {
  id: number
  tipo: TipoTransazione
  soggetto: string
  col: AvatarColor
  corso: string
  categoria?: string
  desc: string
  scadenza: string
  totale: number
  stato: StatoPagamento
  conto: ContoType
  versamenti: Versamento[]
}

export interface PersonFormData {
  nome: string
  email: string
  tel: string
  nato: string
  cf: string
  indirizzo: string
  stato: StatoPersona
  col: AvatarColor
  corsi: number[]
  tipo: PersonType
  stipendio?: number
}

export interface InlineAddData {
  desc: string
  tipo: TipoTransazione
  conto: ContoType
  data: string // ISO date
  categoria: string
  importo: number
}
