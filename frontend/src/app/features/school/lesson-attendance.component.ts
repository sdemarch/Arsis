import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { AttendanceService, LessonAttendance } from './attendance.service';

@Component({
  selector: 'arsis-lesson-attendance', imports: [PageHeaderComponent],
  template: `<arsis-page-header eyebrow="Scuola" title="Registro presenze" description="Registra le presenze degli allievi iscritti alla data della lezione."><div class="actions"><button class="button button--secondary" type="button" (click)="downloadTemplate()">Scarica modello Excel</button><label class="button button--secondary">Importa Excel<input type="file" accept=".xlsx" (change)="importFile($event)"/></label><button class="button button--primary" type="button" (click)="save()">Salva presenze</button></div></arsis-page-header>@if(message()){<p class="notice">{{message()}}</p>}<div class="table-shell"><table><thead><tr><th>Allievo</th><th>Presenza</th></tr></thead><tbody>@for(row of rows();track row.student_person_id){<tr><td>{{row.student_name}}</td><td><select [value]="row.attendance || ''" (change)="setAttendance(row.student_person_id, $any($event.target).value)"><option value="">Non registrata</option><option value="present">Presente</option><option value="absent">Assente</option></select></td></tr>}@empty{<tr><td colspan="2">Nessun allievo iscritto alla data della lezione.</td></tr>}</tbody></table></div>`,
  styles: `:host{display:block}.actions{display:flex;gap:var(--sp-3);align-items:center}.actions input{display:none}.notice{background:var(--color-surface-alt);padding:var(--sp-3);border-radius:var(--radius-md)}select{padding:var(--sp-2)}`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LessonAttendanceComponent {
  private readonly service = inject(AttendanceService); private readonly lessonId = Number(inject(ActivatedRoute).snapshot.paramMap.get('lessonId'));
  protected readonly rows = signal<LessonAttendance[]>([]); protected readonly message = signal('');
  constructor() { if (this.lessonId > 0) this.load(); else this.message.set('Apri il registro dalla pagina di una lezione.'); }
  protected setAttendance(studentId: number, value: string): void { const attendance = (value || null) as LessonAttendance['attendance']; this.rows.update(rows => rows.map(row => row.student_person_id === studentId ? {...row, attendance} : row)); }
  protected save(): void { if (this.lessonId > 0) this.service.save(this.lessonId, this.rows().map(({student_person_id, attendance}) => ({student_person_id, attendance}))).subscribe({next: result => { this.message.set(`${result.processed_rows} presenze salvate.`); this.load(); }}); }
  protected downloadTemplate(): void { if (this.lessonId > 0) this.service.template(this.lessonId).subscribe({next: file => { const url=URL.createObjectURL(file); const anchor=document.createElement('a'); anchor.href=url; anchor.download=`presenze-lezione-${this.lessonId}.xlsx`; anchor.click(); URL.revokeObjectURL(url); }}); }
  protected importFile(event: Event): void { const file=(event.target as HTMLInputElement).files?.[0]; if (file && this.lessonId > 0) this.service.import(this.lessonId, file).subscribe({next: result => { this.message.set(`${result.processed_rows} presenze importate.`); this.load(); }}); }
  private load(): void { this.service.list(this.lessonId).subscribe({next: rows => this.rows.set(rows)}); }
}
