import { ChangeDetectionStrategy, Component, ElementRef, HostListener, ViewChild, inject, input, output } from '@angular/core';

import { ChevronDownIconComponent } from './chevron-down-icon.component';

export interface FilterOption {
  readonly label: string;
  readonly value: string;
}

@Component({
  selector: 'arsis-filter-dropdown',
  imports: [ChevronDownIconComponent],
  template: `
    <details class="filter" #menu>
      <summary class="button button--secondary">
        <span>{{ displayLabel() }}</span>
        <arsis-chevron-down-icon />
      </summary>
      <div class="filter__menu" role="listbox" [attr.aria-label]="label()" [attr.aria-multiselectable]="multiple()">
        @for (option of options(); track option.value) {
          <button type="button" role="option" [attr.aria-selected]="isSelected(option.value)" (click)="toggle(option.value, menu)">
            <span class="filter__tick" [class.is-visible]="isSelected(option.value)" aria-hidden="true">✓</span>
            <span>{{ option.label }}</span>
          </button>
        }
      </div>
    </details>
  `,
  styles: `
    :host { display: inline-block; }
    .filter { position: relative; }
    summary { list-style: none; user-select: none; white-space: nowrap; }
    summary::-webkit-details-marker { display: none; }
    .filter[open] summary { background: var(--bg-raised); border-color: var(--color-accent); }
    .filter[open] arsis-chevron-down-icon { transform: rotate(180deg); }
    .filter__menu { background: var(--bg-surface); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); box-shadow: var(--shadow-md); display: grid; left: 0; min-width: 190px; padding: var(--sp-2); position: absolute; top: calc(100% + var(--sp-2)); z-index: 20; }
    .filter__menu button { align-items: center; background: transparent; border: 0; border-radius: var(--radius-sm); color: var(--text-primary); cursor: pointer; display: grid; font: inherit; font-size: var(--text-sm); gap: var(--sp-2); grid-template-columns: 16px 1fr; padding: var(--sp-2) var(--sp-3); text-align: left; width: 100%; }
    .filter__menu button:hover, .filter__menu button:focus-visible { background: var(--bg-raised); }
    .filter__menu button[aria-selected='true'] { color: var(--color-accent-hover); font-weight: var(--weight-medium); }
    .filter__tick { color: var(--color-accent); font-size: var(--text-sm); opacity: 0; }
    .filter__tick.is-visible { opacity: 1; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FilterDropdownComponent {
  private readonly host = inject(ElementRef<HTMLElement>);
  @ViewChild('menu', { static: true }) private readonly menu!: ElementRef<HTMLDetailsElement>;

  readonly label = input.required<string>();
  readonly options = input.required<readonly FilterOption[]>();
  readonly selected = input<readonly string[]>([]);
  readonly multiple = input(false);
  readonly selectionChange = output<readonly string[]>();

  protected isSelected(value: string): boolean {
    return this.selected().includes(value);
  }

  protected displayLabel(): string {
    const selectedOptions = this.options().filter((option) => this.isSelected(option.value));
    if (!selectedOptions.length) return this.label();
    if (selectedOptions.length === 1) return selectedOptions[0].label;
    return `${this.label()} · ${selectedOptions.length}`;
  }

  protected toggle(value: string, menu: HTMLDetailsElement): void {
    if (!this.multiple()) {
      this.selectionChange.emit([value]);
      menu.open = false;
      return;
    }

    const nextSelection = this.isSelected(value)
      ? this.selected().filter((selectedValue) => selectedValue !== value)
      : [...this.selected(), value];
    this.selectionChange.emit(nextSelection);
  }

  @HostListener('document:click', ['$event'])
  protected closeWhenClickingOutside(event: MouseEvent): void {
    if (!this.host.nativeElement.contains(event.target as Node)) this.menu.nativeElement.open = false;
  }

  @HostListener('document:keydown.escape')
  protected closeWithEscape(): void {
    this.menu.nativeElement.open = false;
  }
}
