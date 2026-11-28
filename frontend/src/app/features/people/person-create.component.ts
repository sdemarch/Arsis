import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { ApiError } from '../../core/api/api.types';
import { RoleTypesService } from '../../core/roles/role-types.service';
import { PeopleService } from './people.service';
import { BackLinkComponent } from '../../shared/ui/back-link.component';

@Component({
  selector: 'arsis-person-create',
  imports: [BackLinkComponent, FormsModule, RouterLink],
  template: `
    <arsis-back-link link="/people" label="Tutte le persone" />
    <article class="card form-card">
      <p class="section-kicker">Persona</p><h1>Nuova persona</h1>
      <form (ngSubmit)="save()">
        <label>Nome <input name="firstName" [(ngModel)]="firstName" required /></label>
        <label>Cognome <input name="lastName" [(ngModel)]="lastName" required /></label>
        <label>Email <input name="email" type="email" [(ngModel)]="email" /></label>
        <label>Telefono <input name="phone" type="tel" [(ngModel)]="phone" /></label>
        <fieldset class="wide roles"><legend>Ruoli</legend><p>Seleziona uno o più ruoli da assegnare subito.</p>@for (role of roleOptions(); track role.value) { <label><input type="checkbox" [checked]="roles.includes(role.value)" (change)="toggleRole(role.value, $any($event.target).checked)" /> {{ role.label }}</label> }</fieldset>
        <label class="wide">Note <textarea name="notes" [(ngModel)]="notes" rows="4"></textarea></label>
        @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
        <div class="actions"><a class="button button--secondary" routerLink="/people">Annulla</a><button class="button button--primary" [disabled]="saving()">{{ saving() ? 'Salvataggio…' : 'Crea persona' }}</button></div>
      </form>
    </article>
  `,
  styles: `
    :host { display: block; margin: 0 auto; max-width: 760px; }
    .form-card { padding: var(--sp-8); } h1 { margin-top: 0; }
    form { display: grid; gap: var(--sp-5); grid-template-columns: 1fr 1fr; }
    label { display: grid; font-weight: var(--weight-medium); gap: var(--sp-2); } .wide, .actions, .error { grid-column: 1 / -1; }
    input, textarea { border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); padding: var(--sp-3); }
    .roles { border: 0; margin: 0; padding: 0; } .roles p { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-1) 0 var(--sp-3); } .roles label { display: inline-flex; margin: 0 var(--sp-4) var(--sp-2) 0; } .roles input { accent-color: var(--color-accent); padding: 0; }
    .actions { display: flex; gap: var(--sp-3); justify-content: flex-end; } .error { color: var(--color-danger); margin: 0; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonCreateComponent {
  private readonly peopleService = inject(PeopleService);
  private readonly router = inject(Router);
  protected firstName = '';
  protected lastName = '';
  protected email = '';
  protected phone = '';
  protected notes = '';
  protected roles: string[] = [];
  private readonly roleTypes = inject(RoleTypesService);
  protected readonly roleOptions = computed(() => this.roleTypes.active().map((role) => ({ value: role.code, label: role.name })));
  protected readonly saving = signal(false);
  protected readonly error = signal<string | null>(null);

  protected save(): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.error.set(null);
    this.peopleService.createPerson({
      first_name: this.firstName,
      last_name: this.lastName,
      email: this.email || null,
      phone: this.phone || null,
      notes: this.notes || null,
      roles: this.roles,
    }).subscribe({
      next: (person) => void this.router.navigate(['/people', person.id]),
      error: (response: { error?: ApiError }) => {
        this.error.set(response.error?.error.message ?? 'Creazione non riuscita.');
        this.saving.set(false);
      },
    });
  }

  protected toggleRole(role: string, selected: boolean): void {
    this.roles = selected ? [...this.roles, role] : this.roles.filter((item) => item !== role);
  }
}
