import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthService } from '../../core/auth/auth.service';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { DashboardService, DashboardSummary } from './dashboard.service';

const TYPE_LABELS = { rehearsal: 'Prova', concert: 'Concerto', event: 'Evento' } as const;

const QUICK_ACTIONS = [
  { label: 'Nuova persona', path: '/people/new', symbol: '+' },
  { label: 'Nuova attività', path: '/activities/new', symbol: '+' },
  { label: 'Nuova lezione', path: '/school/lessons/new', symbol: '+' },
  { label: 'Apri archivio', path: '/archive', symbol: '↗' },
] as const;

interface Loaded {
  readonly summary: DashboardSummary | null;
  readonly failed: boolean;
}

@Component({
  selector: 'arsis-home-page',
  imports: [PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header
      eyebrow="Dashboard"
      [title]="greeting()"
      description="Qui trovi le informazioni operative della tua associazione."
    ><a class="button button--primary" routerLink="/people/new">＋ Nuova persona</a></arsis-page-header>
    @if (state()?.failed) { <p class="error" role="alert">Impossibile caricare il riepilogo: riprova più tardi.</p> }
    <section class="metrics" aria-label="Riepilogo persone attive">
      @for (metric of metrics(); track metric.label) {
        <a class="metric-card" [routerLink]="metric.path" [queryParams]="metric.query">
          <div class="metric-card__top"><span>{{ metric.label }}</span><i>{{ metric.icon }}</i></div>
          <strong>{{ metric.value }}</strong><small>{{ metric.detail }}</small>
        </a>
      }
    </section>
    <section class="dashboard-grid">
      <article class="panel panel--wide">
        <header><div><p class="section-label">Agenda</p><h2>Prossime attività</h2></div><a routerLink="/activities/calendar">Vedi calendario →</a></header>
        <div class="activity-list">
          @for (activity of activities(); track activity.id) {
            <a class="activity-row" [routerLink]="['/activities', activity.id]">
              <time><strong>{{ activity.day }}</strong><span>{{ activity.month }}</span></time>
              <div><strong>{{ activity.title }}</strong><span>{{ activity.time }}@if (activity.location) { · {{ activity.location }} } · {{ activity.participant_count }} convocati</span></div>
              <span class="type-pill">{{ activity.typeLabel }}</span>
            </a>
          } @empty {
            <p class="empty">Nessuna attività in programma.</p>
          }
        </div>
      </article>
      <article class="panel">
        <header><div><p class="section-label">Oggi</p><h2>Lezioni</h2></div><a routerLink="/school/lessons">Tutte →</a></header>
        <div class="lesson-list">
          @for (lesson of lessons(); track lesson.id) {
            <a class="lesson-row" [routerLink]="['/school/lessons', lesson.id, 'attendance']">
              <time>{{ lesson.time }}</time>
              <div><strong><i [style.background]="lesson.course_color"></i>{{ lesson.course_name }}</strong><span>{{ lesson.teacher_name }} · {{ lesson.students }} {{ lesson.students === 1 ? 'allievo' : 'allievi' }}</span></div>
              <small [class.done]="lesson.complete">{{ lesson.complete ? 'Registro completo' : lesson.recorded + '/' + lesson.students + ' presenze' }}</small>
            </a>
          } @empty {
            <p class="empty">Nessuna lezione oggi.</p>
          }
        </div>
      </article>
      <article class="panel panel--actions">
        <header><div><p class="section-label">Scorciatoie</p><h2>Azioni rapide</h2></div></header>
        <div class="quick-grid">
          @for (action of quickActions; track action.label) { <a [routerLink]="action.path"><i>{{ action.symbol }}</i><span>{{ action.label }}</span></a> }
        </div>
      </article>
    </section>
  `,
  styles: `
    .metrics { display: grid; gap: var(--sp-4); grid-template-columns: repeat(4, 1fr); margin-bottom: var(--sp-6); }
    .metric-card, .panel { background: var(--bg-surface); border: var(--border-thin) solid var(--border-subtle); border-radius: var(--radius-lg); box-shadow: var(--shadow-xs); }
    .metric-card { color: inherit; display: grid; gap: var(--sp-1); padding: var(--sp-5); text-decoration: none; }
    .metric-card:hover { box-shadow: var(--shadow-sm); }
    .metric-card__top { align-items: center; display: flex; justify-content: space-between; }
    .metric-card__top i { align-items: center; background: var(--color-accent-soft); border-radius: var(--radius-md); color: var(--color-accent-hover); display: flex; font-size: var(--text-xs); font-style: normal; height: 32px; justify-content: center; width: 32px; }
    .metric-card span, .panel p { color: var(--text-secondary); }
    .metric-card > strong { font-family: var(--font-display); font-size: var(--text-2xl); font-weight: var(--weight-semi); }
    .metric-card small { color: var(--text-tertiary); }
    .dashboard-grid { display: grid; gap: var(--sp-6); grid-template-columns: 1.35fr 1fr; }
    .panel { min-height: var(--panel-min-height); padding: var(--sp-6); }
    .panel h2 { font-family: var(--font-sans); font-size: var(--text-lg); margin: 0 0 var(--sp-4); }
    .panel header { align-items: start; display: flex; justify-content: space-between; }
    .panel header a { color: var(--color-accent-hover); font-size: var(--text-sm); text-decoration: none; }
    .section-label { font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    .activity-list, .lesson-list { display: grid; }
    .activity-row, .lesson-row { color: inherit; text-decoration: none; }
    .activity-row:hover, .lesson-row:hover { background: var(--bg-raised); }
    .activity-row { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-4); grid-template-columns: 44px 1fr auto; padding: var(--sp-3) 0; }
    .activity-row time { align-items: center; background: var(--bg-raised); border-radius: var(--radius-md); display: flex; flex-direction: column; font-family: var(--font-sans); padding: var(--sp-1); }
    .activity-row time strong { font-family: var(--font-display); font-size: var(--text-lg); }
    .activity-row time span { color: var(--text-tertiary); font-size: var(--text-xs); }
    .activity-row > div, .lesson-row > div { display: grid; }
    .activity-row > div span, .lesson-row span { color: var(--text-secondary); font-size: var(--text-sm); }
    .type-pill { background: var(--color-accent-soft); border-radius: var(--radius-full); color: var(--color-accent-hover); font-size: var(--text-xs); padding: var(--sp-1) var(--sp-2); }
    .lesson-row { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-4); grid-template-columns: 48px 1fr auto; padding: var(--sp-4) 0; }
    .lesson-row time { color: var(--color-accent-hover); font-size: var(--text-sm); }
    .lesson-row i { border-radius: var(--radius-full); display: inline-block; height: 8px; margin-right: var(--sp-1); width: 8px; }
    .lesson-row small { color: var(--text-tertiary); font-size: var(--text-xs); white-space: nowrap; }
    .lesson-row small.done { color: var(--color-success); }
    .quick-grid { display: grid; gap: var(--sp-2); grid-template-columns: repeat(2, 1fr); }
    .quick-grid a { align-items: center; border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); color: var(--text-primary); display: flex; gap: var(--sp-2); padding: var(--sp-3); text-decoration: none; }
    .quick-grid a:hover { background: var(--bg-raised); }
    .quick-grid i { color: var(--color-accent); font-size: var(--text-lg); font-style: normal; }
    .empty { color: var(--text-tertiary); padding: var(--sp-4) 0; }
    .error { color: var(--color-danger); }
    @media (max-width: 900px) { .metrics { grid-template-columns: repeat(2, 1fr); } .dashboard-grid { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePageComponent {
  private readonly auth = inject(AuthService);
  protected readonly quickActions = QUICK_ACTIONS;
  protected readonly state = toSignal(
    inject(DashboardService).summary().pipe(
      map((summary): Loaded => ({ summary, failed: false })),
      catchError(() => of<Loaded>({ summary: null, failed: true })),
    ),
  );
  private readonly summary = computed(() => this.state()?.summary ?? null);

  protected readonly greeting = computed(() => {
    const hour = new Date().getHours();
    const salutation = hour < 13 ? 'Buongiorno' : hour < 18 ? 'Buon pomeriggio' : 'Buonasera';
    const firstName = this.auth.user()?.display_name.trim().split(/\s+/)[0];
    return firstName ? `${salutation}, ${firstName}` : salutation;
  });

  protected readonly metrics = computed(() => {
    const people = this.summary()?.people;
    const school = this.summary()?.school;
    const lessonsToday = this.summary()?.today_lessons.length ?? 0;
    const value = (n: number | undefined) => (n === undefined ? '—' : String(n));
    return [
      { label: 'Persone attive', value: value(people?.active), detail: `${people?.members ?? 0} soci`, icon: 'PE', path: '/people', query: null },
      { label: 'Musicanti', value: value(people?.musicians), detail: `${people?.sections ?? 0} sezioni`, icon: 'MU', path: '/people', query: { role: 'musician' } },
      { label: 'Allievi', value: value(people?.students), detail: `${school?.enrolled_students ?? 0} iscritti · ${school?.active_courses ?? 0} corsi attivi`, icon: 'AL', path: '/people', query: { role: 'student' } },
      { label: 'Insegnanti', value: value(people?.teachers), detail: lessonsToday === 1 ? '1 lezione oggi' : `${lessonsToday} lezioni oggi`, icon: 'IN', path: '/people', query: { role: 'teacher' } },
    ];
  });

  protected readonly activities = computed(() =>
    (this.summary()?.upcoming_activities ?? []).map((activity) => {
      const date = new Date(activity.starts_at);
      return {
        ...activity,
        day: new Intl.DateTimeFormat('it-IT', { day: '2-digit' }).format(date),
        month: new Intl.DateTimeFormat('it-IT', { month: 'short' }).format(date).toUpperCase(),
        time: new Intl.DateTimeFormat('it-IT', { weekday: 'short', hour: '2-digit', minute: '2-digit' }).format(date),
        typeLabel: TYPE_LABELS[activity.type],
      };
    }),
  );

  protected readonly lessons = computed(() =>
    (this.summary()?.today_lessons ?? []).map((lesson) => ({
      ...lesson,
      time: new Intl.DateTimeFormat('it-IT', { hour: '2-digit', minute: '2-digit' }).format(new Date(lesson.starts_at)),
      complete: lesson.students > 0 && lesson.recorded >= lesson.students,
    })),
  );
}
