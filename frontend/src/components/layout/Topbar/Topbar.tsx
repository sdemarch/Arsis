import React from 'react'
import styles from './Topbar.module.css'

interface BreadcrumbItem {
  label: string
}

interface TopbarProps {
  breadcrumb: BreadcrumbItem[]
  actions?: React.ReactNode
}

export function Topbar({ breadcrumb, actions }: TopbarProps) {
  return (
    <div className={styles.topbar}>
      <div className={styles.breadcrumb}>
        {breadcrumb.map((item, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span className={styles.sep}>/</span>}
            <span className={i === breadcrumb.length - 1 ? styles.current : styles.ancestor}>
              {item.label}
            </span>
          </React.Fragment>
        ))}
      </div>
      {actions && <div className={styles.actions}>{actions}</div>}
    </div>
  )
}
