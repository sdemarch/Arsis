import React from 'react'
import type { TipoTransazione } from '../../../types'
import styles from './TypePill.module.css'

interface TypePillProps {
  tipo: TipoTransazione
  className?: string
}

const LABELS: Record<TipoTransazione, string> = {
  allievo: 'Allievo',
  insegnante: 'Insegnante',
  generico: 'Generico',
}

export function TypePill({ tipo, className = '' }: TypePillProps) {
  return (
    <span className={[styles.pill, styles[tipo], className].join(' ').trim()}>
      {LABELS[tipo]}
    </span>
  )
}
