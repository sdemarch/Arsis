import React from 'react'
import { fmtEur } from '../../../utils/formatters'
import styles from './ProgressBar.module.css'

interface ProgressBarProps {
  value: number       // 0–100
  showLabel?: boolean
  showSub?: boolean
  paid?: number
  total?: number
  className?: string
}

export function ProgressBar({
  value,
  showLabel = true,
  showSub = true,
  paid,
  total,
  className = '',
}: ProgressBarProps) {
  const color = value >= 100 ? 'success' : value >= 50 ? 'accent' : 'warn'
  return (
    <div className={[styles.wrap, className].join(' ').trim()}>
      <div className={styles.row}>
        <div className={styles.track}>
          <div
            className={[styles.fill, styles[color]].join(' ')}
            style={{ width: `${Math.min(100, value)}%` }}
          />
        </div>
        {showLabel && <span className={styles.label}>{value}%</span>}
      </div>
      {showSub && paid !== undefined && total !== undefined && (
        <span className={styles.sub}>{fmtEur(paid)} / {fmtEur(total)}</span>
      )}
    </div>
  )
}
