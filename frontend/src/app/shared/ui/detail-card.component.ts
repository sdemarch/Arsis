import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'arsis-detail-card',
  imports: [RouterLink],
  template: `
    <a class="back-link" [routerLink]="backLink()">← {{ backLabel() }}</a>

    <article class="detail-card card">
      <header class="detail-card__header">
        <div class="detail-card__identity">
          <ng-content select="[detail-visual]" />
          <div>
            <p class="detail-card__eyebrow">{{ eyebrow() }}</p>
            <h1>{{ title() }}</h1>
            <p class="detail-card__subtitle">{{ subtitle() }}</p>
          </div>
        </div>
        <button class="button" [class.button--primary]="editing()" [class.button--secondary]="!editing()" type="button" (click)="editRequested.emit()">
          @if (editing()) { ✓ Salva modifiche } @else { ✎ Modifica }
        </button>
      </header>

      <div class="detail-card__body">
        <ng-content />
      </div>
    </article>
  `,
  styles: `
    :host { display: block; margin: 0 auto; max-width: 1040px; }
    .back-link { align-items: center; color: var(--text-secondary); display: inline-flex; font-size: var(--text-sm); gap: var(--sp-2); margin-bottom: var(--sp-5); text-decoration: none; }
    .back-link:hover { color: var(--color-accent-hover); }
    .detail-card { overflow: hidden; }
    .detail-card__header { align-items: center; background: var(--bg-raised); border-bottom: var(--border-thin) solid var(--border-subtle); display: flex; gap: var(--sp-5); justify-content: space-between; padding: var(--sp-6) var(--sp-8); }
    .detail-card__identity { align-items: center; display: flex; gap: var(--sp-4); min-width: 0; }
    .detail-card__eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    h1 { font-family: var(--font-sans); font-size: var(--text-2xl); margin: 0; }
    .detail-card__subtitle { color: var(--text-secondary); margin: var(--sp-1) 0 0; }
    .detail-card__body { padding: var(--sp-8); }
    @media (max-width: 720px) {
      .detail-card__header { align-items: stretch; flex-direction: column; padding: var(--sp-5); }
      .detail-card__header .button { width: 100%; }
      .detail-card__body { padding: var(--sp-5); }
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DetailCardComponent {
  readonly backLink = input.required<string>();
  readonly backLabel = input.required<string>();
  readonly eyebrow = input.required<string>();
  readonly title = input.required<string>();
  readonly subtitle = input('');
  readonly editing = input(false);
  readonly editRequested = output<void>();
}
