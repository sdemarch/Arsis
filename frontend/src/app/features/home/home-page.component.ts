import { ChangeDetectionStrategy, Component } from '@angular/core';

import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-home-page',
  imports: [PageHeaderComponent],
  template: `
    <arsis-page-header
      eyebrow="Dashboard"
      title="Buongiorno, Stefano"
      description="Qui trovi le informazioni operative della tua associazione."
    />
    <section class="metrics" aria-label="Riepilogo persone attive">
      @for (metric of metrics; track metric.label) {
        <article class="metric-card">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
        </article>
      }
    </section>
    <section class="dashboard-grid">
      <article class="panel"><h2>Prossime attività</h2><p>Nessuna attività pianificata.</p></article>
      <article class="panel"><h2>Prossime lezioni</h2><p>Nessuna lezione registrata.</p></article>
    </section>
  `,
  styles: `
    .metrics { display: grid; gap: var(--sp-4); grid-template-columns: repeat(4, 1fr); margin-bottom: var(--sp-6); }
    .metric-card, .panel { background: var(--bg-surface); border: var(--border-thin) solid var(--border-subtle); border-radius: var(--radius-lg); box-shadow: var(--shadow-xs); }
    .metric-card { display: grid; gap: var(--sp-2); padding: var(--sp-5); }
    .metric-card span, .panel p { color: var(--text-secondary); }
    .metric-card strong { font-family: var(--font-display); font-size: var(--text-2xl); font-weight: var(--weight-semi); }
    .dashboard-grid { display: grid; gap: var(--sp-6); grid-template-columns: repeat(2, 1fr); }
    .panel { min-height: var(--panel-min-height); padding: var(--sp-6); }
    .panel h2 { font-family: var(--font-sans); font-size: var(--text-lg); margin: 0 0 var(--sp-4); }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePageComponent {
  protected readonly metrics = [
    { label: 'Soci', value: 0 },
    { label: 'Musicanti', value: 0 },
    { label: 'Allievi', value: 0 },
    { label: 'Insegnanti', value: 0 },
  ];
}
