import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { apiErrorMessage } from '../../core/api/api-error';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { ActivityRefundRules, RefundActivityType, SettingsService } from './settings.service';

const TYPES: readonly { readonly value: RefundActivityType; readonly label: string }[] = [
  { value: 'rehearsal', label: 'Prove' },
  { value: 'concert', label: 'Concerti' },
  { value: 'event', label: 'Eventi' },
];

@Component({
  selector: 'arsis-activity-refund-rules-page',
  imports: [BackLinkComponent, FormsModule, PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Configurazioni" title="Rimborsi attività" description="Definisci l’importo riconosciuto per ogni presenza registrata e il rimborso chilometrico per gli autisti.">
      <arsis-back-link class="back-link--compact" link="/settings" label="Configurazioni" />
    </arsis-page-header>
    <form class="card" (ngSubmit)="save()">
      <p>Il rimborso è calcolato per ciascun partecipante segnato come presente. Le presenze assenti o non registrate non maturano alcun importo.</p>
      <label><span>Prova</span><input name="rehearsal" [(ngModel)]="rehearsal" type="number" min="0" step="0.01" required /><small>€ per presenza</small></label>
      <label><span>Concerto</span><input name="concert" [(ngModel)]="concert" type="number" min="0" step="0.01" required /><small>€ per presenza</small></label>
      <label><span>Evento</span><input name="event" [(ngModel)]="event" type="number" min="0" step="0.01" required /><small>€ per presenza</small></label>

      <fieldset>
        <legend>Rimborso chilometrico</legend>
        <p>Riconosciuto agli autisti presenti, in aggiunta all’importo per presenza, quando l’attività ha un luogo. Si calcola sui km di andata e ritorno del luogo, con una maggiorazione per ogni passeggero, più il pedaggio autostradale del luogo.</p>
        <div class="types" role="group" aria-label="Tipi di attività con rimborso chilometrico">
          @for (type of types; track type.value) {
            <label class="check"><input type="checkbox" [name]="'mileage-' + type.value" [ngModel]="enabledTypes.has(type.value)" (ngModelChange)="toggleType(type.value, $event)" />{{ type.label }}</label>
          }
        </div>
        <div class="row">
          <label><span>Tariffa</span><input name="rate" [(ngModel)]="ratePerKm" type="number" min="0" step="0.01" required /><small>€ per km</small></label>
          <label><span>Maggiorazione</span><input name="bonus" [(ngModel)]="bonusPct" type="number" min="0" step="1" required /><small>% per passeggero</small></label>
          <label><span>Passeggeri conteggiati</span><input name="maxPassengers" [(ngModel)]="maxPassengers" type="number" min="0" step="1" required /><small>al massimo</small></label>
        </div>
        <p class="example">{{ example() }}</p>
      </fieldset>
      <p>Le modifiche valgono per le presenze registrate da questo momento: i rimborsi già registrati non cambiano.</p>
      <footer><button class="button button--primary" [disabled]="saving() || !loaded">{{ saving() ? 'Salvataggio…' : 'Salva regole' }}</button><span class="feedback" [class.error]="errorMessage">{{ errorMessage || successMessage }}</span></footer>
    </form>
  `,
  styles: `form{display:grid;gap:var(--sp-5);max-width:680px;padding:var(--sp-6)}p{color:var(--text-secondary);margin:0}label{display:grid;gap:var(--sp-2);max-width:280px}fieldset{border:var(--border-thin) solid var(--border-subtle);border-radius:var(--radius-lg);display:grid;gap:var(--sp-4);margin:0;padding:var(--sp-5)}legend{font-weight:600;padding:0 var(--sp-2)}.types{display:flex;flex-wrap:wrap;gap:var(--sp-5)}label.check{align-items:center;display:flex;gap:var(--sp-2)}.row{display:grid;gap:var(--sp-4);grid-template-columns:repeat(3,minmax(0,1fr))}.example{font-size:var(--text-sm)}input[type=checkbox]{min-height:auto}@media (max-width:640px){.row{grid-template-columns:1fr}}input{background:var(--bg-raised);border:var(--border-thin) solid var(--border-default);border-radius:var(--radius-md);color:var(--text-primary);min-height:40px;padding:0 var(--sp-3)}small{color:var(--text-secondary)}footer{align-items:center;display:flex;gap:var(--sp-3)}.feedback{color:var(--color-success);font-size:var(--text-sm)}.error{color:var(--color-danger)}`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityRefundRulesPageComponent {
  private readonly settings = inject(SettingsService);
  protected rehearsal = '0.00';
  protected concert = '0.00';
  protected event = '0.00';
  protected readonly types = TYPES;
  protected enabledTypes = new Set<RefundActivityType>(['event']);
  protected ratePerKm = '0.00';
  protected bonusPct = 0;
  protected maxPassengers = 4;
  protected loaded = false;
  protected readonly saving = signal(false);
  protected successMessage = '';
  protected errorMessage = '';
  private rules: ActivityRefundRules | null = null;

  constructor() {
    this.settings.activityRefundRules().subscribe({ next: (rules) => this.setForm(rules), error: (error: unknown) => this.errorMessage = apiErrorMessage(error, 'Impossibile caricare le regole di rimborso.') });
  }

  protected save(): void {
    if (!this.rules) return;
    const bonus = Number(this.bonusPct);
    const max = Number(this.maxPassengers);
    if (!Number.isInteger(bonus) || !Number.isInteger(max) || bonus < 0 || max < 0) {
      this.errorMessage = 'Maggiorazione e passeggeri devono essere numeri interi non negativi.';
      return;
    }
    this.saving.set(true); this.successMessage = ''; this.errorMessage = '';
    const mileage = {
      enabled_types: TYPES.map((t) => t.value).filter((t) => this.enabledTypes.has(t)),
      rate_per_km: Number(this.ratePerKm || 0).toFixed(2),
      passenger_bonus_pct: bonus,
      max_bonus_passengers: max,
    };
    this.settings.saveActivityRefundRules({ ...this.rules, rehearsal: this.rehearsal, concert: this.concert, event: this.event, mileage }).subscribe({
      next: (rules) => { this.setForm(rules); this.saving.set(false); this.successMessage = 'Regole di rimborso salvate.'; },
      error: (error: unknown) => { this.saving.set(false); this.errorMessage = apiErrorMessage(error, 'Salvataggio non riuscito.'); },
    });
  }

  private setForm(rules: ActivityRefundRules): void {
    this.rules = rules; this.rehearsal = rules.rehearsal; this.concert = rules.concert; this.event = rules.event;
    this.enabledTypes = new Set(rules.mileage.enabled_types); this.ratePerKm = rules.mileage.rate_per_km;
    this.bonusPct = rules.mileage.passenger_bonus_pct; this.maxPassengers = rules.mileage.max_bonus_passengers;
    this.loaded = true;
  }

  protected toggleType(type: RefundActivityType, enabled: boolean): void {
    const next = new Set(this.enabledTypes);
    if (enabled) next.add(type); else next.delete(type);
    this.enabledTypes = next;
  }

  /** Worked example for 100 km A/R and 2 passengers, toll excluded. */
  protected example(): string {
    const base = 100 * Number(this.ratePerKm || 0);
    const pct = Math.min(2, Number(this.maxPassengers) || 0) * (Number(this.bonusPct) || 0);
    const total = Math.round(base * (100 + pct)) / 100;
    const eur = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' });
    return `Esempio: 100 km A/R con 2 passeggeri → ${eur.format(base)} + ${pct}% = ${eur.format(total)}, più il pedaggio del luogo.`;
  }
}
