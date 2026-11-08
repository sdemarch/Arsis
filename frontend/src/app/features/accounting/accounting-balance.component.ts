import { DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, effect, inject, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ACCOUNT_LABELS, AccountingCategory, AccountingService, AccountingSummary, apiErrorMessage } from './accounting.service';

interface CategoryRow {
  readonly name: string;
  readonly color: string | null;
  readonly amount: number;
}

/** Year balance: opening balances, closing balance per account and totals per category. */
@Component({
  selector: 'arsis-accounting-balance',
  imports: [DecimalPipe, FormsModule],
  template: `
    <section class="card opening">
      <h2>Saldi iniziali {{ year() }}</h2>
      <form (ngSubmit)="saveOpening()">
        <label>Banca (€)<input type="number" name="bank" step="0.01" [(ngModel)]="opening.bank" required /></label>
        <label>Cassa (€)<input type="number" name="cash" step="0.01" [(ngModel)]="opening.cash" required /></label>
        <button class="button button--primary" [disabled]="saving()">Salva saldi</button>
      </form>
      @if (message()) { <p class="message" [class.error]="failed()" role="status">{{ message() }}</p> }
    </section>

    <div class="table-shell">
      <table>
        <thead><tr><th>Conto</th><th class="num">Saldo iniziale</th><th class="num">Entrate</th><th class="num">Uscite</th><th class="num">Saldo finale</th></tr></thead>
        <tbody>
          @for (row of summary()?.accounts ?? []; track row.account) {
            <tr>
              <td>{{ accountLabels[row.account] }}</td>
              <td class="num">{{ +row.opening | number: '1.2-2' }} €</td>
              <td class="num in">{{ +row.income | number: '1.2-2' }} €</td>
              <td class="num out">{{ +row.expense | number: '1.2-2' }} €</td>
              <td class="num"><strong [class.out]="+row.closing < 0">{{ +row.closing | number: '1.2-2' }} €</strong></td>
            </tr>
          }
        </tbody>
        @if (total(); as t) {
          <tfoot><tr><th>Totale</th><th class="num">{{ t.opening | number: '1.2-2' }} €</th><th class="num">{{ t.income | number: '1.2-2' }} €</th><th class="num">{{ t.expense | number: '1.2-2' }} €</th><th class="num">{{ t.closing | number: '1.2-2' }} €</th></tr></tfoot>
        }
      </table>
    </div>

    <div class="categories">
      @for (group of groups(); track group.title) {
        <section class="card">
          <h2>{{ group.title }}</h2>
          <ul>
            @for (row of group.rows; track row.name) {
              <li><span><i [style.background]="row.color ?? 'var(--border-strong)'"></i>{{ row.name }}</span><span>{{ row.amount | number: '1.2-2' }} €</span></li>
            } @empty {
              <li class="empty">Nessun movimento.</li>
            }
          </ul>
        </section>
      }
    </div>
  `,
  styles: `
    :host { display: grid; gap: var(--sp-6); }
    .card { padding: var(--sp-5); }
    h2 { font-size: var(--text-lg); margin: 0 0 var(--sp-4); }
    form { align-items: end; display: flex; flex-wrap: wrap; gap: var(--sp-4); }
    label { display: grid; gap: var(--sp-2); }
    input { min-height: 38px; }
    .message { margin: var(--sp-3) 0 0; color: var(--color-success); }
    .error, .out { color: var(--color-danger); }
    .in { color: var(--color-success); }
    table { width: 100%; }
    th, td { border-bottom: var(--border-thin) solid var(--border-subtle); padding: var(--sp-3); text-align: left; }
    .num { text-align: right; white-space: nowrap; }
    .categories { display: grid; gap: var(--sp-4); grid-template-columns: repeat(2, minmax(0, 1fr)); }
    ul { list-style: none; margin: 0; padding: 0; }
    li { border-top: var(--border-thin) solid var(--border-subtle); display: flex; justify-content: space-between; padding: var(--sp-2) 0; }
    li span:first-child { align-items: center; display: flex; gap: var(--sp-2); }
    i { border-radius: var(--radius-full); display: inline-block; height: 10px; width: 10px; }
    .empty { color: var(--text-secondary); }
    @media (max-width: 800px) { .categories { grid-template-columns: 1fr; } .table-shell { overflow-x: auto; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccountingBalanceComponent {
  private readonly api = inject(AccountingService);

  readonly year = input.required<number>();
  readonly summary = input.required<AccountingSummary | null>();
  readonly categories = input.required<AccountingCategory[]>();
  readonly openingSaved = output<void>();

  protected readonly accountLabels = ACCOUNT_LABELS;
  protected opening = { bank: 0, cash: 0 };
  protected readonly saving = signal(false);
  protected readonly message = signal('');
  protected readonly failed = signal(false);

  protected readonly total = computed(() => {
    const accounts = this.summary()?.accounts ?? [];
    if (!accounts.length) return null;
    const sum = (key: 'opening' | 'income' | 'expense' | 'closing') => accounts.reduce((s, a) => s + Number(a[key]), 0);
    return { opening: sum('opening'), income: sum('income'), expense: sum('expense'), closing: sum('closing') };
  });

  protected readonly groups = computed(() => {
    const rows = (direction: 'income' | 'expense'): CategoryRow[] =>
      (this.summary()?.categories ?? [])
        .filter((c) => c.direction === direction)
        .map((c) => {
          const category = this.categories().find((x) => x.id === c.category_id);
          return { name: category?.name ?? `Categoria #${c.category_id}`, color: category?.color ?? null, amount: Number(c.amount) };
        })
        .sort((a, b) => b.amount - a.amount);
    return [
      { title: 'Entrate per categoria', rows: rows('income') },
      { title: 'Uscite per categoria', rows: rows('expense') },
    ];
  });

  constructor() {
    effect(() => {
      const accounts = this.summary()?.accounts ?? [];
      const opening = (account: string) => Number(accounts.find((a) => a.account === account)?.opening ?? 0);
      this.opening = { bank: opening('bank'), cash: opening('cash') };
    });
  }

  protected saveOpening(): void {
    this.saving.set(true);
    this.api.saveOpeningBalances(this.year(), { bank: Number(this.opening.bank).toFixed(2), cash: Number(this.opening.cash).toFixed(2) }).subscribe({
      next: () => {
        this.saving.set(false);
        this.failed.set(false);
        this.message.set('Saldi iniziali salvati.');
        this.openingSaved.emit();
      },
      error: (err: unknown) => {
        this.saving.set(false);
        this.failed.set(true);
        this.message.set(apiErrorMessage(err, 'Salvataggio dei saldi non riuscito.'));
      },
    });
  }
}
