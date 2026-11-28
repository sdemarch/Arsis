import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, of, switchMap, catchError } from 'rxjs';

import { apiErrorMessage } from '../../core/api/api-error';
import { toOffsetIso } from '../../core/time/local-datetime';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { Place, PlacesService, placeLabel } from '../settings/places.service';
import { ActivitiesService, Activity, Frequency, Recurrence, SeriesPreview } from './activities.service';

const WEEKDAYS = [
  { value: 1, label: 'Lun' }, { value: 2, label: 'Mar' }, { value: 3, label: 'Mer' }, { value: 4, label: 'Gio' },
  { value: 5, label: 'Ven' }, { value: 6, label: 'Sab' }, { value: 7, label: 'Dom' },
] as const;

/** ISO weekday (1 = Monday) of a `YYYY-MM-DD` date, read as a local calendar day. */
function isoWeekday(day: string): number {
  const [year, month, date] = day.split('-').map(Number);
  return ((new Date(year, month - 1, date).getDay() + 6) % 7) + 1;
}

/** Activities have a date only: each one is stored at local midnight with the browser's offset. */
const localMidnight = (day: string): string => toOffsetIso(`${day}T00:00`);

@Component({
  selector: 'arsis-activity-create',
  imports: [BackLinkComponent, FormsModule],
  template: `
    <arsis-back-link link="/activities" label="Tutte le attività" />
    <article class="card">
      <h1>Nuova attività</h1>
      <form (ngSubmit)="save()">
        <label>Titolo<input name="title" [(ngModel)]="title" required /></label>
        <label>Tipo
          <select name="type" [(ngModel)]="type"><option value="rehearsal">Prova</option><option value="concert">Concerto</option><option value="event">Processione</option></select>
        </label>
        <label>{{ repeat ? 'Prima data' : 'Data' }}<input name="startsDate" type="date" [(ngModel)]="startsDate" (ngModelChange)="dateChanged()" required /></label>
        <label>Luogo
          <select name="place" [(ngModel)]="placeId"><option [ngValue]="null">Nessun luogo</option>@for (p of places(); track p.id) {<option [ngValue]="p.id">{{ label(p) }}</option>}</select>
        </label>
        <label>Dettaglio luogo<input name="location" [(ngModel)]="location" placeholder="Es. piazza principale, palco nord" /></label>
        <label>Stato
          <select name="status" [(ngModel)]="status"><option value="planned">Pianificata</option><option value="confirmed">Confermata</option><option value="cancelled">Annullata</option></select>
        </label>

        <fieldset class="repeat">
          <label class="check"><input type="checkbox" name="repeat" [(ngModel)]="repeat" (ngModelChange)="ruleChanged()" /> Ripeti l'attività</label>
          @if (repeat) {
            <div class="rule">
              <label>Frequenza
                <select name="frequency" [(ngModel)]="frequency" (ngModelChange)="ruleChanged()"><option value="weekly">Settimanale</option><option value="monthly">Mensile</option></select>
              </label>
              <label>Ogni
                <span class="every"><input name="interval" type="number" min="1" max="12" [(ngModel)]="interval" (ngModelChange)="ruleChanged()" /> {{ frequency === 'weekly' ? (interval === 1 ? 'settimana' : 'settimane') : (interval === 1 ? 'mese' : 'mesi') }}</span>
              </label>
              <label>Fino al<input name="endsOn" type="date" [min]="startsDate" [(ngModel)]="endsOn" (ngModelChange)="ruleChanged()" required /></label>
            </div>
            @if (frequency === 'weekly') {
              <div class="weekdays" role="group" aria-label="Giorni della settimana">
                @for (day of weekdays; track day.value) {
                  <label class="chip" [class.chip--on]="selectedDays.includes(day.value)"><input type="checkbox" [checked]="selectedDays.includes(day.value)" (change)="toggleDay(day.value)" />{{ day.label }}</label>
                }
              </div>
            } @else if (startsDate) {
              <p class="hint">Ogni mese il giorno {{ dayOfMonth() }}; i mesi senza quel giorno vengono saltati.</p>
            }
            <div class="preview" aria-live="polite">
              @if (previewError()) { <p class="error">{{ previewError() }}</p> }
              @else if (preview(); as p) {
                <p><strong>{{ p.dates.length }} {{ p.dates.length === 1 ? 'attività' : 'attività' }}</strong> · {{ p.description }}</p>
                <ul>@for (day of p.dates.slice(0, 12); track day) { <li>{{ format(day) }}</li> }@if (p.dates.length > 12) { <li class="more">… e altre {{ p.dates.length - 12 }}</li> }</ul>
              } @else { <p class="hint">Indica la prima data e la data di fine per vedere le attività che verranno create.</p> }
            </div>
          }
        </fieldset>

        @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
        <button class="button button--primary" [disabled]="saving() || (repeat && !preview())">{{ repeat ? 'Crea ' + (preview()?.dates?.length ?? '') + ' attività' : 'Crea attività' }}</button>
      </form>
    </article>
  `,
  styles: `
    :host { display: block; margin: auto; max-width: 720px; }
    .card { padding: var(--sp-8); }
    form { display: grid; gap: var(--sp-4); }
    label { display: grid; gap: var(--sp-2); }
    input, select { padding: var(--sp-2); }
    input[type=date] { cursor: pointer; }
    .repeat { border: var(--border-thin) solid var(--border-subtle); border-radius: var(--radius-md); display: grid; gap: var(--sp-4); margin: 0; padding: var(--sp-4); }
    .check { align-items: center; display: flex; font-weight: var(--weight-medium); gap: var(--sp-2); }
    .rule { display: grid; gap: var(--sp-4); grid-template-columns: 1fr 1fr 1.2fr; }
    .every { align-items: center; display: flex; gap: var(--sp-2); }
    .every input { width: 64px; }
    .weekdays { display: flex; flex-wrap: wrap; gap: var(--sp-2); }
    .chip { border: var(--border-thin) solid var(--border-default); border-radius: 999px; cursor: pointer; display: inline-flex; padding: var(--sp-1) var(--sp-3); }
    .chip input { height: 1px; opacity: 0; position: absolute; width: 1px; }
    .chip:focus-within { outline: 2px solid var(--color-accent); }
    .chip--on { background: var(--color-accent-soft); border-color: var(--color-accent); color: var(--color-accent-hover); }
    .preview p { margin: 0 0 var(--sp-2); }
    .preview ul { columns: 2; color: var(--text-secondary); font-size: var(--text-sm); margin: 0; padding-left: var(--sp-5); }
    .more { list-style: none; }
    .hint { color: var(--text-secondary); font-size: var(--text-sm); margin: 0; }
    .error { color: var(--color-danger); margin: 0; }
    @media (max-width: 640px) { .rule { grid-template-columns: 1fr; } .preview ul { columns: 1; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityCreateComponent {
  private readonly service = inject(ActivitiesService);
  private readonly router = inject(Router);
  protected readonly weekdays = WEEKDAYS;
  protected readonly label = placeLabel;
  protected readonly places = signal<Place[]>([]);
  protected readonly saving = signal(false);
  protected readonly error = signal('');
  protected readonly preview = signal<SeriesPreview | null>(null);
  protected readonly previewError = signal('');

  protected title = '';
  protected type: Activity['type'] = 'rehearsal';
  protected startsDate = '';
  protected location = '';
  protected placeId: number | null = null;
  protected status: Activity['status'] = 'planned';
  protected repeat = false;
  protected frequency: Frequency = 'weekly';
  protected interval = 1;
  protected endsOn = '';
  protected selectedDays: number[] = [];

  private readonly ruleChanges = new Subject<void>();

  constructor() {
    inject(PlacesService).list().subscribe({ next: (p) => this.places.set(p) });
    // The backend owns the rule: every change asks it for the dates (debounced).
    this.ruleChanges
      .pipe(
        debounceTime(250),
        switchMap(() => {
          const recurrence = this.recurrence();
          if (!this.repeat || !this.startsDate || !recurrence) return of(null);
          return this.service.previewSeries(this.startsDate, recurrence).pipe(
            catchError((err: unknown) => { this.previewError.set(apiErrorMessage(err, 'Regola non valida.')); return of(null); }),
          );
        }),
        takeUntilDestroyed(inject(DestroyRef)),
      )
      .subscribe((result) => { if (result) this.previewError.set(''); this.preview.set(result); });
  }

  protected dateChanged(): void {
    // Weekly series start on the chosen date's weekday unless days were picked already.
    if (this.startsDate && !this.selectedDays.length) this.selectedDays = [isoWeekday(this.startsDate)];
    this.ruleChanged();
  }

  protected ruleChanged(): void {
    this.preview.set(null);
    this.ruleChanges.next();
  }

  protected toggleDay(day: number): void {
    this.selectedDays = this.selectedDays.includes(day) ? this.selectedDays.filter((d) => d !== day) : [...this.selectedDays, day].sort();
    this.ruleChanged();
  }

  protected dayOfMonth(): number {
    return Number(this.startsDate.slice(8, 10));
  }

  protected format(day: string): string {
    const [year, month, date] = day.split('-').map(Number);
    return new Intl.DateTimeFormat('it-IT', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(year, month - 1, date));
  }

  protected save(): void {
    if (!this.startsDate || !this.title.trim()) return;
    const base = { title: this.title, type: this.type, location: this.location || null, place_id: this.placeId, status: this.status };
    this.error.set('');
    if (!this.repeat) {
      this.saving.set(true);
      this.service.create({ ...base, starts_at: localMidnight(this.startsDate) }).subscribe({
        next: (a) => void this.router.navigate(['/activities', a.id]),
        error: (err: unknown) => { this.saving.set(false); this.error.set(apiErrorMessage(err, 'Creazione non riuscita.')); },
      });
      return;
    }
    const preview = this.preview();
    const recurrence = this.recurrence();
    if (!preview || !recurrence) return;
    this.saving.set(true);
    this.service.createSeries({ ...base, starts_on: this.startsDate, recurrence, occurrences: preview.dates.map(localMidnight) }).subscribe({
      next: (created) => void this.router.navigate(['/activities', created[0].id]),
      error: (err: unknown) => { this.saving.set(false); this.error.set(apiErrorMessage(err, 'Creazione della serie non riuscita.')); },
    });
  }

  private recurrence(): Recurrence | null {
    if (!this.endsOn) return null;
    return {
      frequency: this.frequency,
      interval: Math.min(12, Math.max(1, Math.round(Number(this.interval) || 1))),
      weekdays: this.frequency === 'weekly' ? this.selectedDays : null,
      ends_on: this.endsOn,
    };
  }
}
