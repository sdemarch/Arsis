import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import dashboardData from '../../../assets/mock/dashboard.json';

@Component({
  selector: 'arsis-home-page',
  imports: [PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header
      eyebrow="Dashboard"
      title="Buongiorno, Stefano"
      description="Qui trovi le informazioni operative della tua associazione."
    ><a class="button button--primary" routerLink="/people">＋ Nuova persona</a></arsis-page-header>
    <section class="metrics" aria-label="Riepilogo persone attive">
      @for (metric of metrics; track metric.label) {
        <article class="metric-card">
          <div class="metric-card__top"><span>{{ metric.label }}</span><i>{{ metric.icon }}</i></div>
          <strong>{{ metric.value }}</strong><small>{{ metric.detail }}</small>
        </article>
      }
    </section>
    <section class="dashboard-grid">
      <article class="panel panel--wide">
        <header><div><p class="section-label">Agenda</p><h2>Prossime attività</h2></div><a routerLink="/activities">Vedi calendario →</a></header>
        <div class="activity-list">
          @for (activity of activities; track activity.title) {
            <div class="activity-row">
              <time><strong>{{ activity.day }}</strong><span>{{ activity.month }}</span></time>
              <div><strong>{{ activity.title }}</strong><span>{{ activity.time }} · {{ activity.location }}</span></div>
              <span class="type-pill">{{ activity.type }}</span>
            </div>
          }
        </div>
      </article>
      <article class="panel">
        <header><div><p class="section-label">Oggi</p><h2>Lezioni</h2></div><a routerLink="/school/lessons">Tutte →</a></header>
        <div class="lesson-list">
          @for (lesson of lessons; track lesson.time) {
            <div class="lesson-row"><time>{{ lesson.time }}</time><div><strong>{{ lesson.course }}</strong><span>{{ lesson.teacher }} · {{ lesson.students }}</span></div></div>
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
    .metric-card { display: grid; gap: var(--sp-1); padding: var(--sp-5); }
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
    .activity-row { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-4); grid-template-columns: 44px 1fr auto; padding: var(--sp-3) 0; }
    .activity-row time { align-items: center; background: var(--bg-raised); border-radius: var(--radius-md); display: flex; flex-direction: column; font-family: var(--font-sans); padding: var(--sp-1); }
    .activity-row time strong { font-family: var(--font-display); font-size: var(--text-lg); }
    .activity-row time span { color: var(--text-tertiary); font-size: var(--text-xs); }
    .activity-row > div, .lesson-row > div { display: grid; }
    .activity-row > div span, .lesson-row span { color: var(--text-secondary); font-size: var(--text-sm); }
    .type-pill { background: var(--color-accent-soft); border-radius: var(--radius-full); color: var(--color-accent-hover); font-size: var(--text-xs); padding: var(--sp-1) var(--sp-2); }
    .lesson-row { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-4); grid-template-columns: 48px 1fr; padding: var(--sp-4) 0; }
    .lesson-row time { color: var(--color-accent-hover); font-size: var(--text-sm); }
    .quick-grid { display: grid; gap: var(--sp-2); grid-template-columns: repeat(2, 1fr); }
    .quick-grid a { align-items: center; border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); color: var(--text-primary); display: flex; gap: var(--sp-2); padding: var(--sp-3); text-decoration: none; }
    .quick-grid a:hover { background: var(--bg-raised); }
    .quick-grid i { color: var(--color-accent); font-size: var(--text-lg); font-style: normal; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePageComponent {
  protected readonly metrics = dashboardData.metrics;
  protected readonly activities = dashboardData.activities;
  protected readonly lessons = dashboardData.lessons;
  protected readonly quickActions = dashboardData.quickActions;
}
