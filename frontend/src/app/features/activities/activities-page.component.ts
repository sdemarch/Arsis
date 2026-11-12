import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { catchError, debounceTime, distinctUntilChanged, map, of, switchMap } from 'rxjs';
import { localDateKey } from '../../core/time/local-datetime';
import { FilterDropdownComponent, FilterOption } from '../../shared/ui/filter-dropdown.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { ActivitiesService, Activity } from './activities.service';

const TYPE_LABELS: Record<Activity['type'], string> = { rehearsal: 'Prova', concert: 'Concerto', event: 'Evento' };
const STATUS_LABELS: Record<Activity['status'], string> = { planned: 'Pianificata', confirmed: 'Confermata', cancelled: 'Annullata', completed: 'Conclusa' };
const STATUS_TONES: Record<Activity['status'], string> = { planned: 'warn', confirmed: 'success', cancelled: 'danger', completed: 'success' };

interface CalendarDay {
  readonly key: string;
  readonly day: number;
  readonly inMonth: boolean;
  readonly today: boolean;
  readonly activities: readonly Activity[];
}

function decorate(activity: Activity) {
  const date = new Date(activity.starts_at);
  return {
    ...activity,
    dayKey: localDateKey(date),
    date: new Intl.DateTimeFormat('it-IT', { day: '2-digit', month: 'short' }).format(date).toUpperCase(),
    year: date.getFullYear(),
    weekday: new Intl.DateTimeFormat('it-IT', { weekday: 'long' }).format(date),
    time: new Intl.DateTimeFormat('it-IT', { hour: '2-digit', minute: '2-digit' }).format(date),
    tone: STATUS_TONES[activity.status],
    statusLabel: STATUS_LABELS[activity.status],
    typeLabel: TYPE_LABELS[activity.type],
  };
}

/** Monday-first weeks covering the month of `month` (`YYYY-MM`). */
function monthGrid(month: string): { from: string; to: string; days: { key: string; day: number; inMonth: boolean }[] } {
  const [year, monthIndex] = month.split('-').map(Number);
  const first = new Date(year, monthIndex - 1, 1);
  const start = new Date(first);
  start.setDate(1 - ((first.getDay() + 6) % 7));
  const last = new Date(year, monthIndex, 0);
  const end = new Date(last);
  end.setDate(last.getDate() + (6 - ((last.getDay() + 6) % 7)));
  const days: { key: string; day: number; inMonth: boolean }[] = [];
  for (const cursor = new Date(start); cursor <= end; cursor.setDate(cursor.getDate() + 1)) {
    days.push({ key: localDateKey(cursor), day: cursor.getDate(), inMonth: cursor.getMonth() === monthIndex - 1 });
  }
  return { from: localDateKey(start), to: localDateKey(end), days };
}

function shiftMonth(month: string, delta: number): string {
  const [year, monthIndex] = month.split('-').map(Number);
  return localDateKey(new Date(year, monthIndex - 1 + delta, 1)).slice(0, 7);
}

@Component({
  selector: 'arsis-activities-page',
  imports: [FilterDropdownComponent, FormsModule, PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Attività" [title]="attendanceMode ? 'Presenze alle attività' : 'Calendario e attività'" [description]="attendanceMode ? 'Scegli un’attività per gestire convocati e presenze.' : 'Organizza prove, concerti, eventi e presenze.'">
      <a class="button button--primary" routerLink="/activities/new">＋ Nuova attività</a>
    </arsis-page-header>

    <nav class="view-tabs" aria-label="Vista">
      <a routerLink="/activities" queryParamsHandling="preserve" [class.is-active]="!calendarView">Elenco</a>
      <a routerLink="/activities/calendar" queryParamsHandling="preserve" [class.is-active]="calendarView">Calendario</a>
      <a routerLink="/activities/refunds">Rimborsi</a>
    </nav>

    @if (calendarView) {
      <section class="month card">
        <header>
          <h2>{{ monthLabel() }}</h2>
          <div class="month-nav">
            <button type="button" class="button button--secondary" (click)="goToMonth(-1)" aria-label="Mese precedente">‹</button>
            <button type="button" class="button button--secondary" (click)="goToToday()">Oggi</button>
            <button type="button" class="button button--secondary" (click)="goToMonth(1)" aria-label="Mese successivo">›</button>
          </div>
        </header>
        <div class="month-grid weekdays">@for (day of weekdays; track $index) { <span>{{ day }}</span> }</div>
        <div class="month-grid">
          @for (day of calendarDays(); track day.key) {
            <div class="cell" [class.outside]="!day.inMonth" [class.today]="day.today">
              <span class="cell-day">{{ day.day }}</span>
              @for (activity of day.activities; track activity.id) {
                <a class="chip chip--{{ activity.type }}" [class.cancelled]="activity.status === 'cancelled'" [routerLink]="['/activities', activity.id]" [title]="activity.title">
                  {{ time(activity.starts_at) }} {{ activity.title }}
                </a>
              }
            </div>
          }
        </div>
        <footer class="legend"><span><i class="dot--rehearsal"></i> Prova</span><span><i class="dot--concert"></i> Concerto</span><span><i class="dot--event"></i> Evento</span></footer>
      </section>
    } @else {
      <div class="toolbar">
        <div class="toolbar__group"><input class="search-input" type="search" placeholder="Cerca attività…" aria-label="Cerca attività" [ngModel]="search()" (ngModelChange)="setSearch($event)" /><arsis-filter-dropdown label="Tutte le tipologie" [options]="typeOptions" [selected]="selectedTypes()" [multiple]="true" (selectionChange)="setTypes($event)" /><arsis-filter-dropdown label="Tutti gli anni" [options]="yearOptions()" [selected]="selectedYears()" (selectionChange)="setYears($event)" /></div>
        <div class="toolbar__result">
          @if (selectedDay(); as day) { <button type="button" class="day-chip" (click)="selectDay(null)">{{ dayLabel(day) }} ×</button> }
          <span class="result-count">{{ filteredActivities().length }} attività</span>
          <button class="button button--secondary" type="button" [disabled]="!hasFilters()" (click)="clearFilters()">Azzera filtri</button>
        </div>
      </div>

      <section class="activity-layout">
        <div class="activity-feed">
          @for (activity of filteredActivities(); track activity.id) {
            <a class="activity-card card" [routerLink]="attendanceMode ? ['/activities', activity.id, 'attendance'] : ['/activities', activity.id]" aria-label="Apri {{ activity.title }}">
              <div class="date-block"><strong>{{ activity.date.split(' ')[0] }}</strong><span>{{ activity.date.split(' ')[1] }}</span><small>{{ activity.weekday }}</small></div>
              <div class="activity-main"><div class="activity-title"><span>{{ activity.typeLabel }}</span><h2>{{ activity.title }}</h2></div><p>{{ activity.time }}@if (activity.location) { · {{ activity.location }} }</p><div class="participants"><span class="avatar av-green">{{ activity.participant_count }}</span><small>convocati@if (activity.present_count || activity.absent_count) { · {{ activity.present_count }} presenti · {{ activity.absent_count }} assenti } · rimborsi {{ currency(activity.reimbursement_total) }}</small></div></div>
              <div class="activity-state"><span class="status-badge status-badge--{{ activity.tone }}">{{ activity.statusLabel }}</span></div>
            </a>
          }
          @empty { <div class="empty-state card">Nessuna attività corrisponde ai filtri selezionati.</div> }
        </div>

        <aside class="mini-calendar card">
          <header><button type="button" (click)="goToMonth(-1)" aria-label="Mese precedente">‹</button><h2>{{ monthLabel() }}</h2><button type="button" (click)="goToMonth(1)" aria-label="Mese successivo">›</button></header>
          <div class="weekdays">@for (day of weekdays; track $index) { <span>{{ day }}</span> }</div>
          <div class="days">
            @for (day of calendarDays(); track day.key) {
              <button type="button" [class.outside]="!day.inMonth" [class.today]="day.today" [class.has-event]="day.activities.length" [class.selected]="selectedDay() === day.key" [disabled]="!day.activities.length" (click)="selectDay(selectedDay() === day.key ? null : day.key)" [attr.aria-label]="dayLabel(day.key) + ': ' + day.activities.length + ' attività'">
                <span>{{ day.day }}</span>
                @if (day.activities.length) { <span class="dots">@for (a of day.activities; track a.id) { <i class="dot--{{ a.type }}"></i> }</span> }
              </button>
            }
          </div>
          <footer><span><i class="dot--rehearsal"></i> Prova</span><span><i class="dot--concert"></i> Concerto</span><span><i class="dot--event"></i> Evento</span></footer>
        </aside>
      </section>
    }
  `,
  styles: `
    .view-tabs { border-bottom: var(--border-thin) solid var(--border-default); display: flex; margin-bottom: var(--sp-5); }
    .view-tabs a { border-bottom: 2px solid transparent; color: var(--text-secondary); padding: var(--sp-3) var(--sp-4); text-decoration: none; }
    .view-tabs a.is-active { border-color: var(--color-accent); color: var(--color-accent-hover); font-weight: var(--weight-semi); }
    .result-count { color: var(--text-secondary); font-size: var(--text-sm); }
    .toolbar__result { align-items: center; display: flex; gap: var(--sp-3); }
    .toolbar__result .button:disabled { cursor: not-allowed; opacity: .5; }
    .day-chip { background: var(--color-accent-soft); border: 0; border-radius: var(--radius-full); color: var(--color-accent-hover); cursor: pointer; font: inherit; font-size: var(--text-sm); padding: var(--sp-1) var(--sp-3); }
    .activity-layout { align-items: start; display: grid; gap: var(--sp-6); grid-template-columns: 1fr 320px; }
    .activity-feed { display: grid; gap: var(--sp-3); }
    .empty-state { color: var(--text-tertiary); padding: var(--sp-8); text-align: center; }
    .activity-card { align-items: center; color: inherit; display: grid; gap: var(--sp-5); grid-template-columns: 76px 1fr auto; padding: var(--sp-5); text-decoration: none; }
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

    .dot--rehearsal { background: var(--color-accent); }
    .dot--concert { background: var(--color-success); }
    .dot--event { background: var(--color-warn); }

    .mini-calendar { padding: var(--sp-5); }
    .mini-calendar header { align-items: center; display: flex; justify-content: space-between; }
    .mini-calendar h2 { font-family: var(--font-sans); font-size: var(--text-base); margin: 0; text-transform: capitalize; }
    .mini-calendar header button { background: transparent; border: 0; color: var(--text-secondary); cursor: pointer; font-size: var(--text-xl); }
    .weekdays, .days { display: grid; grid-template-columns: repeat(7, 1fr); }
    .weekdays span { color: var(--text-tertiary); font-size: var(--text-xs); padding: var(--sp-2) 0; text-align: center; }
    .days button { align-items: center; background: transparent; border: 0; border-radius: var(--radius-md); color: inherit; display: flex; flex-direction: column; font: inherit; font-size: var(--text-sm); height: 39px; justify-content: center; position: relative; }
    .days button:disabled { cursor: default; }
    .days button.outside { color: var(--text-tertiary); }
    .days button.today span:first-child { text-decoration: underline; text-underline-offset: 3px; }
    .days button.has-event { background: var(--color-accent-soft); color: var(--color-accent-hover); cursor: pointer; font-weight: var(--weight-semi); }
    .days button.selected { outline: 2px solid var(--color-accent); }
    .dots { bottom: 4px; display: flex; gap: 2px; position: absolute; }
    .dots i { border-radius: var(--radius-full); height: 4px; width: 4px; }
    .mini-calendar footer, .legend { border-top: var(--border-thin) solid var(--border-subtle); display: flex; gap: var(--sp-4); margin-top: var(--sp-3); padding-top: var(--sp-3); }
    .mini-calendar footer span, .legend span { align-items: center; color: var(--text-secondary); display: flex; font-size: var(--text-xs); gap: var(--sp-1); }
    .mini-calendar footer i, .legend i { border-radius: var(--radius-full); height: 6px; width: 6px; }

    .month { padding: var(--sp-5); }
    .month header { align-items: center; display: flex; justify-content: space-between; margin-bottom: var(--sp-4); }
    .month h2 { margin: 0; text-transform: capitalize; }
    .month-nav { display: flex; gap: var(--sp-2); }
    .month-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
    .month-grid.weekdays span { color: var(--text-tertiary); font-size: var(--text-xs); padding: var(--sp-2); }
    .cell { border-left: var(--border-thin) solid var(--border-subtle); border-top: var(--border-thin) solid var(--border-subtle); display: flex; flex-direction: column; gap: 2px; min-height: 104px; min-width: 0; padding: var(--sp-1); }
    .cell:nth-child(7n) { border-right: var(--border-thin) solid var(--border-subtle); }
    .cell:nth-last-child(-n + 7) { border-bottom: var(--border-thin) solid var(--border-subtle); }
    .cell.outside { background: var(--bg-raised); color: var(--text-tertiary); }
    .cell-day { font-size: var(--text-sm); padding: 2px var(--sp-1); }
    .cell.today .cell-day { background: var(--color-accent); border-radius: var(--radius-full); color: var(--text-inverse); align-self: start; }
    .chip { border-left: 3px solid; border-radius: var(--radius-sm); color: var(--text-primary); font-size: var(--text-xs); overflow: hidden; padding: 2px var(--sp-1); text-decoration: none; text-overflow: ellipsis; white-space: nowrap; }
    .chip--rehearsal { background: var(--color-accent-soft); border-color: var(--color-accent); }
    .chip--concert { background: var(--color-success-soft); border-color: var(--color-success); }
    .chip--event { background: var(--color-warn-soft); border-color: var(--color-warn); }
    .chip.cancelled { opacity: .55; text-decoration: line-through; }

    @media (max-width: 900px) { .activity-layout { grid-template-columns: 1fr; } .mini-calendar { order: -1; } }
    @media (max-width: 640px) { .cell { min-height: 64px; } .chip { font-size: 0; height: 6px; padding: 0; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivitiesPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly queryParams = toSignal(this.route.queryParamMap, { initialValue: this.route.snapshot.queryParamMap });
  private readonly activitiesService = inject(ActivitiesService);
  /** Opened from the "Presenze" entry: each card leads to the attendance register. */
  protected readonly attendanceMode = this.route.snapshot.routeConfig?.path === 'attendance';
  protected readonly calendarView = this.route.snapshot.routeConfig?.path === 'calendar';

  private readonly response = toSignal(toObservable(computed(() => this.queryParams().get('q')?.trim() ?? '')).pipe(debounceTime(200), distinctUntilChanged(), switchMap((query) => this.activitiesService.list(query))), { initialValue: null });
  protected readonly activities = computed(() => (this.response()?.items ?? []).map(decorate));

  protected readonly weekdays = ['L', 'M', 'M', 'G', 'V', 'S', 'D'];

  protected currency(value: string): string { return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(Number(value)); }
  protected readonly selectedDay = computed(() => this.queryParams().get('day'));
  /** Month shown by the calendars, `YYYY-MM`: from the URL, else the selected day, else today. */
  protected readonly month = computed(() => this.queryParams().get('month') ?? this.selectedDay()?.slice(0, 7) ?? localDateKey(new Date()).slice(0, 7));
  private readonly grid = computed(() => monthGrid(this.month()));
  private readonly monthActivities = toSignal(
    toObservable(this.grid).pipe(
      switchMap(({ from, to }) => this.activitiesService.listBetween(from, to).pipe(map((page) => page.items), catchError(() => of<Activity[]>([])))),
    ),
    { initialValue: [] },
  );
  protected readonly calendarDays = computed<CalendarDay[]>(() => {
    const today = localDateKey(new Date());
    const byDay = new Map<string, Activity[]>();
    for (const activity of this.monthActivities()) {
      const key = localDateKey(new Date(activity.starts_at));
      byDay.set(key, [...(byDay.get(key) ?? []), activity]);
    }
    return this.grid().days.map((day) => ({ ...day, today: day.key === today, activities: byDay.get(day.key) ?? [] }));
  });
  protected readonly monthLabel = computed(() => {
    const [year, month] = this.month().split('-').map(Number);
    return new Intl.DateTimeFormat('it-IT', { month: 'long', year: 'numeric' }).format(new Date(year, month - 1, 1));
  });

  protected readonly typeOptions: readonly FilterOption[] = [
    { label: 'Prove', value: 'rehearsal' },
    { label: 'Concerti', value: 'concert' },
    { label: 'Eventi', value: 'event' },
  ];
  protected readonly yearOptions = computed<readonly FilterOption[]>(() => [...new Set(this.activities().map((activity) => activity.year))]
    .sort((first, second) => second - first)
    .map((year) => ({ label: String(year), value: String(year) })));
  protected readonly search = computed(() => this.queryParams().get('q')?.trim() ?? '');
  protected readonly selectedTypes = computed(() => this.queryParams().getAll('type'));
  protected readonly selectedYears = computed(() => this.queryParams().getAll('year'));
  protected readonly hasFilters = computed(() => Boolean(this.search() || this.selectedTypes().length || this.selectedYears().length || this.selectedDay()));
  protected readonly filteredActivities = computed(() => {
    const query = this.search().toLocaleLowerCase('it');
    const types = this.selectedTypes();
    const years = this.selectedYears();
    const day = this.selectedDay();

    return this.activities().filter((activity) => {
      const matchesQuery = !query || [activity.title, activity.location ?? '', activity.typeLabel].some((value) => value.toLocaleLowerCase('it').includes(query));
      const matchesType = !types.length || types.includes(activity.type);
      const matchesYear = !years.length || years.includes(String(activity.year));
      const matchesDay = !day || activity.dayKey === day;
      return matchesQuery && matchesType && matchesYear && matchesDay;
    });
  });

  protected time(value: string): string {
    return new Intl.DateTimeFormat('it-IT', { hour: '2-digit', minute: '2-digit' }).format(new Date(value));
  }

  protected dayLabel(key: string): string {
    const [year, month, day] = key.split('-').map(Number);
    return new Intl.DateTimeFormat('it-IT', { day: 'numeric', month: 'long' }).format(new Date(year, month - 1, day));
  }

  protected goToMonth(delta: number): void {
    this.updateQuery({ month: shiftMonth(this.month(), delta) });
  }

  protected goToToday(): void {
    this.updateQuery({ month: null, day: null });
  }

  protected selectDay(day: string | null): void {
    this.updateQuery({ day });
  }

  protected setSearch(query: string): void {
    this.updateQuery({ q: query.trim() || null });
  }

  protected setTypes(types: readonly string[]): void {
    this.updateQuery({ type: types.length ? [...types] : null });
  }

  protected setYears(years: readonly string[]): void {
    this.updateQuery({ year: years.length ? [...years] : null });
  }

  protected clearFilters(): void {
    this.updateQuery({ q: null, type: null, year: null, day: null });
  }

  private updateQuery(queryParams: Record<string, string | string[] | null>): void {
    void this.router.navigate([], { relativeTo: this.route, queryParams, queryParamsHandling: 'merge', replaceUrl: true });
  }
}
