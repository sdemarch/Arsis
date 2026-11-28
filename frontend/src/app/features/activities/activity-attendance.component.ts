import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { apiErrorMessage } from '../../core/api/api-error';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { placeLabel } from '../settings/places.service';
import { ActivityRefundRules, SettingsService } from '../settings/settings.service';
import { ActivitiesService, Activity, Attendance, AttendanceWrite, Participant } from './activities.service';

/** Unsaved edits of one register row. */
interface RowDraft {
  readonly attendance: Attendance | null;
  readonly is_driver: boolean;
  readonly passenger_count: number;
}

const TYPE_LABELS: Record<Activity['type'], string> = { rehearsal: 'Prova', concert: 'Concerto', event: 'Processione' };

/** Attendance register of an activity: every active person can be marked present (§9.5). */
@Component({
  selector: 'arsis-activity-attendance',
  imports: [BackLinkComponent, FormsModule, PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Presenze" [title]="activity()?.title ?? 'Attività'" [description]="subtitle()">
      <arsis-back-link class="back-link--compact" [link]="['/activities', id]" label="Scheda attività" />
    </arsis-page-header>

    <section class="summary">
      <div><strong>{{ rows().length }}</strong><span>Persone attive</span></div>
      <div><strong class="present">{{ count('present') }}</strong><span>Presenti</span></div>
      <div><strong class="absent">{{ count('absent') }}</strong><span>Assenti</span></div>
      <div><strong>{{ count(null) }}</strong><span>Da registrare</span></div>
    </section>

    @if (mileageEnabled()) {
      <p class="mileage-note">
        Rimborso chilometrico attivo · {{ placeText() }}. Indica chi guida e quanti passeggeri trasporta:
        {{ drivers() }} autisti, {{ passengers() }} passeggeri su {{ count('present') - drivers() }} presenti senza auto.
      </p>
    } @else if (activity() && !activity()!.place && mileageType()) {
      <p class="mileage-note">Collega un luogo all’attività per calcolare il rimborso chilometrico agli autisti.</p>
    }
    @if (tooManyPassengers()) { <p class="message error" role="alert">I passeggeri indicati superano i presenti che non guidano.</p> }

    <div class="toolbar">
      <div class="group">
        <input class="search" type="search" placeholder="Cerca una persona…" aria-label="Cerca una persona" [ngModel]="query()" (ngModelChange)="query.set($event)" />
        <label class="only-recorded"><input type="checkbox" [ngModel]="onlyRecorded()" (ngModelChange)="onlyRecorded.set($event)" />Solo registrate</label>
        <button type="button" class="button button--secondary" (click)="markAll('present')" [disabled]="!visibleRows().length">{{ filtered() ? 'Visibili presenti' : 'Tutti presenti' }}</button>
        <button type="button" class="button button--secondary" (click)="markAll(null)" [disabled]="!visibleRows().length">Azzera</button>
      </div>
      <div class="group">
        @if (dirty()) { <span class="unsaved">Modifiche non salvate</span> }
        <button type="button" class="button button--primary" (click)="save()" [disabled]="!dirty() || busy() || tooManyPassengers()">Salva presenze</button>
      </div>
    </div>

    @if (message()) { <p class="message" [class.error]="failed()" role="status">{{ message() }}</p> }

    <div class="table-shell">
      <table>
        <thead><tr><th>Persona</th><th>Presenza</th>@if (mileageEnabled()) { <th>Autista</th><th>Passeggeri</th> }<th class="amount">Rimborso</th></tr></thead>
        <tbody>
          @for (row of visibleRows(); track row.person_id) {
            <tr>
              <td><a [routerLink]="['/people', row.person_id]">{{ row.person_name }}</a></td>
              <td>
                <div class="segmented" role="group" [attr.aria-label]="'Presenza di ' + row.person_name">
                  <button type="button" class="is-present" [class.on]="attendanceOf(row) === 'present'" [attr.aria-pressed]="attendanceOf(row) === 'present'" (click)="toggle(row, 'present')">Presente</button>
                  <button type="button" class="is-absent" [class.on]="attendanceOf(row) === 'absent'" [attr.aria-pressed]="attendanceOf(row) === 'absent'" (click)="toggle(row, 'absent')">Assente</button>
                </div>
              </td>
              @if (mileageEnabled()) {
                <td>
                  @if (draftOf(row).attendance === 'present') {
                    <label class="driver"><input type="checkbox" [checked]="draftOf(row).is_driver" (change)="setDriver(row, $any($event.target).checked)" [attr.aria-label]="row.person_name + ' guida'" />Guida</label>
                  }
                </td>
                <td>
                  @if (draftOf(row).attendance === 'present' && draftOf(row).is_driver) {
                    <input class="passengers" type="number" min="0" step="1" [value]="draftOf(row).passenger_count" (input)="setPassengers(row, $any($event.target).value)" [attr.aria-label]="'Passeggeri di ' + row.person_name" />
                  }
                </td>
              }
              <td class="amount">
                @if (changes().has(row.person_id)) { <span class="pending" title="Calcolato al salvataggio">da salvare</span> }
                @else if (row.attendance === 'present') { <span [title]="refundDetail(row)">{{ currency(row.refund_total) }}</span> }
              </td>
            </tr>
          } @empty {
            <tr><td [attr.colspan]="mileageEnabled() ? 5 : 3" class="empty">{{ rows().length ? 'Nessuna persona corrisponde alla ricerca.' : 'Nessuna persona attiva in anagrafica.' }}</td></tr>
          }
        </tbody>
      </table>
    </div>

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
    .search { min-height: 38px; min-width: 220px; padding: 0 var(--sp-3); }
    .only-recorded { align-items: center; color: var(--text-secondary); display: inline-flex; font-size: var(--text-sm); gap: var(--sp-2); white-space: nowrap; }
    .segmented { display: inline-flex; }
    .segmented button { background: var(--bg-surface); border: var(--border-thin) solid var(--border-default); color: var(--text-secondary); cursor: pointer; font: inherit; font-size: var(--text-sm); padding: var(--sp-1) var(--sp-3); }
    .segmented button:first-child { border-radius: var(--radius-full) 0 0 var(--radius-full); }
    .segmented button:last-child { border-left: 0; border-radius: 0 var(--radius-full) var(--radius-full) 0; }
    .segmented .is-present.on { background: var(--color-success-soft); border-color: var(--color-success); color: var(--color-success); }
    .segmented .is-absent.on { background: var(--color-danger-soft); border-color: var(--color-danger); color: var(--color-danger); }
    .mileage-note { color: var(--text-secondary); font-size: var(--text-sm); margin: 0 0 var(--sp-4); }
    .driver { align-items: center; display: inline-flex; font-size: var(--text-sm); gap: var(--sp-2); }
    .passengers { min-height: 32px; padding: 0 var(--sp-2); width: 72px; }
    .amount { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
    .pending { color: var(--color-warn); font-size: var(--text-sm); }
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
  /** Register rows edited but not yet saved, by person. */
  protected readonly changes = signal<ReadonlyMap<number, RowDraft>>(new Map());
  private readonly rules = signal<ActivityRefundRules | null>(null);
  protected readonly mileageType = computed(() => {
    const a = this.activity();
    const rules = this.rules();
    return !!a && !!rules && rules.mileage.enabled_types.includes(a.type);
  });
  protected readonly mileageEnabled = computed(() => this.mileageType() && !!this.activity()?.place);
  protected readonly placeText = computed(() => {
    const place = this.activity()?.place;
    return place ? placeLabel(place) : '';
  });
  protected readonly drivers = computed(() => this.rows().filter((row) => this.drives(this.draftOf(row))).length);
  protected readonly passengers = computed(() =>
    this.rows().reduce((sum, row) => {
      const draft = this.draftOf(row);
      return sum + (this.drives(draft) ? draft.passenger_count : 0);
    }, 0),
  );
  protected readonly tooManyPassengers = computed(() => this.mileageEnabled() && this.passengers() > this.count('present') - this.drivers());
  protected readonly busy = signal(false);
  protected readonly message = signal('');
  protected readonly failed = signal(false);
  protected readonly query = signal('');
  protected readonly onlyRecorded = signal(false);
  protected readonly filtered = computed(() => !!this.query().trim() || this.onlyRecorded());
  /** Rows matching the search; "Solo registrate" keeps those with attendance or unsaved edits. */
  protected readonly visibleRows = computed(() => {
    const query = this.query().trim().toLocaleLowerCase('it');
    const onlyRecorded = this.onlyRecorded();
    return this.rows().filter(
      (row) =>
        (!query || row.person_name.toLocaleLowerCase('it').includes(query)) &&
        (!onlyRecorded || this.attendanceOf(row) !== null || this.changes().has(row.person_id)),
    );
  });
  protected readonly dirty = computed(() => this.changes().size > 0);
  protected readonly subtitle = computed(() => {
    const a = this.activity();
    if (!a) return '';
    const when = new Intl.DateTimeFormat('it-IT', { dateStyle: 'full' }).format(new Date(a.starts_at));
    return `${TYPE_LABELS[a.type]} · ${when}${a.location ? ' · ' + a.location : ''}`;
  });

  constructor() {
    this.api.get(this.id).subscribe({ next: (a) => this.activity.set(a), error: (err: unknown) => this.fail(err, 'Attività non trovata.') });
    inject(SettingsService).activityRefundRules().subscribe({ next: (rules) => this.rules.set(rules) });
    this.api.participants(this.id).subscribe({ next: (rows) => this.rows.set(rows), error: (err: unknown) => this.fail(err, 'Impossibile caricare le persone.') });
  }

  protected draftOf(row: Participant): RowDraft {
    return this.changes().get(row.person_id) ?? this.savedDraft(row);
  }

  protected attendanceOf(row: Participant): Attendance | null {
    return this.draftOf(row).attendance;
  }

  protected setDriver(row: Participant, driver: boolean): void {
    const draft = this.draftOf(row);
    this.setDraft(row, { ...draft, is_driver: driver, passenger_count: driver ? draft.passenger_count : 0 });
  }

  protected setPassengers(row: Participant, value: string): void {
    const count = Math.max(0, Math.trunc(Number(value) || 0));
    this.setDraft(row, { ...this.draftOf(row), passenger_count: count });
  }

  protected currency(value: string): string {
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(Number(value));
  }

  protected refundDetail(row: Participant): string {
    const parts = [`Presenza ${this.currency(row.refund_flat_amount)}`];
    if (row.refund_distance_km !== null) {
      parts.push(`${row.refund_distance_km} km (+${row.refund_bonus_pct ?? 0}%) ${this.currency(row.refund_mileage_amount)}`);
      parts.push(`pedaggio ${this.currency(row.refund_highway_amount)}`);
    }
    return parts.join(' · ');
  }

  protected count(value: Attendance | null): number {
    return this.rows().filter((row) => this.attendanceOf(row) === value).length;
  }

  /** Clicking the active value again clears it back to "not recorded". */
  protected toggle(row: Participant, value: Attendance): void {
    this.setAttendance(row, this.attendanceOf(row) === value ? null : value);
  }

  /** Applies to the rows currently shown, so a search narrows "Tutti presenti". */
  protected markAll(value: Attendance | null): void {
    for (const row of this.visibleRows()) this.setAttendance(row, value);
  }

  protected save(): void {
    const rows: AttendanceWrite[] = [...this.changes()].map(([person_id, draft]) =>
      draft.attendance === 'present'
        ? { person_id, attendance: draft.attendance, is_driver: draft.is_driver, passenger_count: draft.is_driver ? draft.passenger_count : null }
        : { person_id, attendance: draft.attendance },
    );
    this.run(this.api.saveAttendance(this.id, rows), 'Presenze salvate.', 'Salvataggio delle presenze non riuscito.');
  }

  private setAttendance(row: Participant, value: Attendance | null): void {
    // Only someone present can drive.
    this.setDraft(row, value === 'present' ? { ...this.draftOf(row), attendance: value } : { attendance: value, is_driver: false, passenger_count: 0 });
  }

  private drives(draft: RowDraft): boolean {
    return draft.attendance === 'present' && draft.is_driver;
  }

  private savedDraft(row: Participant): RowDraft {
    return { attendance: row.attendance, is_driver: row.is_driver, passenger_count: row.passenger_count ?? 0 };
  }

  private setDraft(row: Participant, draft: RowDraft): void {
    const saved = this.savedDraft(row);
    const unchanged =
      draft.attendance === saved.attendance &&
      draft.is_driver === saved.is_driver &&
      (!draft.is_driver || draft.passenger_count === saved.passenger_count);
    this.changes.update((changes) => {
      const next = new Map(changes);
      if (unchanged) next.delete(row.person_id);
      else next.set(row.person_id, draft);
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
