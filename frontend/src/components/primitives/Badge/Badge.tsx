import React from 'react'
import styles from './Badge.module.css'

type BadgeVariant = 'green' | 'yellow' | 'red' | 'blue' | 'neutral'

interface BadgeProps {
  variant: BadgeVariant
  dot?: boolean
  children: React.ReactNode
  className?: string
}

export function Badge({ variant, dot = true, children, className = '' }: BadgeProps) {
  return (
    <span className={[styles.badge, styles[variant], className].join(' ').trim()}>
      {dot && <span className={styles.dot} />}
      {children}
    </span>
  )
}
