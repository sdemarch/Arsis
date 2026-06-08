import type { Riga, Rata, Versamento } from '../types'

export function pagato(versamenti: Versamento[]): number {
  return versamenti.reduce((sum, v) => sum + v.importo, 0)
}

export function pct(versamenti: Versamento[], totale: number): number {
  if (totale === 0) return 0
  return Math.min(100, Math.round((pagato(versamenti) / totale) * 100))
}

export function totalePiano(rate: Rata[]): number {
  return rate.reduce((sum, r) => sum + r.importo, 0)
}

export function saldiBancaCassa(righe: Riga[]) {
  let bancaEntrate = 0, bancaUscite = 0
  let cassaEntrate = 0, cassaUscite = 0

  for (const riga of righe) {
    const versato = pagato(riga.versamenti)
    if (riga.tipo === 'allievo') {
      if (riga.conto === 'banca') bancaEntrate += versato
      else cassaEntrate += versato
    } else if (riga.tipo === 'insegnante') {
      if (riga.conto === 'banca') bancaUscite += versato
      else cassaUscite += versato
    } else {
      // generico: positive totale = entrata, negative = uscita
      if (riga.totale >= 0) {
        if (riga.conto === 'banca') bancaEntrate += versato
        else cassaEntrate += versato
      } else {
        if (riga.conto === 'banca') bancaUscite += versato
        else cassaUscite += versato
      }
    }
  }

  return { bancaEntrate, bancaUscite, cassaEntrate, cassaUscite }
}
