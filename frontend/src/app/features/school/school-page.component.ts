import { ChangeDetectionStrategy, Component } from '@angular/core';

import schoolData from '../../../assets/mock/school.json';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-school-page',
  imports: [PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Scuola" title="Scuola di musica" description="Corsi, iscrizioni, lezioni e registro presenze.">
      <button class="button button--primary" type="button">＋ Nuovo corso</button>
    </arsis-page-header>

    <section class="school-summary">
      <div><strong>{{ summary.courses }}</strong><span>Corsi attivi</span></div><div><strong>{{ summary.students }}</strong><span>Allievi iscritti</span></div><div><strong>{{ summary.lessonsThisMonth }}</strong><span>Lezioni questo mese</span></div><div><strong>{{ summary.attendanceRate }}</strong><span>Presenza media</span></div>
    </section>

    <div class="section-heading"><div><p class="eyebrow">Offerta formativa</p><h2>Corsi attivi</h2></div><button class="button button--secondary">Tutti i corsi →</button></div>
    <section class="course-grid">
      @for (course of courses; track course.id) {
        <article class="course-card card" [style.--course-color]="course.color" [style.--course-background]="course.background">
          <div class="course-card__accent"></div>
          <div class="course-card__body"><header><span>{{ course.mode }}</span><button>•••</button></header><h3>{{ course.name }}</h3><p>{{ course.teacher }}</p><dl><div><dt>Allievi</dt><dd>{{ course.students }}</dd></div><div><dt>Orario</dt><dd>{{ course.schedule }}</dd></div><div><dt>Tariffa annua</dt><dd>{{ course.fee }}</dd></div></dl></div>
        </article>
      }
    </section>

    <div class="section-heading lesson-heading"><div><p class="eyebrow">Agenda</p><h2>Lezioni di oggi</h2></div><button class="button button--secondary">＋ Nuova lezione</button></div>
    <div class="table-shell">
      <table><thead><tr><th>Data e ora</th><th>Corso</th><th>Insegnante</th><th>Registro presenze</th><th></th></tr></thead><tbody>
        @for (lesson of lessons; track lesson.time) { <tr><td><div class="date-time"><strong>{{ lesson.time }}</strong><span>{{ lesson.date }}</span></div></td><td><strong>{{ lesson.course }}</strong></td><td>{{ lesson.teacher }}</td><td><span class="status-badge" [class.status-badge--success]="lesson.attendance === 'Completa'">{{ lesson.attendance }}</span></td><td><button class="row-menu">•••</button></td></tr> }
      </tbody></table>
    </div>
  `,
  styles: `
    .school-summary { background: var(--sidebar-bg); border-radius: var(--radius-lg); color: var(--sidebar-active); display: grid; grid-template-columns: repeat(4, 1fr); margin-bottom: var(--sp-8); padding: var(--sp-5); }
    .school-summary div { border-right: var(--border-thin) solid var(--sidebar-border); display: grid; gap: var(--sp-1); padding: 0 var(--sp-5); }
    .school-summary div:last-child { border: 0; }
    .school-summary strong { font-family: var(--font-display); font-size: var(--text-2xl); }
    .school-summary span { color: var(--sidebar-text); font-size: var(--text-sm); }
    .section-heading { align-items: end; display: flex; justify-content: space-between; margin-bottom: var(--sp-4); }
    .section-heading h2 { font-family: var(--font-sans); font-size: var(--text-lg); margin: 0; }
    .eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    .course-grid { display: grid; gap: var(--sp-4); grid-template-columns: repeat(4, 1fr); }
    .course-card { display: grid; grid-template-columns: 5px 1fr; overflow: hidden; }
    .course-card__accent { background: var(--course-color); }
    .course-card__body { padding: var(--sp-5); }
    .course-card header { align-items: center; display: flex; justify-content: space-between; }
    .course-card header span { background: var(--course-background); border-radius: var(--radius-full); color: var(--course-color); font-size: var(--text-xs); padding: var(--sp-1) var(--sp-2); }
    .course-card button, .row-menu { background: transparent; border: 0; color: var(--text-tertiary); cursor: pointer; }
    .course-card h3 { font-family: var(--font-sans); font-size: var(--text-lg); margin: var(--sp-4) 0 var(--sp-1); }
    .course-card p { color: var(--text-secondary); margin: 0 0 var(--sp-5); }
    .course-card dl { display: grid; gap: var(--sp-2); margin: 0; }
    .course-card dl div { display: flex; justify-content: space-between; }
    .course-card dt { color: var(--text-tertiary); font-size: var(--text-sm); }
    .course-card dd { font-size: var(--text-sm); font-weight: var(--weight-medium); margin: 0; }
    .lesson-heading { margin-top: var(--sp-8); }
    .date-time { display: grid; }
    .date-time span { color: var(--text-tertiary); font-size: var(--text-xs); }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SchoolPageComponent {
  protected readonly summary = schoolData.summary;
  protected readonly courses = schoolData.courses;
  protected readonly lessons = schoolData.lessons;
}

