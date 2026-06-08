import React, { useEffect, useRef } from 'react'
import styles from './Modal.module.css'

interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  footerLeft?: React.ReactNode
  actions: React.ReactNode
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
}

export function Modal({ open, onClose, title, footerLeft, actions, size = 'md', children }: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className={styles.backdrop} onMouseDown={(e) => { if (e.target === e.currentTarget) onClose() }}>
      <div className={[styles.dialog, styles[size]].join(' ')} ref={dialogRef} role="dialog" aria-modal="true">
        <div className={styles.header}>
          <h2 className={styles.title}>{title}</h2>
          <button className={styles.close} onClick={onClose} aria-label="Chiudi">✕</button>
        </div>
        <div className={styles.body}>{children}</div>
        <div className={styles.footer}>
          <div className={styles.footerLeft}>{footerLeft}</div>
          <div className={styles.footerRight}>{actions}</div>
        </div>
      </div>
    </div>
  )
}
