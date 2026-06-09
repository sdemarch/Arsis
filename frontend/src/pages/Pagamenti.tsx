import React, { useState } from 'react'
import { RIGHE } from '../mock/data'
import { Badge } from '../components/primitives/Badge/Badge'
import { Avatar } from '../components/primitives/Avatar/Avatar'
import { ContoTag } from '../components/primitives/ContoTag/ContoTag'
import { ProgressBar } from '../components/primitives/ProgressBar/ProgressBar'
import { fmtEur, fmtDate } from '../utils/formatters'
import { pagato, pct } from '../utils/calculations'
import type { StatoPagamento } from '../types'
import styles from './Pagamenti.module.css'

const badgeVariant: Record<StatoPagamento, 'green' | 'yellow' | 'red' | 'blue' | 'neutral'> = {
  'pagato': 'green',
  'in scadenza': 'yellow',
  'scaduto': 'red',
  'futuro': 'blue',
}

type Filter = 'tutti' | StatoPagamento

export default function Pagamenti() {
  const [filter, setFilter] = useState<Filter>('tutti')

  const righe = filter === 'tutti' ? RIGHE : RIGHE.filter(r => r.stato === filter)

  const totEntrate = RIGHE
    .filter(r => r.tipo === 'allievo')
    .reduce((s, r) => s + pagato(r.versamenti), 0)
  const totUscite = RIGHE
    .filter(r => r.tipo === 'insegnante')
    .reduce((s, r) => s + pagato(r.versamenti), 0)

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Pagamenti</h1>
      </div>

      {/* KPI strip */}
      <div className={styles.kpiStrip}>
        <div className={styles.kpiItem}>
          <span className={styles.kpiLabel}>Entrate allievi</span>
          <span className={[styles.kpiVal, styles.green].join(' ')}>{fmtEur(totEntrate)}</span>
        </div>
        <div className={styles.kpiDivider} />
        <div className={styles.kpiItem}>
          <span className={styles.kpiLabel}>Uscite stipendi</span>
          <span className={[styles.kpiVal, styles.red].join(' ')}>{fmtEur(totUscite)}</span>
        </div>
        <div className={styles.kpiDivider} />
        <div className={styles.kpiItem}>
          <span className={styles.kpiLabel}>Bilancio</span>
          <span className={styles.kpiVal}>{fmtEur(totEntrate - totUscite)}</span>
        </div>
      </div>

      {/* Filters */}
      <div className={styles.filters}>
        {(['tutti', 'pagato', 'in scadenza', 'scaduto', 'futuro'] as Filter[]).map(f => (
          <button
            key={f}
            className={[styles.filterBtn, filter === f ? styles.filterActive : ''].join(' ')}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Soggetto</th>
              <th>Descrizione</th>
              <th>Scadenza</th>
              <th>Conto</th>
              <th>Avanzamento</th>
              <th>Importo</th>
              <th>Stato</th>
            </tr>
          </thead>
          <tbody>
            {righe.map(r => {
              const vers = pagato(r.versamenti)
              const perc = pct(r.versamenti, r.totale)
              return (
                <tr key={r.id}>
                  <td>
                    <div className={styles.subject}>
                      {r.soggetto && <Avatar name={r.soggetto} color={r.col} size="sm" />}
                      <span>{r.soggetto || '—'}</span>
                    </div>
                  </td>
                  <td className={styles.desc}>{r.desc}</td>
                  <td className={styles.mono}>{fmtDate(r.scadenza)}</td>
                  <td><ContoTag type={r.conto} /></td>
                  <td className={styles.progress}>
                    <ProgressBar value={perc} paid={vers} total={r.totale} showSub={false} />
                  </td>
                  <td className={styles.mono}>{fmtEur(r.totale)}</td>
                  <td><Badge variant={badgeVariant[r.stato]}>{r.stato}</Badge></td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
