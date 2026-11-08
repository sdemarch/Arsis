import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1';

export interface Lesson {
  readonly id: number;
  readonly course_id: number;
  readonly teacher_person_id: number;
  readonly starts_at: string;
  readonly ends_at: string | null;
  readonly topic: string | null;
  readonly status: 'planned' | 'completed' | 'cancelled';
  readonly notes: string | null;
  readonly archived_at: string | null;
  readonly version: number;
}

export interface LessonWrite {
  readonly version?: number;
  readonly course_id?: number;
  readonly teacher_person_id?: number;
  readonly starts_at?: string;
  readonly ends_at?: string | null;
  readonly topic?: string | null;
  readonly status?: Lesson['status'];
  readonly notes?: string | null;
}

@Injectable({ providedIn: 'root' })
export class LessonsService {
  constructor(private readonly http: HttpClient) {}

  list(query = ''): Observable<Page<Lesson>> {
    let params = new HttpParams().set('page_size', '100');
    if (query.trim()) params = params.set('q', query.trim());
    return this.http.get<Page<Lesson>>(`${API_URL}/lessons`, { params });
  }

  get(id: number): Observable<Lesson> { return this.http.get<Lesson>(`${API_URL}/lessons/${id}`); }
  create(payload: LessonWrite): Observable<Lesson> { return this.http.post<Lesson>(`${API_URL}/lessons`, payload); }
  update(id: number, payload: LessonWrite): Observable<Lesson> { return this.http.patch<Lesson>(`${API_URL}/lessons/${id}`, payload); }
  archive(id: number, version: number): Observable<Lesson> { return this.http.delete<Lesson>(`${API_URL}/lessons/${id}`, { params: new HttpParams().set('version', version) }); }
}
