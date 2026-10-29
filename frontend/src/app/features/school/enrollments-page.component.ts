import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PeopleService } from '../people/people.service';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { CoursesService } from './courses.service';
import { Enrollment, EnrollmentsService } from './enrollments.service';

@Component({
  selector: 'arsis-enrollments-page', imports: [PageHeaderComponent, RouterLink],
  template: `<arsis-page-header eyebrow="Scuola" title="Iscrizioni" description="Allievi iscritti ai corsi attivi."><a class="button button--primary" routerLink="/school/enrollments/new">＋ Nuova iscrizione</a></arsis-page-header><div class="table-shell"><table><thead><tr><th>Allievo</th><th>Corso</th><th>Inizio</th><th>Stato</th><th></th></tr></thead><tbody>@for(item of enrollments();track item.id){<tr><td>{{personName(item.student_person_id)}}</td><td>{{courseName(item.course_id)}}</td><td>{{item.starts_on}}</td><td><span class="status-badge" [class.status-badge--success]="item.status === 'active'">{{statusLabel(item.status)}}</span></td><td><a [routerLink]="['/school/enrollments',item.id]">Apri</a></td></tr>}@empty{<tr><td colspan="5">Nessuna iscrizione attiva.</td></tr>}</tbody></table></div>`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EnrollmentsPageComponent {
  private readonly service = inject(EnrollmentsService); private readonly coursesService = inject(CoursesService); private readonly peopleService = inject(PeopleService);
  protected readonly enrollments = signal<Enrollment[]>([]); private readonly courses = signal(new Map<number, string>()); private readonly people = signal(new Map<number, string>());
  constructor() { this.service.list().subscribe({next: page => this.enrollments.set(page.items)}); this.coursesService.list().subscribe({next: page => this.courses.set(new Map(page.items.map(course => [course.id, course.name])))}); this.peopleService.listPeople('').subscribe({next: page => this.people.set(new Map(page.items.map(person => [person.id, `${person.first_name} ${person.last_name}`])))}); }
  protected courseName(id: number): string { return this.courses().get(id) ?? `Corso #${id}`; }
  protected personName(id: number): string { return this.people().get(id) ?? `Allievo #${id}`; }
  protected statusLabel(status: Enrollment['status']): string { return {active: 'Attiva', completed: 'Completata', cancelled: 'Annullata'}[status]; }
}
