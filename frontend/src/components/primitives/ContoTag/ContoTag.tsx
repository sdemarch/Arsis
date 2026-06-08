import React from 'react'
import type { ContoType } from '../../../types'
import styles from './ContoTag.module.css'

interface ContoTagProps {
  type: ContoType
  className?: string
}

export function ContoTag({ type, className = '' }: ContoTagProps) {
  return (
    <span className={[styles.tag, styles[type], className].join(' ').trim()}>
      {type === 'banca' ? '🏦 Banca' : '💵 Cassa'}
    </span>
  )
}
