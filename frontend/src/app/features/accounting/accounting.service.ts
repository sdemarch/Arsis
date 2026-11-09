import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

export { apiErrorMessage } from '../../core/api/api-error';

const API_URL = '/api/v1/accounting';

export type AccountingDirection = 'income' | 'expense';
export type AccountingAccount = 'bank' | 'cash';
export type AccountingPersonRole = 'student' | 'teacher' | 'member';

export const ACCOUNT_LABELS: Record<AccountingAccount, string> = { bank: 'Banca', cash: 'Cassa' };
export const DIRECTION_LABELS: Record<AccountingDirection | 'both', string> = { income: 'Entrata', expense: 'Uscita', both: 'Entrata o uscita' };
export const ROLE_LABELS: Record<AccountingPersonRole, string> = { student: 'Allievo', teacher: 'Insegnante', member: 'Socio' };

export interface AccountingCategory {
  readonly id: number;
  readonly name: string;
  readonly direction: AccountingDirection | 'both';
  readonly required_person_role: AccountingPersonRole | null;
  readonly course_required: boolean;
  readonly color: string | null;
  readonly display_order: number;
  readonly is_active: boolean;
  readonly archived_at: string | null;
  readonly version: number;
}

export interface AccountingCategoryWrite {
  readonly version?: number;
  readonly name?: string;
  readonly direction?: AccountingDirection | 'both';
  readonly required_person_role?: AccountingPersonRole | null;
  readonly course_required?: boolean;
  readonly color?: string | null;
  readonly display_order?: number;
}

export interface AccountingMovement {
  readonly id: number;
  readonly occurred_on: string;
  readonly direction: AccountingDirection;
  readonly account: AccountingAccount;
  readonly category_id: number;
  readonly amount: string;
  readonly subject: string;
  readonly person_id: number | null;
  readonly course_id: number | null;
  readonly description: string;
  readonly document_reference: string | null;
  readonly is_highlighted: boolean;
  readonly version: number;
}

export interface AccountingMovementWrite {
  readonly version?: number;
  readonly occurred_on?: string;
  readonly direction?: AccountingDirection;
  readonly account?: AccountingAccount;
  readonly category_id?: number;
  readonly amount?: string;
  readonly subject?: string;
  readonly person_id?: number | null;
  readonly course_id?: number | null;
  readonly description?: string;
  readonly document_reference?: string | null;
  readonly is_highlighted?: boolean;
}

export interface MovementFilters {
  readonly month: number | null;
  readonly account: AccountingAccount | null;
  readonly category_id: number | null;
  readonly q: string;
  readonly highlighted: boolean;
  readonly page: number;
}

export interface OpeningBalances {
  readonly fiscal_year: number;
  readonly bank: string;
  readonly cash: string;
}

export interface AccountSummary {
  readonly account: AccountingAccount;
  readonly opening: string;
  readonly income: string;
  readonly expense: string;
  readonly closing: string;
}

export interface AccountingSummary {
  readonly fiscal_year: number;
  readonly accounts: AccountSummary[];
  readonly categories: { readonly category_id: number; readonly direction: AccountingDirection; readonly amount: string }[];
}

@Injectable({ providedIn: 'root' })
export class AccountingService {
  constructor(private readonly http: HttpClient) {}

  categories(includeArchived = false): Observable<AccountingCategory[]> {
    return this.http.get<AccountingCategory[]>(`${API_URL}/categories`, {
      params: new HttpParams().set('include_archived', includeArchived),
    });
  }

  createCategory(payload: AccountingCategoryWrite): Observable<AccountingCategory> {
    return this.http.post<AccountingCategory>(`${API_URL}/categories`, payload);
  }

  updateCategory(id: number, payload: AccountingCategoryWrite & { version: number }): Observable<AccountingCategory> {
    return this.http.patch<AccountingCategory>(`${API_URL}/categories/${id}`, payload);
  }

  archiveCategory(id: number, version: number): Observable<AccountingCategory> {
    return this.http.delete<AccountingCategory>(`${API_URL}/categories/${id}`, { params: new HttpParams().set('version', version) });
  }

  movements(year: number, filters: MovementFilters): Observable<Page<AccountingMovement>> {
    let params = new HttpParams().set('fiscal_year', year).set('page', filters.page).set('page_size', '50');
    if (filters.month) params = params.set('month', filters.month);
    if (filters.account) params = params.set('account', filters.account);
    if (filters.category_id) params = params.set('category_id', filters.category_id);
    if (filters.q.trim()) params = params.set('q', filters.q.trim());
    if (filters.highlighted) params = params.set('is_highlighted', true);
    return this.http.get<Page<AccountingMovement>>(`${API_URL}/movements`, { params });
  }

  create(payload: AccountingMovementWrite): Observable<AccountingMovement> {
    return this.http.post<AccountingMovement>(`${API_URL}/movements`, payload);
  }

  update(id: number, payload: AccountingMovementWrite): Observable<AccountingMovement> {
    return this.http.patch<AccountingMovement>(`${API_URL}/movements/${id}`, payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${API_URL}/movements/${id}`);
  }

  summary(year: number): Observable<AccountingSummary> {
    return this.http.get<AccountingSummary>(`${API_URL}/summary/${year}`);
  }

  openingBalances(year: number): Observable<OpeningBalances> {
    return this.http.get<OpeningBalances>(`${API_URL}/opening-balances/${year}`);
  }

  saveOpeningBalances(year: number, payload: Pick<OpeningBalances, 'bank' | 'cash'>): Observable<OpeningBalances> {
    return this.http.put<OpeningBalances>(`${API_URL}/opening-balances/${year}`, payload);
  }
}
