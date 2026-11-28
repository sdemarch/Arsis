import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { apiErrorMessage } from '../../core/api/api-error';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { MilestoneBoardEntry, MilestoneProgress, MilestonesService, formatMetric, formatTimestamp } from './milestones.service';

/** Who reached each milestone (RB-19), with per-person reset that keeps the excess. */
@Component({
  selector: 'arsis-goals-board',
  imports: [PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Obiettivi" title="Traguardi" description="Le persone che hanno raggiunto un obiettivo su presenze o rimborsi. Azzera l'obiettivo quando hai consegnato il premio: l'eccedenza resta acquisita.">
      <a class="button button--secondary" routerLink="/goals/config">Configura obiettivi</a>
    </arsis-page-header>

    @if (error()) { <p class="error" role="alert">{{ error() }}</p> }

    @if (loaded() && !entries().length) {
      <section class="card empty-state">
        <p>Nessun obiettivo configurato.</p>
        <a class="button button--primary" routerLink="/goals/config">Crea il primo obiettivo</a>
      </section>
    } @else if (loaded()) {
      <p class="summary">
        @if (reachedPeople()) { <strong>{{ reachedPeople() }}</strong> {{ reachedPeople() === 1 ? 'persona ha' : 'persone hanno' }} raggiunto almeno un obiettivo. }
        @else { Nessuno ha ancora raggiunto un obiettivo. }
      </p>
    }

    <div class="grid">
      @for (entry of entries(); track entry.milestone.id) {
        <section class="card goal" [class.goal--reached]="entry.reached.length">
          <header>
            <div>
              <h2>{{ entry.milestone.name }}</h2>
              <p class="target">Soglia: {{ format(entry, entry.milestone.threshold) }}</p>
            </div>
            @if (entry.reached.length > 1) {
              <button type="button" class="button button--secondary" [disabled]="busy()" (click)="resetAll(entry)">Azzera tutti</button>
            }
          </header>

          @if (entry.reached.length) {
            <ul class="people">
              @for (row of entry.reached; track row.person_id) {
                <li class="reached">
                  <span class="who">
                    <span class="badge" aria-hidden="true">★</span>
                    <a [routerLink]="['/people', row.person_id]">{{ row.person_name }}</a>
                    @if (row.times_reached > 1) { <span class="times" title="Soglia raggiunta più volte">×{{ row.times_reached }}</span> }
                    @if (row.reached_at) { <small class="since">dal {{ date(row.reached_at) }}</small> }
                  </span>
                  <span class="figure">{{ format(entry, row.progress) }}</span>
                  <span class="row-actions">
                    @if (row.last_reset_id) { <button type="button" class="link" [disabled]="busy()" (click)="undo(entry, row)" [title]="'Ultimo azzeramento: ' + date(row.last_reset_at)">Annulla azzeramento</button> }
                    <button type="button" class="button button--primary" [disabled]="busy()" (click)="reset(entry, [row])">Azzera</button>
                  </span>
                </li>
              }
            </ul>
          } @else {
            <p class="none">Nessuno ha ancora raggiunto questo obiettivo.</p>
          }

          @if (entry.in_progress.length) {
            <details>
              <summary>In corso ({{ entry.in_progress.length }})</summary>
              <ul class="people">
                @for (row of entry.in_progress; track row.person_id) {
                  <li>
                    <span class="who"><a [routerLink]="['/people', row.person_id]">{{ row.person_name }}</a></span>
                    <span class="progress" [attr.aria-label]="format(entry, row.progress) + ' su ' + format(entry, entry.milestone.threshold)">
                      <span class="bar"><span [style.width.%]="percent(entry, row)"></span></span>
                      <small>mancano {{ format(entry, row.remaining) }}</small>
                    </span>
                    <span class="row-actions">
                      @if (row.last_reset_id) { <button type="button" class="link" [disabled]="busy()" (click)="undo(entry, row)" [title]="'Ultimo azzeramento: ' + date(row.last_reset_at)">Annulla azzeramento</button> }
                    </span>
                  </li>
                }
              </ul>
            </details>
          }
        </section>
      }
    </div>
  `,
  styles: `
    .summary { color: var(--text-secondary); margin: 0 0 var(--sp-5); }
    .error { color: var(--color-danger); }
    .empty-state { align-items: center; display: flex; flex-direction: column; gap: var(--sp-4); padding: var(--sp-8); text-align: center; }
    .grid { display: grid; gap: var(--sp-5); grid-template-columns: repeat(auto-fill, minmax(min(100%, 420px), 1fr)); }
    .goal { border-top: 3px solid var(--border-subtle); padding: var(--sp-5); }
    .goal--reached { border-top-color: var(--color-success); }
    header { align-items: start; display: flex; gap: var(--sp-3); justify-content: space-between; margin-bottom: var(--sp-4); }
    h2 { font-size: var(--text-lg); margin: 0; }
    .target, .none, small, summary { color: var(--text-secondary); }
    .target { font-size: var(--text-sm); margin: var(--sp-1) 0 0; }
    .none { margin: 0; }
    ul.people { list-style: none; margin: 0; padding: 0; }
    li { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-3); grid-template-columns: minmax(0, 1fr) auto auto; padding: var(--sp-2) var(--sp-2); }
    li:first-child { border-top: 0; }
    li.reached { background: var(--color-success-soft); border-radius: var(--radius-sm, 6px); border-top-color: transparent; margin-bottom: var(--sp-1); }
    .who { align-items: center; display: flex; gap: var(--sp-2); min-width: 0; }
    .badge { color: var(--color-success); }
    .since { color: var(--text-secondary); font-size: var(--text-xs); white-space: nowrap; }
    .times { background: var(--color-success); border-radius: 999px; color: var(--text-inverse); font-size: var(--text-xs); font-weight: var(--weight-semi); padding: 0 var(--sp-2); }
    .figure { font-variant-numeric: tabular-nums; font-weight: var(--weight-semi); }
    .row-actions { align-items: center; display: flex; gap: var(--sp-2); justify-content: flex-end; }
    .link { background: none; border: 0; color: var(--text-secondary); cursor: pointer; font-size: var(--text-sm); padding: 0; text-decoration: underline; }
    .progress { align-items: center; display: flex; gap: var(--sp-2); }
    .bar { background: var(--border-subtle); border-radius: 999px; display: block; height: 6px; overflow: hidden; width: 90px; }
    .bar span { background: var(--color-accent); display: block; height: 100%; }
    details { margin-top: var(--sp-4); }
    summary { cursor: pointer; margin-bottom: var(--sp-2); }
    @media (max-width: 600px) { li { grid-template-columns: 1fr auto; } .row-actions { grid-column: 1 / -1; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GoalsBoardComponent {
  private readonly api = inject(MilestonesService);
  protected readonly entries = signal<MilestoneBoardEntry[]>([]);
  protected readonly loaded = signal(false);
  protected readonly busy = signal(false);
  protected readonly error = signal('');
  protected readonly reachedPeople = computed(
    () => new Set(this.entries().flatMap((entry) => entry.reached.map((row) => row.person_id))).size,
  );

  constructor() {
    this.api.board().subscribe({
      next: (entries) => { this.entries.set(entries); this.loaded.set(true); },
      error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Impossibile caricare gli obiettivi.')),
    });
  }

  protected format(entry: MilestoneBoardEntry, value: string): string {
    return formatMetric(entry.milestone.metric, value);
  }

  protected percent(entry: MilestoneBoardEntry, row: MilestoneProgress): number {
    return Math.min(100, (Number(row.progress) / Number(entry.milestone.threshold)) * 100);
  }

  protected date(value: string | null): string {
    return formatTimestamp(value);
  }

  protected resetAll(entry: MilestoneBoardEntry): void {
    this.reset(entry, entry.reached);
  }

  protected reset(entry: MilestoneBoardEntry, rows: readonly MilestoneProgress[]): void {
    const who = rows.length === 1 ? rows[0].person_name : `${rows.length} persone`;
    const threshold = this.format(entry, entry.milestone.threshold);
    if (!window.confirm(`Azzerare “${entry.milestone.name}” per ${who}? Verrà sottratta la soglia (${threshold}); l'eccedenza resta.`)) return;
    this.run(entry, this.api.reset(entry.milestone.id, rows.map((row) => row.person_id)), 'Azzeramento non riuscito.');
  }

  protected undo(entry: MilestoneBoardEntry, row: MilestoneProgress): void {
    if (row.last_reset_id === null) return;
    if (!window.confirm(`Annullare l'ultimo azzeramento di “${entry.milestone.name}” per ${row.person_name}?`)) return;
    this.run(entry, this.api.undoReset(entry.milestone.id, row.last_reset_id), 'Annullamento non riuscito.');
  }

  private run(entry: MilestoneBoardEntry, request: ReturnType<MilestonesService['reset']>, failure: string): void {
    this.busy.set(true);
    this.error.set('');
    request.subscribe({
      next: (updated) => {
        this.busy.set(false);
        this.entries.update((all) => all.map((item) => (item.milestone.id === entry.milestone.id ? updated : item)));
      },
      error: (err: unknown) => { this.busy.set(false); this.error.set(apiErrorMessage(err, failure)); },
    });
  }
}
