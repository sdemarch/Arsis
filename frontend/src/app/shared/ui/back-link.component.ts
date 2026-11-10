import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

/** Consistent parent-navigation control for forms, detail pages and sub-sections. */
@Component({
  selector: 'arsis-back-link',
  imports: [RouterLink],
  template: `
    <a class="back-link" [routerLink]="link()" [attr.aria-label]="'Torna a ' + label()">
      <svg aria-hidden="true" viewBox="0 0 16 16"><path d="M9.5 3.5 5 8l4.5 4.5M5.5 8h6" /></svg>
      <span>{{ label() }}</span>
    </a>
  `,
  styles: `
    :host { display: block; margin-bottom: var(--sp-5); }
    :host(.back-link--compact) { margin-bottom: 0; }
    .back-link { align-items: center; background: var(--bg-surface); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-full); color: var(--text-secondary); display: inline-flex; font-size: var(--text-sm); font-weight: var(--weight-medium); gap: var(--sp-2); min-height: 34px; padding: 0 var(--sp-3); text-decoration: none; }
    .back-link:hover { background: var(--color-accent-soft); border-color: var(--color-accent); color: var(--color-accent-hover); }
    svg { fill: none; height: 16px; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.5; width: 16px; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BackLinkComponent {
  readonly link = input.required<string | readonly unknown[]>();
  readonly label = input.required<string>();
}
