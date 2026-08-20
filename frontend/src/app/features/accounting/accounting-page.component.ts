import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import accountingData from '../../../assets/mock/accounting.json';

@Component({
  selector: 'arsis-accounting-page',
  imports: [PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Amministrazione" title="Contabilità" description="Una base ordinata per i futuri flussi amministrativi." />

    <section class="summary-grid" aria-label="Riepilogo contabile">
      @for (item of data.summary; track item.label) {
        <article class="card summary-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <small>{{ item.note }}</small>
        </article>
      }
    </section>

    <section class="areas-grid" aria-label="Funzioni previste">
      @for (area of data.areas; track area.title) {
        <article class="card area-card">
          <span class="area-card__icon" aria-hidden="true">€</span>
          <div>
            <span class="status-badge status-badge--neutral">{{ area.status }}</span>
            <h2>{{ area.title }}</h2>
            <p>{{ area.description }}</p>
          </div>
        </article>
      }
    </section>
  `,
  styles: `
    :host { display: block; }
    .summary-grid, .areas-grid { display: grid; gap: var(--space-4); grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .summary-grid { margin-bottom: var(--space-6); }
    .summary-card { display: grid; gap: var(--space-2); padding: var(--space-5); }
    .summary-card span, .summary-card small, .area-card p { color: var(--color-text-muted); }
    .summary-card strong { color: var(--color-primary-700); font-family: var(--font-family-heading); font-size: var(--font-size-3xl); }
    .area-card { display: flex; gap: var(--space-4); min-height: 180px; padding: var(--space-5); }
    .area-card__icon { align-items: center; background: var(--color-primary-50); border-radius: var(--radius-lg); color: var(--color-primary-700); display: inline-flex; flex: 0 0 44px; font-family: var(--font-family-heading); font-size: var(--font-size-xl); height: 44px; justify-content: center; }
    .area-card h2 { font-size: var(--font-size-lg); margin: var(--space-3) 0 var(--space-2); }
    .area-card p { line-height: 1.6; margin: 0; }
    @media (max-width: 960px) { .summary-grid, .areas-grid { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccountingPageComponent {
  protected readonly data = accountingData;
}
