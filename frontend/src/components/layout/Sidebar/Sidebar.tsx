import React from 'react'
import { Avatar } from '../../primitives/Avatar/Avatar'
import logo from '../../../assets/img/logo/icon-128x128.png'
import styles from './Sidebar.module.css'

// Icons (inline SVG minimali — sostituibili con lucide-react)
const icons = {
  dashboard: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
    </svg>
  ),
  people: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  ),
  music: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
    </svg>
  ),
  payments: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
      <line x1="1" y1="10" x2="23" y2="10"/>
    </svg>
  ),
  settings: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
    </svg>
  ),
  sun: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  ),
  moon: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  ),
}

interface NavItem {
  id: string
  label: string
  icon: React.ReactNode
  badge?: number
}

interface SidebarProps {
  activeItem: string
  onNavigate: (id: string) => void
  theme: 'light' | 'dark'
  onThemeToggle: () => void
  scadutiCount?: number
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard',   label: 'Dashboard',   icon: icons.dashboard },
  { id: 'anagrafica',  label: 'Anagrafica',  icon: icons.people },
  { id: 'corsi',       label: 'Corsi',       icon: icons.music },
  { id: 'pagamenti',   label: 'Pagamenti',   icon: icons.payments },
  { id: 'impostazioni',label: 'Impostazioni',icon: icons.settings },
]

export function Sidebar({ activeItem, onNavigate, theme, onThemeToggle, scadutiCount = 0 }: SidebarProps) {
  return (
    <nav className={styles.sidebar}>
      {/* Brand */}
      <div className={styles.brand}>
        <img src={logo} className={styles.brandMark} alt="Arsis" />
        <span className={styles.brandName}>Arsis</span>
      </div>

      <div className={styles.divider} />

      {/* Nav */}
      <div className={styles.nav}>
        <span className={styles.sectionLabel}>Menu</span>
        {NAV_ITEMS.map(item => {
          const badge = item.id === 'pagamenti' ? scadutiCount : item.badge
          return (
            <button
              key={item.id}
              className={[styles.navItem, activeItem === item.id ? styles.active : ''].join(' ')}
              onClick={() => onNavigate(item.id)}
            >
              <span className={styles.navIcon}>{item.icon}</span>
              <span className={styles.navLabel}>{item.label}</span>
              {badge ? <span className={styles.badge}>{badge}</span> : null}
            </button>
          )
        })}
      </div>

      {/* Footer */}
      <div className={styles.footer}>
        <div className={styles.divider} />
        <button className={styles.themeToggle} onClick={onThemeToggle} title="Cambia tema">
          {theme === 'light' ? icons.moon : icons.sun}
          <span>{theme === 'light' ? 'Tema scuro' : 'Tema chiaro'}</span>
        </button>
        <div className={styles.user}>
          <Avatar name="Admin Arsis" color="blue" size="sm" />
          <div className={styles.userInfo}>
            <span className={styles.userName}>Admin</span>
            <span className={styles.userRole}>Amministratore</span>
          </div>
        </div>
      </div>
    </nav>
  )
}
