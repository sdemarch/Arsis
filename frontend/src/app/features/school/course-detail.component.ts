import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

import schoolData from '../../../assets/mock/school.json';
import peopleData from '../../../assets/mock/people.json';
import { DetailCardComponent } from '../../shared/ui/detail-card.component';

@Component({
  selector: 'arsis-course-detail',
  imports: [DetailCardComponent, FormsModule],
  template: `
    <arsis-detail-card backLink="/school/courses" backLabel="Tutti i corsi" eyebrow="Corso" [title]="draft.name" [subtitle]="draft.mode + ' · ' + teacherName(draft.teacherId)" [editing]="editing()" (editRequested)="toggleEditing()">
      <div detail-visual class="course-visual" [style.background]="draft.background" [style.color]="draft.color">♫</div>
      <div class="detail-sections">
        <section>
          <header><div><p class="section-kicker">Offerta formativa</p><h2>Dettagli corso</h2></div><span class="status-badge status-badge--success">Attivo</span></header>
          <div class="field-grid">
            <label><span>Nome corso</span>@if (editing()) { <input [(ngModel)]="draft.name" /> } @else { <strong>{{ draft.name }}</strong> }</label>
            <label><span>Modalità</span>@if (editing()) { <select [(ngModel)]="draft.mode"><option>Individuale</option><option>Collettivo</option></select> } @else { <strong>{{ draft.mode }}</strong> }</label>
            <label><span>Insegnante</span>@if (editing()) { <select [(ngModel)]="draft.teacherId">@for (teacher of teachers; track teacher.id) { <option [value]="teacher.id">{{ teacher.name }}</option> }</select> } @else { <strong>{{ teacherName(draft.teacherId) }}</strong> }</label>
            <label><span>Orario</span>@if (editing()) { <input [(ngModel)]="draft.schedule" /> } @else { <strong>{{ draft.schedule }}</strong> }</label>
            <label><span>Tariffa annua</span>@if (editing()) { <input [(ngModel)]="draft.fee" /> } @else { <strong>{{ draft.fee }}</strong> }</label>
            <label><span>Allievi iscritti</span>@if (editing()) { <input type="number" min="0" [(ngModel)]="draft.students" /> } @else { <strong>{{ draft.students }}</strong> }</label>
          </div>
        </section>
        <section>
          <header><div><p class="section-kicker">Didattica</p><h2>Descrizione e note</h2></div></header>
          @if (editing()) { <textarea [(ngModel)]="description" rows="4" placeholder="Aggiungi obiettivi, programma o note sul corso…"></textarea> } @else { <p class="empty-value">{{ description || 'Nessuna descrizione inserita.' }}</p> }
        </section>
      </div>
    </arsis-detail-card>
  `,
  styleUrls: ['../../shared/ui/detail-fields.css', './course-detail.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CourseDetailComponent {
  private readonly courseId = inject(ActivatedRoute).snapshot.paramMap.get('courseId');
  private readonly source = schoolData.courses.find((course) => course.id === this.courseId) ?? schoolData.courses[0];
  protected readonly editing = signal(false);
  protected readonly teachers = peopleData.people.filter((person) => person.roles.includes('Insegnante'));
  protected draft = { ...this.source };
  protected description = '';

  protected toggleEditing(): void {
    this.editing.update((value) => !value);
  }

  protected teacherName(teacherId: string): string {
    return peopleData.people.find((person) => person.id === teacherId)?.name ?? 'Non assegnato';
  }
}
