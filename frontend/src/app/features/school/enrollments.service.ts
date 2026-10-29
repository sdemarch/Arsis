import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1';

export interface Enrollment {
  readonly id: number;
  readonly course_id: number;
  readonly student_person_id: number;
  readonly enrolled_on: string;
  readonly starts_on: string;
  readonly ends_on: string | null;
  readonly status: 'active' | 'completed' | 'cancelled';
  readonly notes: string | null;
  readonly archived_at: string | null;
  readonly version: number;
}

export interface EnrollmentWrite {
  readonly version?: number;
  readonly course_id?: number;
  readonly student_person_id?: number;
  readonly enrolled_on?: string;
  readonly starts_on?: string;
  readonly ends_on?: string | null;
  readonly status?: Enrollment['status'];
  readonly notes?: string | null;
}

@Injectable({ providedIn: 'root' })
export class EnrollmentsService {
  constructor(private readonly http: HttpClient) {}
  list(query = ''): Observable<Page<Enrollment>> { let params = new HttpParams().set('page_size', '100'); if (query.trim()) params = params.set('q', query.trim()); return this.http.get<Page<Enrollment>>(`${API_URL}/enrollments`, { params }); }
  get(id: number): Observable<Enrollment> { return this.http.get<Enrollment>(`${API_URL}/enrollments/${id}`); }
  create(payload: EnrollmentWrite): Observable<Enrollment> { return this.http.post<Enrollment>(`${API_URL}/enrollments`, payload); }
  update(id: number, payload: EnrollmentWrite): Observable<Enrollment> { return this.http.patch<Enrollment>(`${API_URL}/enrollments/${id}`, payload); }
  archive(id: number, version: number): Observable<Enrollment> { return this.http.delete<Enrollment>(`${API_URL}/enrollments/${id}`, { params: new HttpParams().set('version', version) }); }
}
