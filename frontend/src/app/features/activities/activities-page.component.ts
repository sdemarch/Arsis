import { ChangeDetectionStrategy, Component } from '@angular/core';

import activityData from '../../../assets/mock/activities.json';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-activities-page',
  imports: [PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Attività" title="Calendario e attività" description="Organizza prove, concerti, eventi e presenze.">
      <button class="button button--primary" type="button">＋ Nuova attività</button>
    </arsis-page-header>

    <div class="view-tabs"><button class="is-active">Elenco</button><button>Calendario</button></div>
    <div class="toolbar">
      <div class="toolbar__group"><input class="search-input" type="search" placeholder="Cerca attività…" /><button class="button button--secondary">Tutte le tipologie⌄</button><button class="button button--secondary">2026⌄</button></div>
      <span class="result-count">{{ activities.length }} attività in programma</span>
    </div>

    <section class="activity-layout">
      <div class="activity-feed">
        @for (activity of activities; track activity.id) {
          <article class="activity-card card">
            <div class="date-block"><strong>{{ activity.date.split(' ')[0] }}</strong><span>{{ activity.date.split(' ')[1] }}</span><small>{{ activity.weekday }}</small></div>
            <div class="activity-main"><div class="activity-title"><span>{{ activity.type }}</span><h2>{{ activity.title }}</h2></div><p>{{ activity.time }} · {{ activity.location }}</p><div class="participants"><span class="avatar av-green">{{ activity.participants }}</span><small>partecipanti convocati</small></div></div>
            <div class="activity-state"><span class="status-badge status-badge--{{ activity.tone }}">{{ activity.status }}</span><button class="row-menu">•••</button></div>
          </article>
        }
      </div>

      <aside class="mini-calendar card">
        <header><button>‹</button><h2>Agosto 2026</h2><button>›</button></header>
        <div class="weekdays">@for (day of weekdays; track day) { <span>{{ day }}</span> }</div>
        <div class="days">
          @for (day of calendar; track day.day) {
            <div [class.has-event]="day.events.length"><span>{{ day.day }}</span>@if (day.events.length) { <i></i> }</div>
          }
        </div>
        <footer><span><i></i> Prova</span><span><i></i> Concerto</span></footer>
      </aside>
    </section>
  `,
  styles: `
    .view-tabs { border-bottom: var(--border-thin) solid var(--border-default); display: flex; margin-bottom: var(--sp-5); }
    .view-tabs button { background: transparent; border: 0; border-bottom: 2px solid transparent; color: var(--text-secondary); cursor: pointer; padding: var(--sp-3) var(--sp-4); }
    .view-tabs button.is-active { border-color: var(--color-accent); color: var(--color-accent-hover); font-weight: var(--weight-semi); }
    .result-count { color: var(--text-secondary); font-size: var(--text-sm); }
    .activity-layout { align-items: start; display: grid; gap: var(--sp-6); grid-template-columns: 1fr 320px; }
    .activity-feed { display: grid; gap: var(--sp-3); }
    .activity-card { align-items: center; display: grid; gap: var(--sp-5); grid-template-columns: 76px 1fr auto; padding: var(--sp-5); }
    .activity-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-1px); }
    .date-block { align-items: center; border-right: var(--border-thin) solid var(--border-subtle); display: flex; flex-direction: column; }
    .date-block strong { font-family: var(--font-display); font-size: var(--text-2xl); line-height: 1; }
    .date-block span { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); }
    .date-block small { color: var(--text-tertiary); margin-top: var(--sp-1); }
    .activity-title { align-items: center; display: flex; gap: var(--sp-2); }
    .activity-title span { background: var(--color-accent-soft); border-radius: var(--radius-full); color: var(--color-accent-hover); font-size: var(--text-xs); padding: var(--sp-1) var(--sp-2); }
    .activity-title h2 { font-family: var(--font-sans); font-size: var(--text-lg); margin: 0; }
    .activity-main > p { color: var(--text-secondary); margin: var(--sp-1) 0 var(--sp-3); }
    .participants { align-items: center; display: flex; gap: var(--sp-2); }
    .participants .avatar { height: 28px; width: 28px; }
    .participants small { color: var(--text-tertiary); }
    .activity-state { align-items: end; display: flex; flex-direction: column; gap: var(--sp-4); }
    .row-menu { background: transparent; border: 0; color: var(--text-tertiary); cursor: pointer; }
    .mini-calendar { padding: var(--sp-5); }
    .mini-calendar header { align-items: center; display: flex; justify-content: space-between; }
    .mini-calendar h2 { font-family: var(--font-sans); font-size: var(--text-base); }
    .mini-calendar button { background: transparent; border: 0; color: var(--text-secondary); cursor: pointer; font-size: var(--text-xl); }
    .weekdays, .days { display: grid; grid-template-columns: repeat(7, 1fr); }
    .weekdays span { color: var(--text-tertiary); font-size: var(--text-xs); padding: var(--sp-2) 0; text-align: center; }
    .days div { align-items: center; border-radius: var(--radius-md); display: flex; flex-direction: column; font-size: var(--text-sm); height: 39px; justify-content: center; position: relative; }
    .days div.has-event { background: var(--color-accent-soft); color: var(--color-accent-hover); font-weight: var(--weight-semi); }
    .days i { background: var(--color-accent); border-radius: var(--radius-full); bottom: 4px; height: 3px; position: absolute; width: 3px; }
    .mini-calendar footer { border-top: var(--border-thin) solid var(--border-subtle); display: flex; gap: var(--sp-4); margin-top: var(--sp-3); padding-top: var(--sp-3); }
    .mini-calendar footer span { align-items: center; color: var(--text-secondary); display: flex; font-size: var(--text-xs); gap: var(--sp-1); }
    .mini-calendar footer i { background: var(--color-accent); border-radius: var(--radius-full); height: 6px; width: 6px; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivitiesPageComponent {
  protected readonly activities = activityData.activities;
  protected readonly calendar = activityData.calendar;
  protected readonly weekdays = ['L', 'M', 'M', 'G', 'V', 'S', 'D'];
}

