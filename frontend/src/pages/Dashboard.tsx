import React from 'react'
import { fmtEur } from '../utils/formatters'
import { getKpiDashboard, RIGHE, CORSI } from '../mock/data'
import { Card } from '../components/layout/Card/Card'
import { Badge } from '../components/primitives/Badge/Badge'
import styles from './Dashboard.module.css'

const kpi = getKpiDashboard()

const scaduti = RIGHE.filter(r => r.stato === 'scaduto')
const inScadenza = RIGHE.filter(r => r.stato === 'in scadenza')

export default function Dashboard() {
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Dashboard</h1>
        <p className={styles.subtitle}>Panoramica della scuola</p>
      </div>

      {/* KPI */}
      <div className={styles.kpiGrid}>
        <div className={styles.kpi}>
          <span className={styles.kpiLabel}>Allievi attivi</span>
          <span className={styles.kpiValue}>{kpi.allievi}</span>
        </div>
        <div className={styles.kpi}>
          <span className={styles.kpiLabel}>Corsi attivi</span>
          <span className={styles.kpiValue}>{kpi.corsi}</span>
        </div>
        <div className={[styles.kpi, styles.kpiAccent].join(' ')}>
          <span className={styles.kpiLabel}>Incasso allievi</span>
          <span className={styles.kpiValue}>{fmtEur(kpi.incasso)}</span>
        </div>
        <div className={[styles.kpi, styles.kpiDanger].join(' ')}>
          <span className={styles.kpiLabel}>Scaduto non pagato</span>
          <span className={styles.kpiValue}>{fmtEur(kpi.scaduto)}</span>
        </div>
      </div>

      <div className={styles.cols}>
        {/* Rate scadute */}
        <Card title="Rate scadute" action={<Badge variant="red">{scaduti.length}</Badge>}>
          {scaduti.length === 0 ? (
            <p className={styles.empty}>Nessuna rata scaduta</p>
          ) : (
            <div className={styles.list}>
              {scaduti.map(r => (
                <div key={r.id} className={styles.listRow}>
                  <div>
                    <p className={styles.listPrimary}>{r.soggetto}</p>
                    <p className={styles.listSub}>{r.desc}</p>
                  </div>
                  <span className={styles.listAmount}>{fmtEur(r.totale)}</span>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* In scadenza */}
        <Card title="In scadenza" action={<Badge variant="yellow">{inScadenza.length}</Badge>}>
          {inScadenza.length === 0 ? (
            <p className={styles.empty}>Nessuna rata in scadenza</p>
          ) : (
            <div className={styles.list}>
              {inScadenza.map(r => (
                <div key={r.id} className={styles.listRow}>
                  <div>
                    <p className={styles.listPrimary}>{r.soggetto || r.desc}</p>
                    <p className={styles.listSub}>{r.desc}</p>
                  </div>
                  <span className={styles.listAmount}>{fmtEur(r.totale)}</span>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Corsi */}
        <Card title="Corsi attivi">
          <div className={styles.list}>
            {CORSI.filter(c => c.stato === 'attivo').map(c => (
              <div key={c.id} className={styles.listRow}>
                <div>
                  <p className={styles.listPrimary}>{c.nome}</p>
                  <p className={styles.listSub}>{c.insegnante} · {c.giorno} {c.orario}</p>
                </div>
                <span className={styles.listSub}>{c.allievi} allievi</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
