import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useTheme } from './hooks/useTheme'

// Pages (lazy-loadable in future)
import Dashboard from './pages/Dashboard'
import Anagrafica from './pages/Anagrafica'
import Corsi from './pages/Corsi'
import Pagamenti from './pages/Pagamenti'
import Impostazioni from './pages/Impostazioni'

export default function App() {
  useTheme() // applica data-theme su <html>

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/anagrafica" element={<Anagrafica />} />
      <Route path="/corsi" element={<Corsi />} />
      <Route path="/pagamenti" element={<Pagamenti />} />
      <Route path="/impostazioni" element={<Impostazioni />} />
    </Routes>
  )
}
