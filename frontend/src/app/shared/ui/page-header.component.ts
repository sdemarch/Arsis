import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'arsis-page-header',
  template: `
    <header class="page-header">
      <div>
        <p class="eyebrow">{{ eyebrow() }}</p>
        <h1>{{ title() }}</h1>
        @if (description()) { <p class="description">{{ description() }}</p> }
      </div>
      <ng-content />
    </header>
  `,
  styles: `
    .page-header { align-items: start; display: flex; justify-content: space-between; margin-bottom: var(--sp-8); }
    .eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-2); text-transform: uppercase; }
    h1 { margin: 0; }
    .description { color: var(--text-secondary); margin: var(--sp-2) 0 0; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageHeaderComponent {
  readonly eyebrow = input('Arsis');
  readonly title = input.required<string>();
  readonly description = input('');
}
