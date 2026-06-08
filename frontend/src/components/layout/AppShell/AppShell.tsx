import React from 'react'
import styles from './AppShell.module.css'

interface AppShellProps {
  sidebar: React.ReactNode
  topbar: React.ReactNode
  children: React.ReactNode
}

export function AppShell({ sidebar, topbar, children }: AppShellProps) {
  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>{sidebar}</aside>
      <div className={styles.main}>
        <header className={styles.topbar}>{topbar}</header>
        <main className={styles.content}>{children}</main>
      </div>
    </div>
  )
}
