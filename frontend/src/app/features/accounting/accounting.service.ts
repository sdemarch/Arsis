import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1/accounting';

export type AccountingDirection = 'income' | 'expense';
export type AccountingAccount = 'bank' | 'cash';

export interface AccountingCategory {
  readonly id: number;
  readonly name: string;
  readonly direction: AccountingDirection | 'both';
  readonly required_person_role: 'student' | 'teacher' | 'member' | null;
  readonly course_required: boolean;
  readonly color: string | null;
  readonly is_active: boolean;
  readonly archived_at: string | null;
  readonly version: number;
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
}

@Injectable({ providedIn: 'root' })
export class AccountingService {
  constructor(private readonly http: HttpClient) {}

  categories(): Observable<AccountingCategory[]> {
    return this.http.get<AccountingCategory[]>(`${API_URL}/categories`);
  }

  movements(year: number): Observable<Page<AccountingMovement>> {
    return this.http.get<Page<AccountingMovement>>(`${API_URL}/movements`, {
      params: new HttpParams().set('fiscal_year', year).set('page_size', '100'),
    });
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
}
