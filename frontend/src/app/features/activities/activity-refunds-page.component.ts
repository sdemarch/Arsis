import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { BackLinkComponent } from '../../shared/ui/back-link.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { ActivitiesService, RefundSummaryRow } from './activities.service';

@Component({
  selector: 'arsis-activity-refunds-page',
  imports: [BackLinkComponent, PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Attività" title="Riepilogo rimborsi" description="Importi registrati con le presenze: quota per tipologia di attività e rimborso chilometrico agli autisti.">
      <arsis-back-link class="back-link--compact" link="/activities" label="Attività" />
    </arsis-page-header>
    <p class="note">Questo riepilogo è informativo e non genera movimenti nella prima nota.</p>
    <div class="table-shell card"><table><thead><tr><th>Socio</th><th>Prove</th><th>Concerti</th><th>Eventi</th><th>Km guidati</th><th>Carburante</th><th>Pedaggi</th><th>Totale</th></tr></thead><tbody>
      @for (row of rows(); track row.person_id) { <tr><td><a [routerLink]="['/people', row.person_id]">{{ row.person_name }}</a></td><td>{{ currency(row.rehearsal) }}</td><td>{{ currency(row.concert) }}</td><td>{{ currency(row.event) }}</td><td>{{ row.distance_km || '—' }}</td><td>{{ currency(row.mileage) }}</td><td>{{ currency(row.highway) }}</td><td><strong>{{ currency(row.total) }}</strong></td></tr> }
      @empty { <tr><td colspan="8" class="empty">Nessun rimborso maturato: registra almeno una presenza.</td></tr> }
    </tbody></table></div>
  `,
  styles: `.note{color:var(--text-secondary);margin:0 0 var(--sp-4)}.table-shell{overflow-x:auto;padding:var(--sp-2)}table{border-collapse:collapse;width:100%}th,td{border-bottom:var(--border-thin) solid var(--border-subtle);padding:var(--sp-3);text-align:left}th{color:var(--text-secondary);font-size:var(--text-sm)}td:not(:first-child){text-align:right}.empty{color:var(--text-secondary);text-align:center!important}`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityRefundsPageComponent {
  private readonly activities = inject(ActivitiesService);
  protected readonly rows = signal<RefundSummaryRow[]>([]);
  constructor() { this.activities.refundSummary().subscribe({ next: (rows) => this.rows.set(rows) }); }
  protected currency(value: string): string { return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(Number(value)); }
}
