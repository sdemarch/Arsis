import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { apiErrorMessage } from '../../core/api/api-error';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { Place, PlacesService } from './places.service';

interface PlaceDraft {
  name: string;
  address: string;
  distance_km: number;
  highway_cost: string;
  notes: string;
}

const emptyDraft = (): PlaceDraft => ({ name: '', address: '', distance_km: 0, highway_cost: '0.00', notes: '' });

/** Places linked to activities, with the round-trip km and toll used for driver refunds. */
@Component({
  selector: 'arsis-places-page',
  imports: [BackLinkComponent, FormsModule, PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Configurazioni" title="Luoghi" description="I luoghi delle attività, con chilometri e pedaggio di andata e ritorno usati per il rimborso agli autisti.">
      <arsis-back-link class="back-link--compact" link="/settings" label="Configurazioni" />
    </arsis-page-header>

    <section class="card">
      <h2>{{ editing() ? 'Modifica “' + editing()!.name + '”' : 'Nuovo luogo' }}</h2>
      <form (ngSubmit)="save()">
        <label class="wide">Nome<input name="name" [(ngModel)]="draft.name" maxlength="200" required /></label>
        <label class="wide">Indirizzo<input name="address" [(ngModel)]="draft.address" maxlength="500" /></label>
        <label>Km andata e ritorno<input name="km" type="number" min="0" step="1" [(ngModel)]="draft.distance_km" required /></label>
        <label>Pedaggio autostradale A/R (€)<input name="toll" type="number" min="0" step="0.01" [(ngModel)]="draft.highway_cost" required /></label>
        <label class="full">Note<textarea name="notes" rows="2" [(ngModel)]="draft.notes"></textarea></label>
        <div class="actions">
          @if (editing()) { <button type="button" class="button button--secondary" (click)="reset()">Annulla</button> }
          <button class="button button--primary" [disabled]="busy()">{{ editing() ? 'Salva' : 'Aggiungi' }}</button>
        </div>
      </form>
      <p class="hint">Le modifiche a chilometri e pedaggio valgono per le presenze registrate da questo momento: i rimborsi già registrati non cambiano.</p>
      @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
    </section>

    <section class="card list">
      <ul>
        @for (item of active(); track item.id) {
          <li>
            <span class="name"><strong>{{ item.name }}</strong>@if (item.address) { <small>{{ item.address }}</small> }</span>
            <span class="figures"><span>{{ item.distance_km }} km A/R</span><span>{{ currency(item.highway_cost) }} pedaggio</span></span>
            <span class="row-actions">
              <button type="button" class="button button--secondary" (click)="edit(item)">Modifica</button>
              <button type="button" class="button button--secondary" (click)="archive(item)">Archivia</button>
            </span>
          </li>
        } @empty {
          <li class="empty">Nessun luogo. Aggiungi i luoghi dove si svolgono concerti e processioni.</li>
        }
      </ul>
      @if (archived().length) {
        <details>
          <summary>Luoghi archiviati ({{ archived().length }})</summary>
          <ul>@for (item of archived(); track item.id) { <li><span class="name">{{ item.name }}</span><span class="figures"><span>{{ item.distance_km }} km A/R</span><span>{{ currency(item.highway_cost) }} pedaggio</span></span></li> }</ul>
        </details>
      }
    </section>
  `,
  styles: `
    .card { padding: var(--sp-6); }
    .card + .card { margin-top: var(--sp-5); }
    h2 { margin-top: 0; }
    form { align-items: end; display: grid; gap: var(--sp-4); grid-template-columns: repeat(2, minmax(0, 1fr)) repeat(2, minmax(0, 0.8fr)); }
    label { display: grid; gap: var(--sp-2); }
    label.full, .actions { grid-column: 1 / -1; }
    input, textarea { min-height: 38px; min-width: 0; padding: var(--sp-2); }
    .actions { display: flex; gap: var(--sp-2); justify-content: flex-end; }
    .hint { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-4) 0 0; }
    .error { color: var(--color-danger); }
    ul { list-style: none; margin: 0; padding: 0; }
    li { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-3); grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) auto; padding: var(--sp-3) 0; }
    li:first-child { border-top: 0; }
    .name { display: grid; gap: var(--sp-1); }
    small, .figures, .empty { color: var(--text-secondary); }
    .figures { display: flex; flex-wrap: wrap; gap: var(--sp-3); font-variant-numeric: tabular-nums; }
    .row-actions { display: flex; gap: var(--sp-2); }
    details { margin-top: var(--sp-5); }
    summary { color: var(--text-secondary); cursor: pointer; }
    @media (max-width: 800px) { form, li { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlacesPageComponent {
  private readonly api = inject(PlacesService);
  private readonly places = signal<Place[]>([]);

  protected readonly active = computed(() => this.places().filter((p) => !p.archived_at));
  protected readonly archived = computed(() => this.places().filter((p) => p.archived_at));
  protected readonly editing = signal<Place | null>(null);
  protected readonly busy = signal(false);
  protected readonly error = signal('');
  protected draft = emptyDraft();

  constructor() {
    this.load();
  }

  protected currency(value: string): string {
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(Number(value));
  }

  protected edit(item: Place): void {
    this.editing.set(item);
    this.error.set('');
    this.draft = { name: item.name, address: item.address ?? '', distance_km: item.distance_km, highway_cost: item.highway_cost, notes: item.notes ?? '' };
  }

  protected reset(): void {
    this.editing.set(null);
    this.error.set('');
    this.draft = emptyDraft();
  }

  protected save(): void {
    const name = this.draft.name.trim();
    const km = Number(this.draft.distance_km);
    if (!name) return;
    if (!Number.isInteger(km) || km < 0) {
      this.error.set('I chilometri devono essere un numero intero non negativo.');
      return;
    }
    const payload = {
      name,
      address: this.draft.address.trim() || null,
      distance_km: km,
      highway_cost: Number(this.draft.highway_cost || 0).toFixed(2),
      notes: this.draft.notes.trim() || null,
    };
    const current = this.editing();
    const request = current ? this.api.update(current.id, { ...payload, version: current.version }) : this.api.create(payload);
    this.busy.set(true);
    request.subscribe({
      next: () => { this.busy.set(false); this.reset(); this.load(); },
      error: (err: unknown) => { this.busy.set(false); this.error.set(apiErrorMessage(err, 'Salvataggio non riuscito.')); },
    });
  }

  protected archive(item: Place): void {
    if (!window.confirm(`Archiviare il luogo “${item.name}”? Le attività già collegate lo mantengono.`)) return;
    this.api.archive(item.id, item.version).subscribe({
      next: () => { if (this.editing()?.id === item.id) this.reset(); this.load(); },
      error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Archiviazione non riuscita.')),
    });
  }

  private load(): void {
    this.api.list(true).subscribe({ next: (items) => this.places.set(items) });
  }
}
