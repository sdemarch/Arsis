import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'arsis-chevron-down-icon',
  template: `
    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="m4 6 4 4 4-4" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
    </svg>
  `,
  styles: `
    :host { display: inline-flex; flex: 0 0 auto; height: 16px; width: 16px; }
    svg { display: block; height: 100%; width: 100%; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChevronDownIconComponent {}
