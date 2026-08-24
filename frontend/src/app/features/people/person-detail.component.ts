import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import peopleData from '../../../assets/mock/people.json';
import { ConfigurationStore } from '../../core/config/configuration.store';
import { DetailCardComponent } from '../../shared/ui/detail-card.component';

@Component({
  selector: 'arsis-person-detail',
  imports: [DetailCardComponent, FormsModule, RouterLink],
  template: `
    <arsis-detail-card
      backLink="/people"
      backLabel="Tutte le persone"
      eyebrow="Persona"
      [title]="draft.name"
      [subtitle]="draft.roles.join(' · ')"
      [editing]="editing()"
      (editRequested)="toggleEditing()"
    >
      <span detail-visual class="avatar avatar--large {{ draft.avatar }}">{{ draft.initials }}</span>

      <div class="detail-sections">
        <section>
          <header><div><p class="section-kicker">Anagrafica</p><h2>Dati personali</h2></div><span class="status-badge status-badge--success">{{ draft.status }}</span></header>
          <div class="field-grid">
            <label><span>Nome e cognome</span>@if (editing()) { <input [(ngModel)]="draft.name" /> } @else { <strong>{{ draft.name }}</strong> }</label>
            <label><span>Stato</span>@if (editing()) { <select [(ngModel)]="draft.status"><option>Attiva</option><option>Archiviata</option></select> } @else { <strong>{{ draft.status }}</strong> }</label>
            <label class="field-grid__wide"><span>Ruoli</span>@if (editing()) { <div class="role-selector">@for (role of availableRoles(); track role.id) { <button type="button" [class.is-selected]="hasRole(role.label)" [attr.aria-pressed]="hasRole(role.label)" (click)="toggleRole(role.label)"><i></i>{{ role.label }}</button> }</div> } @else { <div class="tag-list">@for (role of draft.roles; track role) { <em>{{ role }}</em> }</div> }</label>
            <label><span>Ultima modifica</span><strong>{{ draft.updated }}</strong></label>
            <label><span>Anagrafica di riferimento</span>
              @if (editing()) {
                <select [(ngModel)]="draft.referencePersonId"><option [ngValue]="null">Nessun referente</option>@for (person of referenceCandidates; track person.id) { <option [value]="person.id">{{ person.name }}</option> }</select>
              } @else if (referencePerson(); as reference) {
                <a class="reference-person" [routerLink]="['/people', reference.id]"><span class="avatar {{ reference.avatar }}">{{ reference.initials }}</span><span><strong>{{ reference.name }}</strong><small>{{ reference.roles.join(' · ') }}</small></span></a>
              } @else { <strong class="empty-inline">Nessun referente collegato</strong> }
            </label>
          </div>
        </section>

        <section>
          <header><div><p class="section-kicker">Recapiti</p><h2>Contatti</h2></div></header>
          <div class="field-grid">
            <label><span>Email</span>@if (editing()) { <input type="email" [(ngModel)]="draft.email" /> } @else { <a href="mailto:{{ draft.email }}">{{ draft.email }}</a> }</label>
            <label><span>Telefono</span>@if (editing()) { <input type="tel" [(ngModel)]="draft.phone" /> } @else { <a href="tel:{{ draft.phone }}">{{ draft.phone }}</a> }</label>
          </div>
        </section>

        <section>
          <header><div><p class="section-kicker">Informazioni interne</p><h2>Note</h2></div></header>
          @if (editing()) { <textarea [(ngModel)]="notes" rows="4" placeholder="Aggiungi una nota sulla persona…"></textarea> }
          @else { <p class="empty-value">{{ notes || 'Nessuna nota inserita.' }}</p> }
        </section>
      </div>
    </arsis-detail-card>
  `,
  styleUrl: '../../shared/ui/detail-fields.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonDetailComponent {
  private readonly personId = inject(ActivatedRoute).snapshot.paramMap.get('personId');
  private readonly configuration = inject(ConfigurationStore);
  private readonly source = peopleData.people.find((person) => person.id === this.personId) ?? peopleData.people[0];

  protected readonly editing = signal(false);
  protected draft = { ...this.source, roles: [...this.source.roles] };
  protected readonly availableRoles = computed(() => this.configuration.roles().filter((role) => role.active));
  protected readonly referenceCandidates = peopleData.people.filter((person) => person.id !== this.personId);
  protected notes = '';

  protected toggleEditing(): void {
    this.editing.update((value) => !value);
  }

  protected hasRole(role: string): boolean {
    return this.draft.roles.includes(role);
  }

  protected toggleRole(role: string): void {
    this.draft.roles = this.hasRole(role)
      ? this.draft.roles.filter((selectedRole) => selectedRole !== role)
      : [...this.draft.roles, role];
  }

  protected referencePerson() {
    return peopleData.people.find((person) => person.id === this.draft.referencePersonId);
  }
}
