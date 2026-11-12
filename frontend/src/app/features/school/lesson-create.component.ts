import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { apiErrorMessage } from '../../core/api/api-error';
import { PeopleService, PersonListItem } from '../people/people.service';
import { Course, CoursesService } from './courses.service';
import { LessonsService } from './lessons.service';
import { BackLinkComponent } from '../../shared/ui/back-link.component';

@Component({
  selector: 'arsis-lesson-create',
  imports: [BackLinkComponent, FormsModule],
  template: `
    <arsis-back-link link="/school/lessons" label="Tutte le lezioni" />
    <article class="card">
      <h1>Nuova lezione</h1>
      <form (ngSubmit)="save()">
        <label>Corso
          <select name="course" [(ngModel)]="courseId" (ngModelChange)="courseChanged($event)" required>
            <option [ngValue]="null">Seleziona…</option>
            @for (c of courses(); track c.id) { <option [ngValue]="c.id">{{ c.name }}</option> }
          </select>
        </label>
        <label>Insegnante
          <select name="teacher" [(ngModel)]="teacherId" required>
            <option [ngValue]="null">Seleziona…</option>
            @for (p of teachers(); track p.id) { <option [ngValue]="p.id">{{ p.last_name }} {{ p.first_name }}</option> }
          </select>
          <small>Proposto dal corso; cambialo per una sostituzione.</small>
        </label>
        <label>Inizio<input name="starts" type="datetime-local" [(ngModel)]="startsAt" required /></label>
        <label>Fine<input name="ends" type="datetime-local" [(ngModel)]="endsAt" /></label>
        <label>Argomento<input name="topic" [(ngModel)]="topic" /></label>
        <label>Note<textarea name="notes" [(ngModel)]="notes"></textarea></label>
        @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
        <button class="button button--primary" [disabled]="saving()">Crea lezione</button>
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
export class LessonCreateComponent {
  private readonly service = inject(LessonsService);
  private readonly router = inject(Router);

  private readonly people = toSignal(inject(PeopleService).listPeople('').pipe(map((page) => page.items), catchError(() => of<PersonListItem[]>([]))), { initialValue: [] });
  protected readonly teachers = computed(() => this.people().filter((p) => !p.archived_at && p.roles.includes('teacher')));
  protected readonly courses = toSignal(
    inject(CoursesService).list().pipe(
      map((page) => page.items.filter((c) => !c.archived_at)),
      catchError(() => of<Course[]>([])),
    ),
    { initialValue: [] },
  );
  protected readonly saving = signal(false);
  protected readonly error = signal('');

  // Opened from a course page as /school/lessons/new?course=ID.
  protected courseId: number | null = Number(inject(ActivatedRoute).snapshot.queryParamMap.get('course')) || null;
  protected teacherId: number | null = null;
  protected startsAt = '';
  protected endsAt = '';
  protected topic = '';
  protected notes = '';

  constructor() {
    // Courses arrive asynchronously: propose the teacher of a preselected course once they do.
    const preselected = this.courseId;
    if (preselected) {
      inject(CoursesService).get(preselected).subscribe({ next: (course) => { this.teacherId ??= course.teacher_person_id; } });
    }
  }

  protected courseChanged(id: number | null): void {
    const course = this.courses().find((c) => c.id === id);
    if (course) this.teacherId = course.teacher_person_id;
  }

  protected save(): void {
    if (!this.courseId || !this.teacherId || !this.startsAt) {
      this.error.set('Compila i campi obbligatori.');
      return;
    }
    this.saving.set(true);
    this.service.create({ course_id: this.courseId, teacher_person_id: this.teacherId, starts_at: this.startsAt, ends_at: this.endsAt || null, topic: this.topic || null, notes: this.notes || null }).subscribe({
      next: (item) => void this.router.navigate(['/school/lessons', item.id]),
      error: (err: unknown) => {
        this.saving.set(false);
        this.error.set(apiErrorMessage(err, 'Creazione della lezione non riuscita.'));
      },
    });
  }
}
