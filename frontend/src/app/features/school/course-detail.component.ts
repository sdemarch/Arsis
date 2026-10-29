import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { DetailCardComponent } from '../../shared/ui/detail-card.component';
import { Course, CoursesService } from './courses.service';

@Component({
  selector: 'arsis-course-detail', imports: [DetailCardComponent, FormsModule],
  template: `@if (course(); as item) { <arsis-detail-card backLink="/school/courses" backLabel="Tutti i corsi" eyebrow="Corso" [title]="item.name" [subtitle]="item.mode === 'individual' ? 'Individuale' : 'Gruppo'" [editing]="editing()" [editable]="!item.archived_at" (editRequested)="editing() ? save() : beginEdit()"><div detail-visual class="course-visual" [style.background]="item.color + '20'" [style.color]="item.color">♫</div><div class="detail-sections"><section><header><div><p class="section-kicker">Offerta formativa</p><h2>Dettagli corso</h2></div><span class="status-badge" [class.status-badge--success]="item.status === 'active'">{{ item.status === 'active' ? 'Attivo' : 'Inattivo' }}</span></header><div class="field-grid"><label><span>Nome corso</span>@if(editing()){<input [(ngModel)]="draft.name"/>}@else{<strong>{{item.name}}</strong>}</label><label><span>Modalità</span>@if(editing()){<select [(ngModel)]="draft.mode"><option value="individual">Individuale</option><option value="group">Gruppo</option></select>}@else{<strong>{{item.mode === 'individual' ? 'Individuale' : 'Gruppo'}}</strong>}</label><label><span>Tariffa annua</span>@if(editing()){<input type="number" min="0" [(ngModel)]="draft.annual_fee"/>}@else{<strong>{{item.annual_fee}} €</strong>}</label></div></section><section><header><div><p class="section-kicker">Didattica</p><h2>Descrizione</h2></div></header>@if(editing()){<textarea [(ngModel)]="draft.description" rows="4"></textarea>}@else{<p class="empty-value">{{item.description || 'Nessuna descrizione inserita.'}}</p>}</section>@if(!item.archived_at){<section><button class="button button--secondary" type="button" (click)="archive()">Archivia corso</button></section>}</div></arsis-detail-card> } @else { <p>Caricamento corso…</p> }`,
  styleUrls: ['../../shared/ui/detail-fields.css', './course-detail.component.css'], changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CourseDetailComponent {
  private readonly service = inject(CoursesService); private readonly router = inject(Router);
  private readonly courseId = Number(inject(ActivatedRoute).snapshot.paramMap.get('courseId'));
  protected readonly course = signal<Course | null>(null); protected readonly editing = signal(false); protected draft: Partial<Course> = {};
  constructor() { this.load(); }
  protected beginEdit(): void { this.draft = { ...this.course()! }; this.editing.set(true); }
  protected save(): void { const course = this.course(); if (course) this.service.update(course.id, { ...this.draft, version: course.version }).subscribe({ next: () => { this.editing.set(false); this.load(); } }); }
  protected archive(): void { const course = this.course(); if (course && window.confirm(`Archiviare ${course.name}?`)) this.service.archive(course.id, course.version).subscribe({ next: () => void this.router.navigate(['/school/courses']) }); }
  private load(): void { this.service.get(this.courseId).subscribe({ next: (course) => this.course.set(course) }); }
}
