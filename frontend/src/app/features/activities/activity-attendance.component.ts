import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { apiErrorMessage } from '../../core/api/api-error';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { PeopleService, PersonListItem } from '../people/people.service';
import { ActivitiesService, Activity, Attendance, Participant } from './activities.service';

const TYPE_LABELS: Record<Activity['type'], string> = { rehearsal: 'Prova', concert: 'Concerto', event: 'Evento' };

/** Convoked participants of an activity and their attendance register (§9.4–9.5). */
@Component({
  selector: 'arsis-activity-attendance',
  imports: [FormsModule, PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Presenze" [title]="activity()?.title ?? 'Attività'" [description]="subtitle()">
      <a class="button button--secondary" [routerLink]="['/activities', id]">← Scheda attività</a>
    </arsis-page-header>

    <section class="summary">
      <div><strong>{{ rows().length }}</strong><span>Convocati</span></div>
      <div><strong class="present">{{ count('present') }}</strong><span>Presenti</span></div>
      <div><strong class="absent">{{ count('absent') }}</strong><span>Assenti</span></div>
      <div><strong>{{ count(null) }}</strong><span>Da registrare</span></div>
    </section>

    <div class="toolbar">
      <div class="group">
        <button type="button" class="button button--secondary" (click)="markAll('present')" [disabled]="!rows().length">Tutti presenti</button>
        <button type="button" class="button button--secondary" (click)="markAll(null)" [disabled]="!rows().length">Azzera</button>
      </div>
      <div class="group">
        @if (dirty()) { <span class="unsaved">Modifiche non salvate</span> }
        <button type="button" class="button button--primary" (click)="save()" [disabled]="!dirty() || busy()">Salva presenze</button>
      </div>
    </div>

    @if (message()) { <p class="message" [class.error]="failed()" role="status">{{ message() }}</p> }

    <div class="table-shell">
      <table>
        <thead><tr><th>Partecipante</th><th>Convocazione</th><th>Presenza</th><th><span class="visually-hidden">Rimuovi</span></th></tr></thead>
        <tbody>
          @for (row of rows(); track row.person_id) {
            <tr>
              <td><a [routerLink]="['/people', row.person_id]">{{ row.person_name }}</a></td>
              <td><span class="source">{{ row.source === 'automatic' ? 'Musicante attivo' : 'Aggiunto' }}</span></td>
              <td>
                <div class="segmented" role="group" [attr.aria-label]="'Presenza di ' + row.person_name">
                  <button type="button" class="is-present" [class.on]="attendanceOf(row) === 'present'" [attr.aria-pressed]="attendanceOf(row) === 'present'" (click)="toggle(row, 'present')">Presente</button>
                  <button type="button" class="is-absent" [class.on]="attendanceOf(row) === 'absent'" [attr.aria-pressed]="attendanceOf(row) === 'absent'" (click)="toggle(row, 'absent')">Assente</button>
                </div>
              </td>
              <td class="remove"><button type="button" (click)="remove(row)" [attr.aria-label]="'Rimuovi ' + row.person_name" title="Rimuovi dai convocati">×</button></td>
            </tr>
          } @empty {
            <tr><td colspan="4" class="empty">Nessun partecipante. Aggiungi i musicanti attivi o singole persone.</td></tr>
          }
        </tbody>
      </table>
    </div>

    <section class="card add">
      <h2>Convocati</h2>
      <form (ngSubmit)="add()">
        <select name="person" [(ngModel)]="personToAdd" aria-label="Persona da aggiungere">
          <option [ngValue]="null">Aggiungi una persona…</option>
          @for (p of addable(); track p.id) { <option [ngValue]="p.id">{{ p.last_name }} {{ p.first_name }}</option> }
        </select>
        <button class="button button--secondary" [disabled]="!personToAdd || busy()">Aggiungi</button>
      </form>
      <p>
        <button type="button" class="link" (click)="convoke()" [disabled]="busy()">Aggiungi i musicanti attivi mancanti</button>
        — utile per le attività create prima della convocazione automatica. Chi è stato rimosso a mano non viene riaggiunto.
      </p>
    </section>
  `,
  styles: `
    .summary { display: grid; gap: var(--sp-4); grid-template-columns: repeat(4, minmax(0, 1fr)); margin-bottom: var(--sp-5); }
    .summary div { background: var(--bg-surface); border: var(--border-thin) solid var(--border-subtle); border-radius: var(--radius-lg); display: grid; gap: var(--sp-1); padding: var(--sp-4); }
    .summary strong { font-family: var(--font-display); font-size: var(--text-2xl); }
    .summary span { color: var(--text-secondary); font-size: var(--text-sm); }
    .present { color: var(--color-success); }
    .absent, .error { color: var(--color-danger); }
    .toolbar { align-items: center; display: flex; flex-wrap: wrap; gap: var(--sp-3); justify-content: space-between; margin-bottom: var(--sp-4); }
    .group { align-items: center; display: flex; gap: var(--sp-2); }
    .unsaved { color: var(--color-warn); font-size: var(--text-sm); }
    .message { margin: 0 0 var(--sp-4); }
    table { width: 100%; }
    th, td { border-bottom: var(--border-thin) solid var(--border-subtle); padding: var(--sp-3); text-align: left; }
    .source { color: var(--text-secondary); font-size: var(--text-sm); }
    .segmented { display: inline-flex; }
    .segmented button { background: var(--bg-surface); border: var(--border-thin) solid var(--border-default); color: var(--text-secondary); cursor: pointer; font: inherit; font-size: var(--text-sm); padding: var(--sp-1) var(--sp-3); }
    .segmented button:first-child { border-radius: var(--radius-full) 0 0 var(--radius-full); }
    .segmented button:last-child { border-left: 0; border-radius: 0 var(--radius-full) var(--radius-full) 0; }
    .segmented .is-present.on { background: var(--color-success-soft); border-color: var(--color-success); color: var(--color-success); }
    .segmented .is-absent.on { background: var(--color-danger-soft); border-color: var(--color-danger); color: var(--color-danger); }
    .remove { text-align: right; width: 40px; }
    .remove button { background: none; border: 0; color: var(--text-tertiary); cursor: pointer; font-size: var(--text-xl); }
    .remove button:hover { color: var(--color-danger); }
    .empty { color: var(--text-secondary); text-align: center; }
    .add { margin-top: var(--sp-6); padding: var(--sp-5); }
    .add h2 { font-size: var(--text-lg); margin: 0 0 var(--sp-3); }
    .add form { display: flex; gap: var(--sp-2); max-width: 560px; }
    .add select { flex: 1; min-height: 38px; min-width: 0; }
    .add p { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-3) 0 0; }
    .link { background: none; border: 0; color: var(--color-accent-hover); cursor: pointer; font: inherit; padding: 0; text-decoration: underline; }
    .visually-hidden { clip: rect(0, 0, 0, 0); height: 1px; margin: -1px; overflow: hidden; padding: 0; position: absolute; white-space: nowrap; width: 1px; }
    @media (max-width: 800px) { .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); } .table-shell { overflow-x: auto; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityAttendanceComponent {
  private readonly api = inject(ActivitiesService);
  protected readonly id = Number(inject(ActivatedRoute).snapshot.paramMap.get('activityId'));

  protected readonly activity = signal<Activity | null>(null);
  protected readonly rows = signal<Participant[]>([]);
  /** Attendance edited but not yet saved, by person. */
  private readonly changes = signal<ReadonlyMap<number, Attendance | null>>(new Map());
  protected readonly busy = signal(false);
  protected readonly message = signal('');
  protected readonly failed = signal(false);
  protected personToAdd: number | null = null;

  private readonly people = toSignal(inject(PeopleService).listPeople('').pipe(map((page) => page.items), catchError(() => of<PersonListItem[]>([]))), { initialValue: [] });
  protected readonly addable = computed(() => {
    const present = new Set(this.rows().map((row) => row.person_id));
    return this.people().filter((p) => !p.archived_at && !present.has(p.id));
  });
  protected readonly dirty = computed(() => this.changes().size > 0);
  protected readonly subtitle = computed(() => {
    const a = this.activity();
    if (!a) return '';
    const when = new Intl.DateTimeFormat('it-IT', { dateStyle: 'full', timeStyle: 'short' }).format(new Date(a.starts_at));
    return `${TYPE_LABELS[a.type]} · ${when}${a.location ? ' · ' + a.location : ''}`;
  });

  constructor() {
    this.api.get(this.id).subscribe({ next: (a) => this.activity.set(a), error: (err: unknown) => this.fail(err, 'Attività non trovata.') });
    this.api.participants(this.id).subscribe({ next: (rows) => this.rows.set(rows), error: (err: unknown) => this.fail(err, 'Impossibile caricare i partecipanti.') });
  }

  protected attendanceOf(row: Participant): Attendance | null {
    const changes = this.changes();
    return changes.has(row.person_id) ? (changes.get(row.person_id) ?? null) : row.attendance;
  }

  protected count(value: Attendance | null): number {
    return this.rows().filter((row) => this.attendanceOf(row) === value).length;
  }

  /** Clicking the active value again clears it back to "not recorded". */
  protected toggle(row: Participant, value: Attendance): void {
    this.setAttendance(row, this.attendanceOf(row) === value ? null : value);
  }

  protected markAll(value: Attendance | null): void {
    for (const row of this.rows()) this.setAttendance(row, value);
  }

  protected save(): void {
    const rows = [...this.changes()].map(([person_id, attendance]) => ({ person_id, attendance }));
    this.run(this.api.saveAttendance(this.id, rows), 'Presenze salvate.', 'Salvataggio delle presenze non riuscito.');
  }

  protected add(): void {
    const personId = this.personToAdd;
    if (!personId) return;
    this.busy.set(true);
    this.api.addParticipant(this.id, personId).subscribe({
      next: (participant) => {
        this.busy.set(false);
        this.personToAdd = null;
        this.rows.update((rows) => [...rows, participant].sort((a, b) => this.sortKey(a).localeCompare(this.sortKey(b), 'it')));
        this.notify(`${participant.person_name} aggiunto ai convocati.`);
      },
      error: (err: unknown) => this.fail(err, 'Aggiunta non riuscita.'),
    });
  }

  protected remove(row: Participant): void {
    if (!window.confirm(`Rimuovere ${row.person_name} dai convocati?`)) return;
    this.busy.set(true);
    this.api.removeParticipant(this.id, row.person_id).subscribe({
      next: () => {
        this.busy.set(false);
        this.rows.update((rows) => rows.filter((r) => r.person_id !== row.person_id));
        this.changes.update((changes) => { const next = new Map(changes); next.delete(row.person_id); return next; });
        this.notify(`${row.person_name} rimosso dai convocati.`);
      },
      error: (err: unknown) => this.fail(err, 'Rimozione non riuscita.'),
    });
  }

  protected convoke(): void {
    const before = this.rows().length;
    this.busy.set(true);
    this.api.convokeMusicians(this.id).subscribe({
      next: (rows) => {
        this.busy.set(false);
        this.rows.set(rows);
        const added = rows.length - before;
        this.notify(added ? `${added} musicanti aggiunti.` : 'Tutti i musicanti attivi sono già convocati.');
      },
      error: (err: unknown) => this.fail(err, 'Aggiornamento dei convocati non riuscito.'),
    });
  }

  private setAttendance(row: Participant, value: Attendance | null): void {
    this.changes.update((changes) => {
      const next = new Map(changes);
      if (value === row.attendance) next.delete(row.person_id);
      else next.set(row.person_id, value);
      return next;
    });
  }

  private run(request: ReturnType<ActivitiesService['saveAttendance']>, success: string, failure: string): void {
    this.busy.set(true);
    request.subscribe({
      next: (rows) => {
        this.busy.set(false);
        this.rows.set(rows);
        this.changes.set(new Map());
        this.notify(success);
      },
      error: (err: unknown) => this.fail(err, failure),
    });
  }

  private sortKey(row: Participant): string {
    const person = this.people().find((p) => p.id === row.person_id);
    return person ? `${person.last_name} ${person.first_name}` : row.person_name;
  }

  private notify(text: string): void {
    this.failed.set(false);
    this.message.set(text);
  }

  private fail(err: unknown, fallback: string): void {
    this.busy.set(false);
    this.failed.set(true);
    this.message.set(apiErrorMessage(err, fallback));
  }
}
