import { ChangeDetectionStrategy, Component, computed, effect, inject, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { PersonListItem } from '../people/people.service';
import { Course } from '../school/courses.service';
import {
  AccountingCategory,
  AccountingDirection,
  AccountingAccount,
  AccountingMovement,
  AccountingService,
  ROLE_LABELS,
  apiErrorMessage,
} from './accounting.service';

interface MovementDraft {
  occurred_on: string;
  direction: AccountingDirection;
  account: AccountingAccount;
  category_id: number | null;
  amount: number | null;
  subject: string;
  person_id: number | null;
  course_id: number | null;
  description: string;
  document_reference: string;
  is_highlighted: boolean;
}

const today = (): string => new Date().toISOString().slice(0, 10);

function emptyDraft(): MovementDraft {
  return { occurred_on: today(), direction: 'income', account: 'bank', category_id: null, amount: null, subject: '', person_id: null, course_id: null, description: '', document_reference: '', is_highlighted: false };
}

/** Create or edit a first-note movement, asking for person and course when the category needs them. */
@Component({
  selector: 'arsis-movement-form',
  imports: [FormsModule],
  template: `
    <form (ngSubmit)="submit()">
      <label>Data<input type="date" name="occurred_on" [(ngModel)]="draft.occurred_on" required /></label>
      <label>Categoria
        <select name="category" [(ngModel)]="draft.category_id" (ngModelChange)="categoryChanged($event)" required>
          <option [ngValue]="null">Seleziona…</option>
          @for (c of selectableCategories(); track c.id) { <option [ngValue]="c.id">{{ c.name }}</option> }
        </select>
      </label>
      <label>Verso
        <select name="direction" [(ngModel)]="draft.direction" [disabled]="directionLocked()">
          <option value="income">Entrata</option>
          <option value="expense">Uscita</option>
        </select>
      </label>
      <label>Conto
        <select name="account" [(ngModel)]="draft.account">
          <option value="bank">Banca</option>
          <option value="cash">Cassa</option>
        </select>
      </label>
      <label>{{ personLabel() }}
        <select name="person" [(ngModel)]="draft.person_id" (ngModelChange)="personChanged($event)" [required]="!!requiredRole()">
          <option [ngValue]="null">{{ requiredRole() ? 'Seleziona…' : 'Nessuna' }}</option>
          @for (p of eligiblePeople(); track p.id) { <option [ngValue]="p.id">{{ p.last_name }} {{ p.first_name }}</option> }
        </select>
      </label>
      @if (showCourse()) {
        <label>Corso{{ courseRequired() ? '' : ' (facoltativo)' }}
          <select name="course" [(ngModel)]="draft.course_id" [required]="courseRequired()">
            <option [ngValue]="null">{{ courseRequired() ? 'Seleziona…' : 'Nessuno' }}</option>
            @for (c of eligibleCourses(); track c.id) { <option [ngValue]="c.id">{{ c.name }}</option> }
          </select>
        </label>
      }
      <label>Soggetto<input name="subject" [(ngModel)]="draft.subject" maxlength="200" required /></label>
      <label>Descrizione<input name="description" [(ngModel)]="draft.description" maxlength="500" required /></label>
      <label>Importo (€)<input type="number" name="amount" min="0.01" step="0.01" [(ngModel)]="draft.amount" required /></label>
      <label>Riferimento documento<input name="document_reference" [(ngModel)]="draft.document_reference" maxlength="200" placeholder="Facoltativo" /></label>
      <div class="actions">
        <label class="flag" [class.on]="draft.is_highlighted" title="Segnala il movimento come da verificare">
          <input type="checkbox" name="is_highlighted" [(ngModel)]="draft.is_highlighted" /><span aria-hidden="true">⚑</span>Evidenziato
        </label>
        @if (movement()) { <button type="button" class="button button--secondary" (click)="cancelled.emit()">Annulla</button> }
        <button class="button button--primary" [disabled]="saving()">{{ movement() ? 'Salva modifiche' : 'Registra' }}</button>
      </div>
      @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
    </form>
  `,
  styles: `
    form { display: grid; gap: var(--sp-4); grid-template-columns: repeat(3, minmax(0, 1fr)); }
    label { color: var(--text-secondary); display: grid; font-size: var(--text-sm); font-weight: var(--weight-medium); gap: var(--sp-2); }
    input, select { background: var(--bg-surface); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); box-shadow: inset 0 1px 1px hsla(160, 20%, 10%, .02); box-sizing: border-box; color: var(--text-primary); font: inherit; min-height: 42px; min-width: 0; padding: 0 var(--sp-3); transition: background-color var(--duration-fast) var(--ease), border-color var(--duration-fast) var(--ease), box-shadow var(--duration-fast) var(--ease); width: 100%; }
    input:hover, select:hover { border-color: var(--border-strong); }
    input:focus, select:focus { background: var(--bg-surface); border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-soft); outline: 0; }
    input:disabled, select:disabled { background: var(--bg-raised); color: var(--text-tertiary); cursor: not-allowed; }
    input::placeholder { color: var(--text-tertiary); }
    select { cursor: pointer; }
    input[type='date'], input[type='number'] { font-variant-numeric: tabular-nums; }
    .actions { align-items: center; display: flex; gap: var(--sp-2); grid-column: 1 / -1; justify-content: flex-end; }
    .flag { align-items: center; background: var(--bg-raised); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-full); color: var(--text-secondary); cursor: pointer; display: inline-flex; font-size: var(--text-sm); gap: var(--sp-1); margin-right: auto; padding: var(--sp-2) var(--sp-3); }
    .flag input { accent-color: var(--color-warn); margin: 0; min-height: 0; padding: 0; width: auto; }
    .flag span { color: var(--color-warn); }
    .flag.on { background: var(--color-warn-soft); border-color: var(--color-warn); color: var(--text-primary); }
    .error { color: var(--color-danger); grid-column: 1 / -1; margin: 0; }
    @media (max-width: 800px) { form { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MovementFormComponent {
  private readonly api = inject(AccountingService);

  readonly categories = input.required<AccountingCategory[]>();
  readonly people = input.required<PersonListItem[]>();
  readonly courses = input.required<Course[]>();
  /** Movement being edited; null registers a new one. */
  readonly movement = input<AccountingMovement | null>(null);
  readonly saved = output<AccountingMovement>();
  readonly cancelled = output<void>();

  protected draft = emptyDraft();
  protected readonly saving = signal(false);
  protected readonly error = signal('');
  private readonly categoryId = signal<number | null>(null);
  private readonly personId = signal<number | null>(null);

  private readonly category = computed(() => this.categories().find((c) => c.id === this.categoryId()));
  protected readonly selectableCategories = computed(() =>
    this.categories().filter((c) => c.is_active || c.id === this.movement()?.category_id),
  );
  protected readonly requiredRole = computed(() => this.category()?.required_person_role ?? null);
  protected readonly courseRequired = computed(() => this.category()?.course_required === true);
  protected readonly directionLocked = computed(() => !!this.category() && this.category()?.direction !== 'both');
  protected readonly showCourse = computed(() => this.courseRequired() || this.requiredRole() === 'student' || this.requiredRole() === 'teacher');
  protected readonly personLabel = computed(() => {
    const role = this.requiredRole();
    return role ? ROLE_LABELS[role] : 'Persona (facoltativa)';
  });
  protected readonly eligiblePeople = computed(() => {
    const role = this.requiredRole();
    return this.people().filter((p) => !p.archived_at && (!role || p.roles.includes(role)));
  });
  protected readonly eligibleCourses = computed(() => {
    const active = this.courses().filter((c) => !c.archived_at);
    const teacherId = this.requiredRole() === 'teacher' ? this.personId() : null;
    return teacherId ? active.filter((c) => c.teacher_person_id === teacherId) : active;
  });

  constructor() {
    effect(() => {
      const movement = this.movement();
      this.draft = movement
        ? { ...movement, amount: Number(movement.amount), document_reference: movement.document_reference ?? '' }
        : emptyDraft();
      this.categoryId.set(this.draft.category_id);
      this.personId.set(this.draft.person_id);
      this.error.set('');
    });
  }

  protected categoryChanged(id: number | null): void {
    this.categoryId.set(id);
    const category = this.category();
    if (category && category.direction !== 'both') this.draft.direction = category.direction;
    if (this.requiredRole() && !this.eligiblePeople().some((p) => p.id === this.draft.person_id)) this.personChanged(null);
    if (!this.showCourse()) this.draft.course_id = null;
  }

  protected personChanged(id: number | null): void {
    this.draft.person_id = id;
    this.personId.set(id);
    const person = this.people().find((p) => p.id === id);
    if (person) this.draft.subject = `${person.first_name} ${person.last_name}`;
    if (!this.eligibleCourses().some((c) => c.id === this.draft.course_id)) this.draft.course_id = null;
  }

  protected submit(): void {
    const d = this.draft;
    if (!d.category_id || !d.subject.trim() || !d.description.trim() || !d.amount || d.amount <= 0 || (this.requiredRole() && !d.person_id) || (this.courseRequired() && !d.course_id)) {
      this.error.set('Compila i campi obbligatori.');
      return;
    }
    const payload = {
      occurred_on: d.occurred_on,
      direction: d.direction,
      account: d.account,
      category_id: d.category_id,
      amount: d.amount.toFixed(2),
      subject: d.subject.trim(),
      person_id: d.person_id,
      course_id: d.course_id,
      description: d.description.trim(),
      document_reference: d.document_reference.trim() || null,
      is_highlighted: d.is_highlighted,
    };
    const existing = this.movement();
    const request = existing ? this.api.update(existing.id, { ...payload, version: existing.version }) : this.api.create(payload);
    this.saving.set(true);
    request.subscribe({
      next: (movement) => {
        this.saving.set(false);
        this.error.set('');
        if (!existing) {
          this.draft = { ...emptyDraft(), occurred_on: d.occurred_on, account: d.account };
          this.categoryId.set(null);
          this.personId.set(null);
        }
        this.saved.emit(movement);
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.error.set(apiErrorMessage(err, 'Salvataggio non riuscito: controlla categoria e dati.'));
      },
    });
  }
}
