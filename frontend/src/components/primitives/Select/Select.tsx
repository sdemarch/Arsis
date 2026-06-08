import React from 'react'
import styles from './Select.module.css'

interface SelectOption { value: string; label: string }

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: SelectOption[]
  error?: string
  required?: boolean
}

export function Select({ label, options, error, required, className = '', ...rest }: SelectProps) {
  return (
    <div className={styles.field}>
      {label && (
        <label className={styles.label}>
          {label}
          {required && <span className={styles.req}>*</span>}
        </label>
      )}
      <div className={[styles.wrap, error ? styles.hasError : ''].join(' ')}>
        <select className={[styles.select, className].join(' ')} {...rest}>
          {options.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>
      {error && <span className={styles.error}>{error}</span>}
    </div>
  )
}
