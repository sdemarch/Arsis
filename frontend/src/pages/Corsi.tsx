import React from 'react'
import { CORSI } from '../mock/data'
import { COURSE_COLORS } from '../utils/courseColors'
import { Badge } from '../components/primitives/Badge/Badge'
import { fmtEur } from '../utils/formatters'
import styles from './Corsi.module.css'

const statoVariant = (s: string) =>
  s === 'attivo' ? 'green' : s === 'sospeso' ? 'yellow' : 'neutral'

export default function Corsi() {
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Corsi</h1>
      </div>
      <div className={styles.grid}>
        {CORSI.map(corso => {
          const color = COURSE_COLORS[corso.color]
          return (
            <div key={corso.id} className={styles.card}>
              <div className={styles.stripe} style={{ background: color.hex }} />
              <div className={styles.cardBody}>
                <div className={styles.cardHeader}>
                  <div className={styles.iconWrap} style={{ background: color.bg }}>
                    <span style={{ color: color.hex, fontSize: 18 }}>♪</span>
                  </div>
                  <Badge variant={statoVariant(corso.stato) as any}>{corso.stato}</Badge>
                </div>
                <h3 className={styles.courseName}>{corso.nome}</h3>
                <p className={styles.teacher}>{corso.insegnante}</p>
                <div className={styles.tags}>
                  <span className={styles.tag}>{corso.tipo}</span>
                  <span className={styles.tag}>{corso.giorno}</span>
                  <span className={styles.tag}>{corso.orario}</span>
                </div>
                <div className={styles.stats}>
                  <div className={styles.stat}>
                    <span className={styles.statValue}>{corso.allievi}</span>
                    <span className={styles.statLabel}>allievi</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statValue}>{fmtEur(corso.piano.quota)}</span>
                    <span className={styles.statLabel}>quota annua</span>
                  </div>
                  <div className={styles.stat}>
                    <span className={styles.statValue}>{corso.piano.rate.length}</span>
                    <span className={styles.statLabel}>rate</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
