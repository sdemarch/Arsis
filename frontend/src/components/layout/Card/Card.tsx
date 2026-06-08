import React from 'react'
import styles from './Card.module.css'

interface CardProps {
  title?: string
  action?: React.ReactNode
  padding?: 'sm' | 'md'
  noBorder?: boolean
  children: React.ReactNode
  className?: string
}

export function Card({ title, action, padding = 'md', noBorder = false, children, className = '' }: CardProps) {
  return (
    <div className={[styles.card, noBorder ? styles.noBorder : '', className].join(' ').trim()}>
      {(title || action) && (
        <div className={styles.header}>
          {title && <h3 className={styles.title}>{title}</h3>}
          {action && <div className={styles.action}>{action}</div>}
        </div>
      )}
      <div className={[styles.body, styles[padding]].join(' ')}>{children}</div>
    </div>
  )
}
