import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';

import { apiErrorMessage } from '../../core/api/api-error';
import { RoleType, RoleTypesService } from '../../core/roles/role-types.service';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

interface RoleDraft {
  name: string;
  plural_name: string;
  description: string;
}

const emptyDraft = (): RoleDraft => ({ name: '', plural_name: '', description: '' });

/** The roles people can hold (RB-21): built-in ones can be renamed, custom ones added. */
@Component({
  selector: 'arsis-roles-page',
  imports: [BackLinkComponent, FormsModule, PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Configurazioni" title="Ruoli" description="I ruoli che si possono assegnare alle persone. I nomi al plurale compaiono nel menu di Soci.">
      <arsis-back-link class="back-link--compact" link="/settings" label="Configurazioni" />
    </arsis-page-header>

    <section class="card">
      <h2>{{ editing() ? 'Modifica “' + editing()!.name + '”' : 'Nuovo ruolo' }}</h2>
      <form (ngSubmit)="save()">
        <label>Nome<input name="name" [(ngModel)]="draft.name" maxlength="100" required placeholder="Es. Volontario" /></label>
        <label>Nome al plurale<input name="plural" [(ngModel)]="draft.plural_name" maxlength="100" required placeholder="Es. Volontari" /></label>
        <label class="full">Descrizione<input name="description" [(ngModel)]="draft.description" maxlength="500" /></label>
        <div class="actions">
          @if (editing()) { <button type="button" class="button button--secondary" (click)="reset()">Annulla</button> }
          <button class="button button--primary" [disabled]="busy()">{{ editing() ? 'Salva' : 'Aggiungi' }}</button>
        </div>
      </form>
      @if (editing()?.is_system) { <p class="hint">Ruolo predefinito: puoi cambiarne nome e descrizione, mentre corsi, iscrizioni, strumenti e dati del socio restano legati a esso.</p> }
      @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
    </section>

    <section class="card list">
      <ul>
        @for (role of roles.active(); track role.id; let first = $first; let last = $last) {
          <li>
            <span class="name">
              <strong>{{ role.name }}</strong>
              @if (role.is_system) { <span class="badge">Predefinito</span> }
              <small>{{ role.plural_name }}@if (role.description) { · {{ role.description }} }</small>
            </span>
            <span class="count">{{ role.active_people }} {{ role.active_people === 1 ? 'persona' : 'persone' }}</span>
            <span class="row-actions">
              <button type="button" class="button button--secondary" [disabled]="first || busy()" (click)="move(role, -1)" aria-label="Sposta su">↑</button>
              <button type="button" class="button button--secondary" [disabled]="last || busy()" (click)="move(role, 1)" aria-label="Sposta giù">↓</button>
              <button type="button" class="button button--secondary" (click)="edit(role)">Modifica</button>
              @if (!role.is_system) {
                <button type="button" class="button button--secondary" [disabled]="busy()" (click)="archive(role)"
                  [title]="role.active_people ? 'Chiudi prima i ruoli attivi delle persone' : ''">Archivia</button>
              }
            </span>
          </li>
        }
      </ul>
      @if (roles.archived().length) {
        <details>
          <summary>Ruoli archiviati ({{ roles.archived().length }})</summary>
          <ul>@for (role of roles.archived(); track role.id) { <li><span class="name">{{ role.name }}<small>{{ role.plural_name }}</small></span></li> }</ul>
        </details>
      }
      <p class="hint">Un ruolo personalizzato si può archiviare quando nessuno lo ricopre più e nessuna categoria contabile attiva lo richiede. Le assegnazioni passate restano nello storico.</p>
    </section>
  `,
  styles: `
    .card { padding: var(--sp-6); }
    .card + .card { margin-top: var(--sp-5); }
    h2 { margin-top: 0; }
    form { align-items: end; display: grid; gap: var(--sp-4); grid-template-columns: repeat(2, minmax(0, 1fr)); }
    label { display: grid; gap: var(--sp-2); }
    label.full, .actions { grid-column: 1 / -1; }
    input { min-height: 38px; min-width: 0; padding: var(--sp-2); }
    .actions { display: flex; gap: var(--sp-2); justify-content: flex-end; }
    .hint { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-4) 0 0; }
    .error { color: var(--color-danger); }
    ul { list-style: none; margin: 0; padding: 0; }
    li { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-3); grid-template-columns: minmax(0, 1.6fr) auto auto; padding: var(--sp-3) 0; }
    li:first-child { border-top: 0; }
    .name { align-items: baseline; display: flex; flex-wrap: wrap; gap: var(--sp-1) var(--sp-2); }
    .name small { color: var(--text-secondary); flex-basis: 100%; }
    .badge { background: var(--color-accent-soft); border-radius: 999px; color: var(--color-accent-hover); font-size: var(--text-xs); padding: 0 var(--sp-2); }
    .count { color: var(--text-secondary); font-size: var(--text-sm); font-variant-numeric: tabular-nums; white-space: nowrap; }
    .row-actions { display: flex; gap: var(--sp-2); }
    details { margin-top: var(--sp-5); }
    summary { color: var(--text-secondary); cursor: pointer; }
    @media (max-width: 800px) { form, li { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RolesPageComponent {
  protected readonly roles = inject(RoleTypesService);
  protected readonly editing = signal<RoleType | null>(null);
  protected readonly busy = signal(false);
  protected readonly error = signal('');
  protected draft = emptyDraft();

  constructor() {
    this.reload();
  }

  protected edit(role: RoleType): void {
    this.editing.set(role);
    this.error.set('');
    this.draft = { name: role.name, plural_name: role.plural_name, description: role.description ?? '' };
  }

  protected reset(): void {
    this.editing.set(null);
    this.error.set('');
    this.draft = emptyDraft();
  }

  protected save(): void {
    const name = this.draft.name.trim();
    const plural = this.draft.plural_name.trim();
    if (!name || !plural) {
      this.error.set('Indica il nome del ruolo al singolare e al plurale.');
      return;
    }
    const payload = { name, plural_name: plural, description: this.draft.description.trim() || null };
    const current = this.editing();
    this.run(current ? this.roles.update(current.id, { ...payload, version: current.version }) : this.roles.create(payload), 'Salvataggio non riuscito.', true);
  }

  /** Swap display order with the neighbour. */
  protected move(role: RoleType, step: -1 | 1): void {
    const list = this.roles.active();
    const index = list.findIndex((item) => item.id === role.id);
    const other = list[index + step];
    if (!other) return;
    this.busy.set(true);
    this.roles.update(role.id, { display_order: other.display_order, version: role.version }).subscribe({
      next: () => this.run(this.roles.update(other.id, { display_order: role.display_order, version: other.version }), 'Riordino non riuscito.'),
      error: (err: unknown) => { this.busy.set(false); this.error.set(apiErrorMessage(err, 'Riordino non riuscito.')); this.reload(); },
    });
  }

  protected archive(role: RoleType): void {
    if (!window.confirm(`Archiviare il ruolo “${role.name}”? Non si potrà più assegnare.`)) return;
    this.run(this.roles.archive(role.id, role.version), 'Archiviazione non riuscita.', this.editing()?.id === role.id);
  }

  private run(request: Observable<RoleType>, failure: string, resetForm = false): void {
    this.busy.set(true);
    this.error.set('');
    request.subscribe({
      next: () => { this.busy.set(false); if (resetForm) this.reset(); this.reload(); },
      error: (err: unknown) => { this.busy.set(false); this.error.set(apiErrorMessage(err, failure)); this.reload(); },
    });
  }

  private reload(): void {
    this.roles.refresh().subscribe({ error: () => this.error.set('Impossibile caricare i ruoli.') });
  }
}
