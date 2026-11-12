import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { apiErrorMessage } from '../../core/api/api-error';
import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { ActivityRefundRules, SettingsService } from './settings.service';

@Component({
  selector: 'arsis-activity-refund-rules-page',
  imports: [BackLinkComponent, FormsModule, PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Configurazioni" title="Rimborsi attività" description="Definisci l’importo riconosciuto per ogni presenza registrata.">
      <arsis-back-link class="back-link--compact" link="/settings" label="Configurazioni" />
    </arsis-page-header>
    <form class="card" (ngSubmit)="save()">
      <p>Il rimborso è calcolato per ciascun partecipante segnato come presente. Le presenze assenti o non registrate non maturano alcun importo.</p>
      <label><span>Prova</span><input name="rehearsal" [(ngModel)]="rehearsal" type="number" min="0" step="0.01" required /><small>€ per presenza</small></label>
      <label><span>Concerto</span><input name="concert" [(ngModel)]="concert" type="number" min="0" step="0.01" required /><small>€ per presenza</small></label>
      <label><span>Evento</span><input name="event" [(ngModel)]="event" type="number" min="0" step="0.01" required /><small>€ per presenza</small></label>
      <footer><button class="button button--primary" [disabled]="saving() || !loaded">{{ saving() ? 'Salvataggio…' : 'Salva regole' }}</button><span class="feedback" [class.error]="errorMessage">{{ errorMessage || successMessage }}</span></footer>
    </form>
  `,
  styles: `form{display:grid;gap:var(--sp-5);max-width:680px;padding:var(--sp-6)}p{color:var(--text-secondary);margin:0}label{display:grid;gap:var(--sp-2);max-width:280px}input{background:var(--bg-raised);border:var(--border-thin) solid var(--border-default);border-radius:var(--radius-md);color:var(--text-primary);min-height:40px;padding:0 var(--sp-3)}small{color:var(--text-secondary)}footer{align-items:center;display:flex;gap:var(--sp-3)}.feedback{color:var(--color-success);font-size:var(--text-sm)}.error{color:var(--color-danger)}`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityRefundRulesPageComponent {
  private readonly settings = inject(SettingsService);
  protected rehearsal = '0.00';
  protected concert = '0.00';
  protected event = '0.00';
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
    this.saving.set(true); this.successMessage = ''; this.errorMessage = '';
    this.settings.saveActivityRefundRules({ ...this.rules, rehearsal: this.rehearsal, concert: this.concert, event: this.event }).subscribe({
      next: (rules) => { this.setForm(rules); this.saving.set(false); this.successMessage = 'Regole di rimborso salvate.'; },
      error: (error: unknown) => { this.saving.set(false); this.errorMessage = apiErrorMessage(error, 'Salvataggio non riuscito.'); },
    });
  }

  private setForm(rules: ActivityRefundRules): void {
    this.rules = rules; this.rehearsal = rules.rehearsal; this.concert = rules.concert; this.event = rules.event; this.loaded = true;
  }
}
