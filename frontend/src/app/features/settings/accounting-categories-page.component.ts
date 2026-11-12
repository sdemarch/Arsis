import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import {
  AccountingCategory,
  AccountingCategoryWrite,
  AccountingPersonRole,
  AccountingService,
  DIRECTION_LABELS,
  ROLE_LABELS,
  apiErrorMessage,
} from '../accounting/accounting.service';

interface CategoryDraft {
  name: string;
  direction: AccountingCategory['direction'];
  required_person_role: AccountingPersonRole | null;
  course_required: boolean;
  color: string;
}

const emptyDraft = (): CategoryDraft => ({ name: '', direction: 'income', required_person_role: null, course_required: false, color: '#378ADD' });

@Component({
  selector: 'arsis-accounting-categories-page',
  imports: [BackLinkComponent, FormsModule, PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Configurazioni" title="Categorie contabili" description="Definisci le voci della prima nota e i dati richiesti per ciascuna.">
      <arsis-back-link class="back-link--compact" link="/settings" label="Configurazioni" />
    </arsis-page-header>

    <section class="card">
      <h2>{{ editing() ? 'Modifica “' + editing()!.name + '”' : 'Nuova categoria' }}</h2>
      <form (ngSubmit)="save()">
        <label>Nome<input name="name" [(ngModel)]="draft.name" maxlength="120" required /></label>
        <label>Verso
          <select name="direction" [(ngModel)]="draft.direction">
            <option value="income">Entrata</option>
            <option value="expense">Uscita</option>
            <option value="both">Entrata o uscita</option>
          </select>
        </label>
        <label>Persona richiesta
          <select name="role" [(ngModel)]="draft.required_person_role">
            <option [ngValue]="null">Nessuna</option>
            <option value="student">Allievo</option>
            <option value="teacher">Insegnante</option>
            <option value="member">Socio</option>
          </select>
        </label>
        <label class="check"><input type="checkbox" name="course" [(ngModel)]="draft.course_required" />Corso obbligatorio</label>
        <label>Colore<input type="color" name="color" [(ngModel)]="draft.color" /></label>
        <div class="actions">
          @if (editing()) { <button type="button" class="button button--secondary" (click)="reset()">Annulla</button> }
          <button class="button button--primary">{{ editing() ? 'Salva' : 'Aggiungi' }}</button>
        </div>
      </form>
      @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
    </section>

    <section class="card list">
      <ul>
        @for (item of active(); track item.id; let first = $first; let last = $last) {
          <li>
            <span class="name"><i [style.background]="item.color ?? 'var(--border-strong)'"></i><strong>{{ item.name }}</strong></span>
            <small>{{ describe(item) }}</small>
            <span class="row-actions">
              <button type="button" class="button button--secondary" [disabled]="first" (click)="move(item, -1)" aria-label="Sposta su">↑</button>
              <button type="button" class="button button--secondary" [disabled]="last" (click)="move(item, 1)" aria-label="Sposta giù">↓</button>
              <button type="button" class="button button--secondary" (click)="edit(item)">Modifica</button>
              <button type="button" class="button button--secondary" (click)="archive(item)">Archivia</button>
            </span>
          </li>
        } @empty {
          <li>Nessuna categoria attiva.</li>
        }
      </ul>
      @if (archived().length) {
        <details>
          <summary>Categorie archiviate ({{ archived().length }})</summary>
          <ul>@for (item of archived(); track item.id) { <li><span class="name">{{ item.name }}</span><small>{{ describe(item) }}</small></li> }</ul>
        </details>
      }
    </section>
  `,
  styles: `
    .card { padding: var(--sp-6); }
    .card + .card { margin-top: var(--sp-5); }
    h2 { margin-top: 0; }
    form { align-items: end; display: grid; gap: var(--sp-4); grid-template-columns: 2fr repeat(2, 1fr) auto auto; }
    label { display: grid; gap: var(--sp-2); }
    label.check { align-items: center; display: flex; min-height: 38px; }
    input:not([type='checkbox']), select { min-height: 38px; min-width: 0; padding: var(--sp-2); }
    input[type='color'] { padding: var(--sp-1); width: 56px; }
    .actions { display: flex; gap: var(--sp-2); grid-column: 1 / -1; justify-content: flex-end; }
    .error { color: var(--color-danger); }
    ul { list-style: none; margin: 0; padding: 0; }
    li { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-3); grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr) auto; padding: var(--sp-3) 0; }
    li:first-child { border-top: 0; }
    .name { align-items: center; display: flex; gap: var(--sp-2); }
    i { border-radius: var(--radius-full); display: inline-block; flex: none; height: 12px; width: 12px; }
    small { color: var(--text-secondary); }
    .row-actions { display: flex; gap: var(--sp-2); }
    details { margin-top: var(--sp-5); }
    summary { color: var(--text-secondary); cursor: pointer; }
    @media (max-width: 800px) { form, li { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccountingCategoriesPageComponent {
  private readonly api = inject(AccountingService);
  private readonly categories = signal<AccountingCategory[]>([]);

  protected readonly active = computed(() => this.categories().filter((c) => !c.archived_at));
  protected readonly archived = computed(() => this.categories().filter((c) => c.archived_at));
  protected readonly editing = signal<AccountingCategory | null>(null);
  protected readonly error = signal('');
  protected draft = emptyDraft();

  constructor() {
    this.load();
  }

  protected describe(item: AccountingCategory): string {
    const parts = [DIRECTION_LABELS[item.direction]];
    if (item.required_person_role) parts.push(`${ROLE_LABELS[item.required_person_role].toLowerCase()} richiesto`);
    if (item.course_required) parts.push('corso richiesto');
    return parts.join(' · ');
  }

  protected edit(item: AccountingCategory): void {
    this.editing.set(item);
    this.error.set('');
    this.draft = { name: item.name, direction: item.direction, required_person_role: item.required_person_role, course_required: item.course_required, color: item.color ?? '#378ADD' };
  }

  protected reset(): void {
    this.editing.set(null);
    this.error.set('');
    this.draft = emptyDraft();
  }

  protected save(): void {
    const name = this.draft.name.trim();
    if (!name) return;
    const payload: AccountingCategoryWrite = { ...this.draft, name, color: this.draft.color.toUpperCase() };
    const current = this.editing();
    const request = current
      ? this.api.updateCategory(current.id, { ...payload, version: current.version })
      : this.api.createCategory({ ...payload, display_order: this.nextOrder() });
    request.subscribe({ next: () => { this.reset(); this.load(); }, error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Salvataggio non riuscito.')) });
  }

  protected move(item: AccountingCategory, delta: -1 | 1): void {
    const list = this.active();
    const other = list[list.indexOf(item) + delta];
    if (!other) return;
    // Renumber in steps of 10 so the two swapped rows always end up with distinct positions.
    const position = (c: AccountingCategory) => (list.indexOf(c) + 1) * 10;
    this.api.updateCategory(item.id, { version: item.version, display_order: position(other) }).subscribe({
      next: () => this.api.updateCategory(other.id, { version: other.version, display_order: position(item) }).subscribe({ next: () => this.load(), error: () => this.load() }),
      error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Riordino non riuscito.')),
    });
  }

  protected archive(item: AccountingCategory): void {
    if (!window.confirm(`Archiviare la categoria “${item.name}”? I movimenti già registrati restano invariati.`)) return;
    this.api.archiveCategory(item.id, item.version).subscribe({
      next: () => { if (this.editing()?.id === item.id) this.reset(); this.load(); },
      error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Archiviazione non riuscita.')),
    });
  }

  private nextOrder(): number {
    return Math.max(0, ...this.active().map((c) => c.display_order)) + 10;
  }

  private load(): void {
    this.api.categories(true).subscribe({ next: (items) => this.categories.set(items) });
  }
}
