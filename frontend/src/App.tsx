import React, { useState } from 'react'
import { AppShell } from './components/layout/AppShell/AppShell'
import { Sidebar } from './components/layout/Sidebar/Sidebar'
import { Topbar } from './components/layout/Topbar/Topbar'
import { useTheme } from './hooks/useTheme'
import { RIGHE } from './mock/data'

import Dashboard from './pages/Dashboard'
import Anagrafica from './pages/Anagrafica'
import Corsi from './pages/Corsi'
import Pagamenti from './pages/Pagamenti'
import Impostazioni from './pages/Impostazioni'

type PageId = 'dashboard' | 'anagrafica' | 'corsi' | 'pagamenti' | 'impostazioni'

const BREADCRUMBS: Record<PageId, string[]> = {
  dashboard:    ['Arsis', 'Dashboard'],
  anagrafica:   ['Arsis', 'Anagrafica'],
  corsi:        ['Arsis', 'Corsi'],
  pagamenti:    ['Arsis', 'Pagamenti'],
  impostazioni: ['Arsis', 'Impostazioni'],
}

const scadutiCount = RIGHE.filter(r => r.stato === 'scaduto').length

export default function App() {
  const { theme, toggle } = useTheme()
  const [page, setPage] = useState<PageId>('dashboard')

  const breadcrumb = BREADCRUMBS[page].map(label => ({ label }))

  const pageContent = {
    dashboard:    <Dashboard />,
    anagrafica:   <Anagrafica />,
    corsi:        <Corsi />,
    pagamenti:    <Pagamenti />,
    impostazioni: <Impostazioni />,
  }[page]

  return (
    <AppShell
      sidebar={
        <Sidebar
          activeItem={page}
          onNavigate={id => setPage(id as PageId)}
          theme={theme}
          onThemeToggle={toggle}
          scadutiCount={scadutiCount}
        />
      }
      topbar={<Topbar breadcrumb={breadcrumb} />}
    >
      {pageContent}
    </AppShell>
  )
}
