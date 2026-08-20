import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { PageHeaderComponent } from './page-header.component';

@Component({
  selector: 'arsis-placeholder-page',
  imports: [PageHeaderComponent],
  template: `
    <arsis-page-header [eyebrow]="eyebrow()" [title]="title()" [description]="description()" />
    <section class="empty-state">
      <span aria-hidden="true">♪</span>
      <h2>Area pronta per l'implementazione</h2>
      <p>Routing, layout e token di stile sono già collegati.</p>
    </section>
  `,
  styles: `
    .empty-state { background: var(--bg-surface); border: var(--border-thin) dashed var(--border-strong); border-radius: var(--radius-lg); color: var(--text-secondary); padding: var(--sp-12); text-align: center; }
    .empty-state span { color: var(--color-accent); font-family: var(--font-display); font-size: var(--text-3xl); }
    .empty-state h2 { color: var(--text-primary); font-family: var(--font-sans); font-size: var(--text-lg); margin: var(--sp-4) 0 var(--sp-2); }
    .empty-state p { margin: 0; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlaceholderPageComponent {
  readonly eyebrow = input('Arsis');
  readonly title = input.required<string>();
  readonly description = input('');
}
