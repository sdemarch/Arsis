import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = 'http://localhost:8000/api/v1';

export interface Course {
  readonly id: number;
  readonly name: string;
  readonly description: string | null;
  readonly mode: 'individual' | 'group';
  readonly category: 'instrument' | 'ensemble';
  readonly instrument_id: number | null;
  readonly teacher_person_id: number;
  readonly weekday: number | null;
  readonly start_time: string | null;
  readonly end_time: string | null;
  readonly annual_fee: string;
  readonly color: string;
  readonly status: 'active' | 'inactive';
  readonly notes: string | null;
  readonly archived_at: string | null;
  readonly version: number;
}

export interface CourseWrite {
  readonly version?: number;
  readonly name?: string;
  readonly description?: string | null;
  readonly mode?: 'individual' | 'group';
  readonly category?: 'instrument' | 'ensemble';
  readonly instrument_id?: number | null;
  readonly teacher_person_id?: number;
  readonly weekday?: number | null;
  readonly start_time?: string | null;
  readonly end_time?: string | null;
  readonly annual_fee?: string;
  readonly color?: string;
  readonly status?: 'active' | 'inactive';
  readonly notes?: string | null;
}

@Injectable({ providedIn: 'root' })
export class CoursesService {
  constructor(private readonly http: HttpClient) {}

  list(query = ''): Observable<Page<Course>> {
    let params = new HttpParams().set('page_size', '100');
    if (query.trim()) params = params.set('q', query.trim());
    return this.http.get<Page<Course>>(`${API_URL}/courses`, { params });
  }

  get(courseId: number): Observable<Course> { return this.http.get<Course>(`${API_URL}/courses/${courseId}`); }
  create(payload: CourseWrite): Observable<Course> { return this.http.post<Course>(`${API_URL}/courses`, payload); }
  update(courseId: number, payload: CourseWrite): Observable<Course> { return this.http.patch<Course>(`${API_URL}/courses/${courseId}`, payload); }
  archive(courseId: number, version: number): Observable<Course> { return this.http.delete<Course>(`${API_URL}/courses/${courseId}`, { params: new HttpParams().set('version', version) }); }
}
