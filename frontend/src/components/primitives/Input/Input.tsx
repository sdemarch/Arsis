import React from 'react'
import styles from './Input.module.css'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  hint?: string
  error?: string
  prefix?: string
  suffix?: React.ReactNode
  required?: boolean
  size?: 'sm' | 'md'
}

export function Input({ label, hint, error, prefix, suffix, required, size = 'md', className = '', ...rest }: InputProps) {
  return (
    <div className={styles.field}>
      {label && (
        <label className={styles.label}>
          {label}
          {required && <span className={styles.req}>*</span>}
        </label>
      )}
      <div className={[styles.inputWrap, styles[size], error ? styles.hasError : ''].join(' ')}>
        {prefix && <span className={styles.prefix}>{prefix}</span>}
        <input className={[styles.input, className].join(' ')} {...rest} />
        {suffix && <span className={styles.suffix}>{suffix}</span>}
      </div>
      {error ? (
        <span className={styles.error}>{error}</span>
      ) : hint ? (
        <span className={styles.hint}>{hint}</span>
      ) : null}
    </div>
  )
}
