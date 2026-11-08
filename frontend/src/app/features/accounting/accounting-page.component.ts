import { DatePipe, DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, debounceTime, map, of, switchMap } from 'rxjs';

import { Page } from '../../core/api/api.types';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { PeopleService, PersonListItem } from '../people/people.service';
import { Course, CoursesService } from '../school/courses.service';
import { AccountingBalanceComponent } from './accounting-balance.component';
import {
  ACCOUNT_LABELS,
  AccountingCategory,
  AccountingMovement,
  AccountingService,
  AccountingSummary,
  DIRECTION_LABELS,
  MovementFilters,
  apiErrorMessage,
} from './accounting.service';
import { MovementFormComponent } from './movement-form.component';

const MONTHS = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'];

@Component({
  selector: 'arsis-accounting-page',
  imports: [AccountingBalanceComponent, DatePipe, DecimalPipe, FormsModule, MovementFormComponent, PageHeaderComponent, RouterLink],
  templateUrl: './accounting-page.component.html',
  styleUrl: './accounting-page.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccountingPageComponent {
  private readonly api = inject(AccountingService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  protected readonly months = MONTHS;
  protected readonly accountLabels = ACCOUNT_LABELS;
  protected readonly directionLabels = DIRECTION_LABELS;

  protected readonly tab = toSignal(this.route.queryParamMap.pipe(map((params) => (params.get('tab') === 'balance' ? 'balance' : 'register'))), { initialValue: 'register' });
  protected readonly year = signal(new Date().getFullYear());
  protected readonly filters = signal<MovementFilters>({ month: null, account: null, category_id: null, q: '', page: 1 });
  protected readonly editing = signal<AccountingMovement | null>(null);
  protected readonly error = signal('');
  private readonly reload = signal(0);

  protected readonly categories = signal<AccountingCategory[]>([]);
  protected readonly people = toSignal(inject(PeopleService).listPeople('').pipe(map((page) => page.items), catchError(() => of<PersonListItem[]>([]))), { initialValue: [] });
  protected readonly courses = toSignal(inject(CoursesService).list().pipe(map((page) => page.items), catchError(() => of<Course[]>([]))), { initialValue: [] });

  private readonly page = toSignal(
    toObservable(computed(() => ({ year: this.year(), filters: this.filters(), reload: this.reload() }))).pipe(
      debounceTime(150),
      switchMap(({ year, filters }) =>
        this.api.movements(year, filters).pipe(
          catchError(() => {
            this.error.set('Impossibile caricare il registro.');
            return of<Page<AccountingMovement> | null>(null);
          }),
        ),
      ),
    ),
    { initialValue: null },
  );
  protected readonly movements = computed(() => this.page()?.items ?? []);
  protected readonly meta = computed(() => this.page()?.meta ?? null);

  protected readonly summary = toSignal(
    toObservable(computed(() => ({ year: this.year(), reload: this.reload() }))).pipe(
      switchMap(({ year }) => this.api.summary(year).pipe(catchError(() => of<AccountingSummary | null>(null)))),
    ),
    { initialValue: null },
  );
  protected readonly accountCards = computed(() => {
    const accounts = this.summary()?.accounts ?? [];
    return [
      ...accounts.map((a) => ({ label: this.accountLabels[a.account], value: Number(a.closing) })),
      { label: 'Totale disponibile', value: accounts.reduce((sum, a) => sum + Number(a.closing), 0) },
    ];
  });

  constructor() {
    this.api.categories(true).subscribe({ next: (items) => this.categories.set(items) });
  }

  protected setTab(tab: 'register' | 'balance'): void {
    void this.router.navigate([], { relativeTo: this.route, queryParams: { tab }, queryParamsHandling: 'merge', replaceUrl: true });
  }

  protected shiftYear(delta: number): void {
    this.year.update((year) => year + delta);
    this.editing.set(null);
    this.filters.update((f) => ({ ...f, page: 1 }));
  }

  protected setFilter(patch: Partial<MovementFilters>): void {
    this.filters.update((f) => ({ ...f, ...patch, page: patch.page ?? 1 }));
  }

  protected categoryName(id: number): string {
    return this.categories().find((c) => c.id === id)?.name ?? `Categoria #${id}`;
  }

  protected categoryColor(id: number): string | null {
    return this.categories().find((c) => c.id === id)?.color ?? null;
  }

  protected edit(movement: AccountingMovement): void {
    this.editing.set(movement);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  protected onSaved(): void {
    this.editing.set(null);
    this.error.set('');
    this.refresh();
  }

  protected remove(movement: AccountingMovement): void {
    if (!window.confirm(`Eliminare il movimento “${movement.description}”?`)) return;
    this.api.delete(movement.id).subscribe({
      next: () => {
        if (this.editing()?.id === movement.id) this.editing.set(null);
        this.refresh();
      },
      error: (err: unknown) => this.error.set(apiErrorMessage(err, 'Eliminazione non riuscita.')),
    });
  }

  protected refresh(): void {
    this.error.set('');
    this.reload.update((n) => n + 1);
  }
}
