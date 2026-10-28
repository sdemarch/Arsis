import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { ActivatedRoute } from '@angular/router';

import { ApiError } from '../../core/api/api.types';
import { DetailCardComponent } from '../../shared/ui/detail-card.component';
import { PeopleService, PersonDetail, PersonRole, PersonUpdate } from './people.service';

const ROLE_OPTIONS = [
  { value: 'member', label: 'Socio' },
  { value: 'musician', label: 'Musicante' },
  { value: 'student', label: 'Allievo' },
  { value: 'teacher', label: 'Insegnante' },
] as const;

@Component({
  selector: 'arsis-person-detail',
  imports: [DetailCardComponent, FormsModule],
  template: `
    @if (person(); as item) {
      <arsis-detail-card
        backLink="/people"
        backLabel="Tutte le persone"
        eyebrow="Persona"
        [title]="item.first_name + ' ' + item.last_name"
        [subtitle]="roleNames().join(' · ')"
        [editing]="editing()"
        [editable]="!item.archived_at"
        (editRequested)="editing() ? save() : beginEditing()"
      >
        <span detail-visual class="avatar avatar--large av-blue">{{ initials() }}</span>
        @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
        <div class="detail-sections">
          <section>
            <header>
              <div><p class="section-kicker">Anagrafica</p><h2>Dati personali</h2></div>
              <span class="status-badge" [class.status-badge--success]="!item.archived_at">{{ item.archived_at ? 'Archiviata' : 'Attiva' }}</span>
            </header>
            <div class="field-grid">
              <label><span>Nome</span>@if (editing()) { <input name="firstName" [(ngModel)]="draft.first_name" required /> } @else { <strong>{{ item.first_name }}</strong> }</label>
              <label><span>Cognome</span>@if (editing()) { <input name="lastName" [(ngModel)]="draft.last_name" required /> } @else { <strong>{{ item.last_name }}</strong> }</label>
              <label><span>Data di nascita</span>@if (editing()) { <input name="birthDate" type="date" [(ngModel)]="draft.birth_date" /> } @else { <strong>{{ item.birth_date || 'Non indicata' }}</strong> }</label>
              <label><span>Luogo di nascita</span>@if (editing()) { <input name="birthPlace" [(ngModel)]="draft.birth_place" /> } @else { <strong>{{ item.birth_place || 'Non indicato' }}</strong> }</label>
              <label><span>Codice fiscale</span>@if (editing()) { <input name="taxCode" [(ngModel)]="draft.tax_code" /> } @else { <strong>{{ item.tax_code || 'Non indicato' }}</strong> }</label>
              <label class="field-grid__wide"><span>Indirizzo</span>@if (editing()) { <input name="address" [(ngModel)]="draft.residence_address" /> } @else { <strong>{{ item.residence_address || 'Non indicato' }}</strong> }</label>
            </div>
          </section>

          <section>
            <header><div><p class="section-kicker">Ruoli</p><h2>Incarichi e appartenenze</h2></div></header>
            <div class="role-list">
              @for (role of roles(); track role.id) {
                <div><span>{{ roleLabel(role.role_type) }}</span><small>Dal {{ role.start_date }} · {{ role.status }}</small>@if (!item.archived_at) { <button type="button" class="text-button" (click)="archiveRole(role)">Rimuovi</button> }</div>
              } @empty { <p class="empty-value">Nessun ruolo assegnato.</p> }
            </div>
            @if (editing()) {
              <div class="role-add">
                <select name="newRole" [(ngModel)]="newRole"><option value="">Aggiungi un ruolo…</option>@for (role of roleOptions; track role.value) { <option [value]="role.value">{{ role.label }}</option> }</select>
                <input name="roleStart" type="date" [(ngModel)]="roleStartDate" />
                <button type="button" class="button button--secondary" [disabled]="!newRole || saving()" (click)="addRole()">Aggiungi</button>
              </div>
            }
          </section>

          <section>
            <header><div><p class="section-kicker">Recapiti</p><h2>Contatti</h2></div></header>
            <div class="field-grid">
              <label><span>Email</span>@if (editing()) { <input name="email" type="email" [(ngModel)]="draft.email" /> } @else { <strong>{{ item.email || 'Non indicata' }}</strong> }</label>
              <label><span>Telefono</span>@if (editing()) { <input name="phone" type="tel" [(ngModel)]="draft.phone" /> } @else { <strong>{{ item.phone || 'Non indicato' }}</strong> }</label>
            </div>
          </section>

          <section>
            <header><div><p class="section-kicker">Informazioni interne</p><h2>Note</h2></div></header>
            @if (editing()) { <textarea name="notes" [(ngModel)]="draft.notes" rows="4"></textarea> } @else { <p class="empty-value">{{ item.notes || 'Nessuna nota inserita.' }}</p> }
          </section>

          @if (!item.archived_at) {
            <section class="danger-zone"><header><div><p class="section-kicker">Archiviazione</p><h2>Rimuovi dalla vista attiva</h2></div></header><p>La persona resta nello storico e può essere consultata.</p><button type="button" class="button button--secondary" (click)="archivePerson()">Archivia persona</button></section>
          }
        </div>
      </arsis-detail-card>
    } @else { <p class="empty-value">Caricamento della persona…</p> }
  `,
  styles: `
    .error { color: var(--color-danger); margin: 0 0 var(--sp-4); }
    input, select, textarea { border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); font: inherit; padding: var(--sp-2); width: 100%; }
    .role-list { display: grid; gap: var(--sp-2); } .role-list > div { align-items: center; background: var(--bg-raised); border-radius: var(--radius-md); display: flex; gap: var(--sp-3); padding: var(--sp-3); }
    .role-list small { color: var(--text-secondary); flex: 1; } .text-button { background: transparent; border: 0; color: var(--color-danger); cursor: pointer; }
    .role-add { display: grid; gap: var(--sp-3); grid-template-columns: 1fr 160px auto; margin-top: var(--sp-4); } .role-add .button { white-space: nowrap; }
    .danger-zone { border: var(--border-thin) solid color-mix(in srgb, var(--color-danger) 35%, var(--border-default)); border-radius: var(--radius-md); padding: var(--sp-5); } .danger-zone p { color: var(--text-secondary); }
    @media (max-width: 640px) { .role-add { grid-template-columns: 1fr; } .role-list > div { align-items: flex-start; flex-direction: column; } }
  `,
  styleUrl: '../../shared/ui/detail-fields.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly peopleService = inject(PeopleService);
  private readonly personId = Number(this.route.snapshot.paramMap.get('personId'));
  protected readonly person = signal<PersonDetail | null>(null);
  protected readonly roles = signal<PersonRole[]>([]);
  protected readonly editing = signal(false);
  protected readonly saving = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly roleOptions = ROLE_OPTIONS;
  protected readonly roleNames = computed(() => this.roles().map((role) => this.roleLabel(role.role_type)));
  protected readonly initials = computed(() => {
    const person = this.person();
    return person ? `${person.first_name[0] ?? ''}${person.last_name[0] ?? ''}` : '';
  });
  protected draft = this.emptyDraft();
  protected newRole = '';
  protected roleStartDate = new Date().toISOString().slice(0, 10);

  constructor() { this.load(); }

  protected beginEditing(): void {
    const person = this.person();
    if (!person) return;
    this.draft = this.toDraft(person);
    this.editing.set(true);
    this.error.set(null);
  }

  protected save(): void {
    const person = this.person();
    if (!person || !this.draft.first_name.trim() || !this.draft.last_name.trim()) return;
    this.saving.set(true);
    this.error.set(null);
    const payload: PersonUpdate = {
      version: person.version,
      first_name: this.draft.first_name.trim(), last_name: this.draft.last_name.trim(),
      birth_date: this.emptyToNull(this.draft.birth_date), birth_place: this.emptyToNull(this.draft.birth_place),
      tax_code: this.emptyToNull(this.draft.tax_code), residence_address: this.emptyToNull(this.draft.residence_address),
      email: this.emptyToNull(this.draft.email), phone: this.emptyToNull(this.draft.phone), notes: this.emptyToNull(this.draft.notes),
    };
    this.peopleService.updatePerson(person.id, payload).subscribe({ next: () => { this.editing.set(false); this.finishAndReload(); }, error: (response) => this.fail(response) });
  }

  protected addRole(): void {
    const person = this.person();
    if (!person || !this.newRole) return;
    this.saving.set(true); this.error.set(null);
    this.peopleService.createRole(person.id, this.newRole, this.roleStartDate).subscribe({ next: () => { this.newRole = ''; this.finishAndReload(); }, error: (response) => this.fail(response) });
  }

  protected archiveRole(role: PersonRole): void {
    if (!window.confirm(`Rimuovere il ruolo ${this.roleLabel(role.role_type)}?`)) return;
    this.saving.set(true); this.error.set(null);
    this.peopleService.archiveRole(role.id, role.version).subscribe({ next: () => this.finishAndReload(), error: (response) => this.fail(response) });
  }

  protected archivePerson(): void {
    const person = this.person();
    if (!person || !window.confirm(`Archiviare ${person.first_name} ${person.last_name}?`)) return;
    this.saving.set(true); this.error.set(null);
    this.peopleService.archivePerson(person.id, person.version).subscribe({ next: () => this.finishAndReload(), error: (response) => this.fail(response) });
  }

  protected roleLabel(type: string): string { return ROLE_OPTIONS.find((role) => role.value === type)?.label ?? type; }

  private load(): void {
    forkJoin({ person: this.peopleService.getPerson(this.personId), roles: this.peopleService.listRoles(this.personId) }).subscribe({
      next: ({ person, roles }) => { this.person.set(person); this.roles.set(roles); this.draft = this.toDraft(person); this.saving.set(false); },
      error: (response) => this.fail(response),
    });
  }

  private finishAndReload(): void { this.load(); }
  private fail(response: { error?: ApiError }): void { this.error.set(response.error?.error.message ?? 'Operazione non riuscita.'); this.saving.set(false); }
  private emptyToNull(value: string): string | null { return value.trim() || null; }
  private emptyDraft() { return { first_name: '', last_name: '', birth_date: '', birth_place: '', tax_code: '', residence_address: '', email: '', phone: '', notes: '' }; }
  private toDraft(person: PersonDetail) { return { first_name: person.first_name, last_name: person.last_name, birth_date: person.birth_date ?? '', birth_place: person.birth_place ?? '', tax_code: person.tax_code ?? '', residence_address: person.residence_address ?? '', email: person.email ?? '', phone: person.phone ?? '', notes: person.notes ?? '' }; }
}
