import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { ApiError } from '../../core/api/api.types';
import { PeopleService } from './people.service';

@Component({
  selector: 'arsis-person-create',
  imports: [FormsModule, RouterLink],
  template: `
    <a class="back-link" routerLink="/people">← Tutte le persone</a>
    <article class="card form-card">
      <p class="section-kicker">Persona</p><h1>Nuova persona</h1>
      <form (ngSubmit)="save()">
        <label>Nome <input name="firstName" [(ngModel)]="firstName" required /></label>
        <label>Cognome <input name="lastName" [(ngModel)]="lastName" required /></label>
        <label>Email <input name="email" type="email" [(ngModel)]="email" /></label>
        <label>Telefono <input name="phone" type="tel" [(ngModel)]="phone" /></label>
        <label class="wide">Note <textarea name="notes" [(ngModel)]="notes" rows="4"></textarea></label>
        @if (error()) { <p class="error" role="alert">{{ error() }}</p> }
        <div class="actions"><a class="button button--secondary" routerLink="/people">Annulla</a><button class="button button--primary" [disabled]="saving()">{{ saving() ? 'Salvataggio…' : 'Crea persona' }}</button></div>
      </form>
    </article>
  `,
  styles: `
    :host { display: block; margin: 0 auto; max-width: 760px; }
    .back-link { color: var(--text-secondary); display: inline-block; margin-bottom: var(--sp-5); text-decoration: none; }
    .form-card { padding: var(--sp-8); } h1 { margin-top: 0; }
    form { display: grid; gap: var(--sp-5); grid-template-columns: 1fr 1fr; }
    label { display: grid; font-weight: var(--weight-medium); gap: var(--sp-2); } .wide, .actions, .error { grid-column: 1 / -1; }
    input, textarea { border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); padding: var(--sp-3); }
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
    }).subscribe({
      next: (person) => void this.router.navigate(['/people', person.id]),
      error: (response: { error?: ApiError }) => {
        this.error.set(response.error?.error.message ?? 'Creazione non riuscita.');
        this.saving.set(false);
      },
    });
  }
}
