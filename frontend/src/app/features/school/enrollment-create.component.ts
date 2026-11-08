import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { apiErrorMessage } from '../../core/api/api-error';
import { PeopleService, PersonListItem } from '../people/people.service';
import { Course, CoursesService } from './courses.service';
import { EnrollmentsService } from './enrollments.service';

@Component({
  selector: 'arsis-enrollment-create',
  imports: [FormsModule, RouterLink],
  template: `
    <a routerLink="/school/enrollments">← Tutte le iscrizioni</a>
    <article class="card">
      <h1>Nuova iscrizione</h1>
      <form (ngSubmit)="save()">
        <label>Corso
          <select name="course" [(ngModel)]="courseId" required>
            <option [ngValue]="null">Seleziona…</option>
            @for (c of courses(); track c.id) { <option [ngValue]="c.id">{{ c.name }}</option> }
          </select>
        </label>
        <label>Allievo
          <select name="student" [(ngModel)]="studentId" required>
            <option [ngValue]="null">Seleziona…</option>
            @for (p of students(); track p.id) { <option [ngValue]="p.id">{{ p.last_name }} {{ p.first_name }}</option> }
          </select>
          @if (!students().length) { <small>Nessuna persona con ruolo allievo: assegnalo dalla scheda persona.</small> }
        </label>
        <label>Data iscrizione<input name="enrolled" type="date" [(ngModel)]="enrolledOn" required /></label>
        <label>Inizio corso<input name="starts" type="date" [(ngModel)]="startsOn" required /></label>
        <label>Note<textarea name="notes" [(ngModel)]="notes"></textarea></label>
        @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
        <button class="button button--primary" [disabled]="saving()">Crea iscrizione</button>
      </form>
    </article>
  `,
  styles: `
    :host { display: block; margin: auto; max-width: 720px; }
    .card { padding: var(--sp-8); }
    form { display: grid; gap: var(--sp-4); }
    label { display: grid; gap: var(--sp-2); }
    input, select, textarea { padding: var(--sp-2); }
    small { color: var(--text-secondary); }
    .error { color: var(--color-danger); margin: 0; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EnrollmentCreateComponent {
  private readonly service = inject(EnrollmentsService);
  private readonly router = inject(Router);

  private readonly people = toSignal(inject(PeopleService).listPeople('').pipe(map((page) => page.items), catchError(() => of<PersonListItem[]>([]))), { initialValue: [] });
  protected readonly students = computed(() => this.people().filter((p) => !p.archived_at && p.roles.includes('student')));
  protected readonly courses = toSignal(inject(CoursesService).list().pipe(map((page) => page.items.filter((c) => !c.archived_at)), catchError(() => of<Course[]>([]))), { initialValue: [] });
  protected readonly saving = signal(false);
  protected readonly error = signal('');

  // Opened from a course page as /school/enrollments/new?course=ID.
  protected courseId: number | null = Number(inject(ActivatedRoute).snapshot.queryParamMap.get('course')) || null;
  protected studentId: number | null = null;
  protected enrolledOn = new Date().toISOString().slice(0, 10);
  protected startsOn = this.enrolledOn;
  protected notes = '';

  protected save(): void {
    if (!this.courseId || !this.studentId) {
      this.error.set('Seleziona corso e allievo.');
      return;
    }
    this.saving.set(true);
    this.service.create({ course_id: this.courseId, student_person_id: this.studentId, enrolled_on: this.enrolledOn, starts_on: this.startsOn, notes: this.notes || null }).subscribe({
      next: (item) => void this.router.navigate(['/school/enrollments', item.id]),
      error: (err: unknown) => {
        this.saving.set(false);
        this.error.set(apiErrorMessage(err, 'Creazione dell’iscrizione non riuscita.'));
      },
    });
  }
}
