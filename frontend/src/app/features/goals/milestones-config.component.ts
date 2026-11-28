import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { apiErrorMessage } from '../../core/api/api-error';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { METRIC_OPTIONS, Milestone, MilestoneMetric, MilestonesService, formatMetric, metricLabel } from './milestones.service';

interface MilestoneDraft {
  name: string;
  metric: MilestoneMetric;
  threshold: string;
  notes: string;
}

const emptyDraft = (): MilestoneDraft => ({ name: '', metric: 'rehearsal_count', threshold: '10', notes: '' });

/** Configurable milestones: what is counted and the threshold to reach. */
@Component({
  selector: 'arsis-milestones-config',
  imports: [BackLinkComponent, FormsModule, PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Obiettivi" title="Configura obiettivi" description="Ogni obiettivo conta presenze o rimborsi già registrati, compreso lo storico.">
      <arsis-back-link class="back-link--compact" link="/goals" label="Traguardi" />
    </arsis-page-header>

    <section class="card">
      <h2>{{ editing() ? 'Modifica “' + editing()!.name + '”' : 'Nuovo obiettivo' }}</h2>
      <form (ngSubmit)="save()">
        <label class="wide">Nome<input name="name" [(ngModel)]="draft.name" maxlength="200" required placeholder="Es. 10 prove" /></label>
        <label>Cosa si conta
          <select name="metric" [(ngModel)]="draft.metric">
            @for (option of metrics; track option.value) { <option [value]="option.value">{{ option.label }}</option> }
          </select>
        </label>
        <label>Soglia{{ isMoney() ? ' (€)' : '' }}<input name="threshold" type="number" [min]="isMoney() ? 0.01 : 1" [step]="isMoney() ? 0.01 : 1" [(ngModel)]="draft.threshold" required /></label>
        <label class="full">Note<textarea name="notes" rows="2" [(ngModel)]="draft.notes"></textarea></label>
        <div class="actions">
          @if (editing()) { <button type="button" class="button button--secondary" (click)="reset()">Annulla</button> }
          <button class="button button--primary" [disabled]="busy()">{{ editing() ? 'Salva' : 'Aggiungi' }}</button>
        </div>
      </form>
      <p class="hint">Cambiare la soglia non modifica gli azzeramenti già fatti: ognuno ha sottratto la soglia in vigore in quel momento.</p>
      @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
    </section>

    <section class="card list">
      <ul>
        @for (item of active(); track item.id) {
          <li>
            <span class="name"><strong>{{ item.name }}</strong><small>{{ label(item) }}</small></span>
            <span class="figures">{{ format(item) }}</span>
            <span class="row-actions">
              <button type="button" class="button button--secondary" (click)="edit(item)">Modifica</button>
              <button type="button" class="button button--secondary" (click)="archive(item)">Archivia</button>
            </span>
          </li>
        } @empty {
          <li class="empty">Nessun obiettivo. Aggiungine uno, ad esempio «10 prove» o «150 € di rimborsi».</li>
        }
      </ul>
      @if (archived().length) {
        <details>
          <summary>Obiettivi archiviati ({{ archived().length }})</summary>
          <ul>@for (item of archived(); track item.id) { <li><span class="name">{{ item.name }}<small>{{ label(item) }}</small></span><span class="figures">{{ format(item) }}</span></li> }</ul>
        </details>
      }
    </section>
  `,
  styles: `
    .card { padding: var(--sp-6); }
    .card + .card { margin-top: var(--sp-5); }
    h2 { margin-top: 0; }
    form { align-items: end; display: grid; gap: var(--sp-4); grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 0.6fr); }
    label { display: grid; gap: var(--sp-2); }
    label.full, .actions { grid-column: 1 / -1; }
    input, select, textarea { min-height: 38px; min-width: 0; padding: var(--sp-2); }
    .actions { display: flex; gap: var(--sp-2); justify-content: flex-end; }
    .hint { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-4) 0 0; }
    .error { color: var(--color-danger); }
    ul { list-style: none; margin: 0; padding: 0; }
    li { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-3); grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) auto; padding: var(--sp-3) 0; }
    li:first-child { border-top: 0; }
    .name { display: grid; gap: var(--sp-1); }
    small, .figures, .empty { color: var(--text-secondary); }
    .figures { font-variant-numeric: tabular-nums; }
    .row-actions { display: flex; gap: var(--sp-2); }
    details { margin-top: var(--sp-5); }
    summary { color: var(--text-secondary); cursor: pointer; }
    @media (max-width: 800px) { form, li { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MilestonesConfigComponent {
  private readonly api = inject(MilestonesService);
  private readonly milestones = signal<Milestone[]>([]);

  protected readonly metrics = METRIC_OPTIONS;
  protected readonly active = computed(() => this.milestones().filter((m) => !m.archived_at));
  protected readonly archived = computed(() => this.milestones().filter((m) => m.archived_at));
  protected readonly editing = signal<Milestone | null>(null);
  protected readonly busy = signal(false);
  protected readonly error = signal('');
  protected draft = emptyDraft();

  constructor() {
    this.load();
  }

  protected isMoney(): boolean {
    return this.draft.metric === 'reimbursement_total';
  }

  protected label(item: Milestone): string {
    return metricLabel(item.metric);
  }

  protected format(item: Milestone): string {
    return formatMetric(item.metric, item.threshold);
  }

  protected edit(item: Milestone): void {
    this.editing.set(item);
    this.error.set('');
    this.draft = { name: item.name, metric: item.metric, threshold: String(Number(item.threshold)), notes: item.notes ?? '' };
  }

  protected reset(): void {
    this.editing.set(null);
    this.error.set('');
    this.draft = emptyDraft();
  }

  protected save(): void {
    const name = this.draft.name.trim();
    const threshold = Number(this.draft.threshold);
    if (!name) return;
    if (!(threshold > 0) || (!this.isMoney() && !Number.isInteger(threshold))) {
      this.error.set(this.isMoney() ? 'La soglia deve essere un importo positivo.' : 'La soglia deve essere un numero intero positivo.');
      return;
    }
    const payload = { name, metric: this.draft.metric, threshold: threshold.toFixed(2), notes: this.draft.notes.trim() || null };
    const current = this.editing();
    const request = current ? this.api.update(current.id, { ...payload, version: current.version }) : this.api.create(payload);
    this.busy.set(true);
    request.subscribe({
      next: () => { this.busy.set(false); this.reset(); this.load(); },
      error: (err: unknown) => { this.busy.set(false); this.error.set(apiErrorMessage(err, 'Salvataggio non riuscito.')); },
    });
  }

  protected archive(item: Milestone): void {
    if (!window.confirm(`Archiviare l'obiettivo “${item.name}”? Non comparirà più tra i traguardi.`)) return;
    this.api.archive(item.id, item.version).subscribe({
      next: () => { if (this.editing()?.id === item.id) this.reset(); this.load(); },
      error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Archiviazione non riuscita.')),
    });
  }

  private load(): void {
    this.api.list(true).subscribe({ next: (items) => this.milestones.set(items) });
  }
}
