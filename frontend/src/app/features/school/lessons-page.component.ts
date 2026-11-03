import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PeopleService } from '../people/people.service';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { CoursesService } from './courses.service';
import { Lesson, LessonsService } from './lessons.service';

@Component({
  selector: 'arsis-lessons-page', imports: [DatePipe, PageHeaderComponent, RouterLink],
  template: `<arsis-page-header eyebrow="Scuola" title="Lezioni" description="Agenda e storico delle lezioni dei corsi."><a class="button button--primary" routerLink="/school/lessons/new">＋ Nuova lezione</a></arsis-page-header><div class="table-shell"><table><thead><tr><th>Data e ora</th><th>Corso</th><th>Insegnante</th><th>Argomento</th><th>Stato</th><th></th></tr></thead><tbody>@for(item of lessons();track item.id){<tr><td>{{item.starts_at | date:'dd/MM/yyyy HH:mm'}}</td><td>{{courseName(item.course_id)}}</td><td>{{personName(item.teacher_person_id)}}</td><td>{{item.topic || '—'}}</td><td><span class="status-badge" [class.status-badge--success]="item.status === 'completed'">{{statusLabel(item.status)}}</span></td><td><a [routerLink]="['/school/lessons',item.id]">Apri</a></td></tr>}@empty{<tr><td colspan="6">Nessuna lezione registrata.</td></tr>}</tbody></table></div>`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LessonsPageComponent {
  private readonly service = inject(LessonsService); private readonly coursesService = inject(CoursesService); private readonly peopleService = inject(PeopleService);
  protected readonly lessons = signal<Lesson[]>([]); private readonly courses = signal(new Map<number, string>()); private readonly people = signal(new Map<number, string>());
  constructor() { this.service.list().subscribe({next: page => this.lessons.set(page.items)}); this.coursesService.list().subscribe({next: page => this.courses.set(new Map(page.items.map(course => [course.id, course.name])))}); this.peopleService.listPeople('').subscribe({next: page => this.people.set(new Map(page.items.map(person => [person.id, `${person.first_name} ${person.last_name}`])))}); }
  protected courseName(id: number): string { return this.courses().get(id) ?? `Corso #${id}`; }
  protected personName(id: number): string { return this.people().get(id) ?? `Insegnante #${id}`; }
  protected statusLabel(status: Lesson['status']): string { return {planned: 'Pianificata', completed: 'Completata', cancelled: 'Annullata'}[status]; }
}
