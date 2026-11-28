import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { apiErrorMessage } from '../../core/api/api-error';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import {
  ACHIEVEMENT_STATUS_LABELS,
  AchievementStatus,
  Milestone,
  MilestoneAchievement,
  MilestonesService,
  formatMetric,
  formatTimestamp,
} from './milestones.service';

/** Log of every milestone reached (RB-20): open, consumed by a reset, or revoked. */
@Component({
  selector: 'arsis-goals-history',
  imports: [FormsModule, PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Obiettivi" title="Storico traguardi" description="Ogni volta che una persona raggiunge un obiettivo resta registrato qui, con la data. L'azzeramento chiude il traguardo; se il progresso scende sotto la soglia il traguardo viene revocato." />

    <section class="card filters">
      <label>Obiettivo
        <select name="milestone" [(ngModel)]="milestoneId" (ngModelChange)="load()">
          <option [ngValue]="null">Tutti</option>
          @for (item of milestones(); track item.id) { <option [ngValue]="item.id">{{ item.name }}{{ item.archived_at ? ' (archiviato)' : '' }}</option> }
        </select>
      </label>
      <label>Stato
        <select name="status" [(ngModel)]="status" (ngModelChange)="load()">
          <option [ngValue]="null">Tutti</option>
          @for (option of statuses; track option) { <option [ngValue]="option">{{ labels[option] }}</option> }
        </select>
      </label>
    </section>

    @if (error()) { <p class="error" role="alert">{{ error() }}</p> }

    <div class="table-shell card">
      <table>
        <thead><tr><th>Raggiunto il</th><th>Persona</th><th>Obiettivo</th><th>Progresso</th><th>Stato</th><th>Chiuso il</th></tr></thead>
        <tbody>
          @for (row of rows(); track row.id) {
            <tr>
              <td>{{ when(row.reached_at) }}</td>
              <td><a [routerLink]="['/people', row.person_id]">{{ row.person_name }}</a></td>
              <td>{{ row.milestone_name }} <small>· soglia {{ format(row, row.threshold) }}</small></td>
              <td class="num">{{ format(row, row.progress) }}</td>
              <td><span [class]="'status status--' + row.status">{{ labels[row.status] }}</span></td>
              <td>{{ when(row.closed_at) || '—' }}</td>
            </tr>
          } @empty {
            <tr><td colspan="6" class="empty">{{ loaded() ? 'Nessun traguardo registrato con questi filtri.' : 'Caricamento…' }}</td></tr>
          }
        </tbody>
      </table>
    </div>
    @if (rows().length === limit) { <p class="hint">Mostrati gli ultimi {{ limit }} traguardi: usa i filtri per restringere.</p> }
  `,
  styles: `
    .filters { display: flex; flex-wrap: wrap; gap: var(--sp-4); margin-bottom: var(--sp-5); padding: var(--sp-4) var(--sp-5); }
    label { display: grid; gap: var(--sp-2); min-width: 220px; }
    select { min-height: 38px; padding: var(--sp-2); }
    .table-shell { overflow-x: auto; padding: var(--sp-2); }
    table { border-collapse: collapse; width: 100%; }
    th, td { border-bottom: var(--border-thin) solid var(--border-subtle); padding: var(--sp-3); text-align: left; }
    th { color: var(--text-secondary); font-size: var(--text-sm); }
    td.num { font-variant-numeric: tabular-nums; text-align: right; }
    small, .hint { color: var(--text-secondary); }
    .hint { font-size: var(--text-sm); }
    .empty { color: var(--text-secondary); text-align: center; }
    .error { color: var(--color-danger); }
    .status { border-radius: 999px; font-size: var(--text-xs); font-weight: var(--weight-semi); padding: var(--sp-1) var(--sp-2); white-space: nowrap; }
    .status--open { background: var(--color-success-soft); color: var(--color-success); }
    .status--reset { background: var(--color-accent-soft); color: var(--color-accent-hover); }
    .status--revoked { background: var(--color-warn-soft); color: var(--color-warn); }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GoalsHistoryComponent {
  private readonly api = inject(MilestonesService);
  protected readonly limit = 500;
  protected readonly labels = ACHIEVEMENT_STATUS_LABELS;
  protected readonly statuses: readonly AchievementStatus[] = ['open', 'reset', 'revoked'];
  protected readonly milestones = signal<Milestone[]>([]);
  protected readonly rows = signal<MilestoneAchievement[]>([]);
  protected readonly loaded = signal(false);
  protected readonly error = signal('');
  protected milestoneId: number | null = null;
  protected status: AchievementStatus | null = null;

  constructor() {
    this.api.list(true).subscribe({ next: (items) => this.milestones.set(items) });
    this.load();
  }

  protected load(): void {
    this.error.set('');
    this.api
      .achievements({ milestone_id: this.milestoneId ?? undefined, status: this.status ?? undefined, limit: this.limit })
      .subscribe({
        next: (rows) => { this.rows.set(rows); this.loaded.set(true); },
        error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Impossibile caricare lo storico.')),
      });
  }

  protected format(row: MilestoneAchievement, value: string): string {
    return formatMetric(row.metric, value);
  }

  protected when(value: string | null): string {
    return formatTimestamp(value, true);
  }
}
