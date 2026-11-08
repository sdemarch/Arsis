import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { apiErrorMessage } from '../../core/api/api-error';
import { COURSE_COLORS } from '../../core/config/course-colors';
import { PeopleService, PersonListItem } from '../people/people.service';
import { CataloguesService, Instrument } from '../settings/catalogues.service';
import { CoursesService } from './courses.service';

@Component({
  selector: 'arsis-course-create',
  imports: [FormsModule, RouterLink],
  template: `
    <a routerLink="/school/courses">← Tutti i corsi</a>
    <article class="card">
      <h1>Nuovo corso</h1>
      <form (ngSubmit)="save()">
        <label>Nome<input name="name" [(ngModel)]="name" required /></label>
        <label>Insegnante
          <select name="teacher" [(ngModel)]="teacherId" required>
            <option [ngValue]="null">Seleziona…</option>
            @for (p of teachers(); track p.id) { <option [ngValue]="p.id">{{ p.last_name }} {{ p.first_name }}</option> }
          </select>
          @if (!teachers().length) { <small>Nessuna persona con ruolo insegnante: assegnalo dalla scheda persona.</small> }
        </label>
        <label>Modalità
          <select name="mode" [(ngModel)]="mode"><option value="individual">Individuale</option><option value="group">Gruppo</option></select>
        </label>
        <label>Categoria
          <select name="category" [(ngModel)]="category"><option value="ensemble">Ensemble</option><option value="instrument">Strumento</option></select>
        </label>
        @if (category === 'instrument') {
          <label>Strumento
            <select name="instrument" [(ngModel)]="instrumentId" required>
              <option [ngValue]="null">Seleziona…</option>
              @for (i of instruments(); track i.id) { <option [ngValue]="i.id">{{ i.name }}</option> }
            </select>
          </label>
        }
        <label>Tariffa annua (€)<input name="fee" type="number" [(ngModel)]="annualFee" min="0" step="0.01" required /></label>
        <fieldset>
          <legend>Colore</legend>
          <div class="swatches">
            @for (c of colors; track c.value) {
              <label class="swatch" [style.background]="c.value" [class.selected]="color === c.value" [title]="c.name">
                <input type="radio" name="color" [value]="c.value" [(ngModel)]="color" [attr.aria-label]="c.name" />
              </label>
            }
          </div>
        </fieldset>
        @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
        <button class="button button--primary" [disabled]="saving()">Crea corso</button>
      </form>
    </article>
  `,
  styles: `
    :host { display: block; margin: auto; max-width: 720px; }
    .card { padding: var(--sp-8); }
    form { display: grid; gap: var(--sp-4); }
    label { display: grid; gap: var(--sp-2); }
    input, select { padding: var(--sp-2); }
    small { color: var(--text-secondary); }
    fieldset { border: 0; margin: 0; padding: 0; }
    legend { margin-bottom: var(--sp-2); }
    .swatches { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
    .swatch { border: 2px solid transparent; border-radius: var(--radius-full); cursor: pointer; display: block; height: 32px; width: 32px; }
    .swatch.selected { box-shadow: 0 0 0 2px var(--bg-surface), 0 0 0 4px var(--text-primary); }
    .swatch input { opacity: 0; position: absolute; }
    .error { color: var(--color-danger); margin: 0; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CourseCreateComponent {
  private readonly service = inject(CoursesService);
  private readonly router = inject(Router);

  private readonly people = toSignal(inject(PeopleService).listPeople('').pipe(map((page) => page.items), catchError(() => of<PersonListItem[]>([]))), { initialValue: [] });
  protected readonly teachers = computed(() => this.people().filter((p) => !p.archived_at && p.roles.includes('teacher')));
  protected readonly instruments = toSignal(inject(CataloguesService).instruments().pipe(map((page) => page.items.filter((i) => i.is_active)), catchError(() => of<Instrument[]>([]))), { initialValue: [] });
  protected readonly colors = COURSE_COLORS;
  protected readonly saving = signal(false);
  protected readonly error = signal('');

  protected name = '';
  protected teacherId: number | null = null;
  protected instrumentId: number | null = null;
  protected mode: 'individual' | 'group' = 'individual';
  protected category: 'instrument' | 'ensemble' = 'ensemble';
  protected annualFee = 0;
  protected color = COURSE_COLORS[0].value;

  protected save(): void {
    if (!this.name.trim() || !this.teacherId || (this.category === 'instrument' && !this.instrumentId)) {
      this.error.set('Compila i campi obbligatori.');
      return;
    }
    this.saving.set(true);
    this.service.create({
      name: this.name.trim(),
      teacher_person_id: this.teacherId,
      mode: this.mode,
      category: this.category,
      instrument_id: this.category === 'instrument' ? this.instrumentId : null,
      annual_fee: Number(this.annualFee).toFixed(2),
      color: this.color,
    }).subscribe({
      next: (course) => void this.router.navigate(['/school/courses', course.id]),
      error: (err: unknown) => {
        this.saving.set(false);
        this.error.set(apiErrorMessage(err, 'Creazione del corso non riuscita.'));
      },
    });
  }
}
