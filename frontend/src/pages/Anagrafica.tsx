import React, { useState } from 'react'
import { ALLIEVI, INSEGNANTI } from '../mock/data'
import { Avatar } from '../components/primitives/Avatar/Avatar'
import { Badge } from '../components/primitives/Badge/Badge'
import styles from './Anagrafica.module.css'

type Tab = 'allievi' | 'insegnanti'

export default function Anagrafica() {
  const [tab, setTab] = useState<Tab>('allievi')
  const [q, setQ] = useState('')

  const allievi = ALLIEVI.filter(a =>
    `${a.nome} ${a.cognome}`.toLowerCase().includes(q.toLowerCase())
  )
  const insegnanti = INSEGNANTI.filter(i =>
    `${i.nome} ${i.cognome}`.toLowerCase().includes(q.toLowerCase())
  )

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Anagrafica</h1>
        <input
          className={styles.search}
          placeholder="Cerca per nome…"
          value={q}
          onChange={e => setQ(e.target.value)}
        />
      </div>

      <div className={styles.tabs}>
        <button className={[styles.tab, tab === 'allievi' ? styles.active : ''].join(' ')} onClick={() => setTab('allievi')}>
          Allievi <span className={styles.count}>{ALLIEVI.length}</span>
        </button>
        <button className={[styles.tab, tab === 'insegnanti' ? styles.active : ''].join(' ')} onClick={() => setTab('insegnanti')}>
          Insegnanti <span className={styles.count}>{INSEGNANTI.length}</span>
        </button>
      </div>

      <div className={styles.list}>
        {tab === 'allievi' && allievi.map(a => (
          <div key={a.id} className={styles.row}>
            <Avatar name={`${a.nome} ${a.cognome}`} color={a.col} size="md" />
            <div className={styles.info}>
              <p className={styles.name}>{a.nome} {a.cognome}</p>
              <p className={styles.sub}>{a.email}</p>
            </div>
            <Badge variant={a.stato === 'attivo' ? 'green' : 'neutral'}>{a.stato}</Badge>
            <span className={styles.corsi}>{a.corsi.length} {a.corsi.length === 1 ? 'corso' : 'corsi'}</span>
          </div>
        ))}
        {tab === 'insegnanti' && insegnanti.map(i => (
          <div key={i.id} className={styles.row}>
            <Avatar name={`${i.nome} ${i.cognome}`} color={i.col} size="md" />
            <div className={styles.info}>
              <p className={styles.name}>{i.nome} {i.cognome}</p>
              <p className={styles.sub}>{i.email}</p>
            </div>
            <Badge variant="green">{i.stato}</Badge>
            <span className={styles.corsi}>{i.corsi.length} {i.corsi.length === 1 ? 'corso' : 'corsi'}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
