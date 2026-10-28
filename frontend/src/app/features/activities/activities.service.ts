import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = 'http://localhost:8000/api/v1';

export interface Activity {
  readonly id: number; readonly type: 'rehearsal' | 'concert' | 'event'; readonly title: string;
  readonly description: string | null; readonly starts_at: string; readonly ends_at: string | null;
  readonly location: string | null; readonly status: 'planned' | 'confirmed' | 'cancelled' | 'completed';
  readonly notes: string | null; readonly archived_at: string | null; readonly version: number;
}

@Injectable({ providedIn: 'root' })
export class ActivitiesService {
  constructor(private readonly http: HttpClient) {}
  list(query = ''): Observable<Page<Activity>> { let params = new HttpParams().set('page_size', '100'); if (query.trim()) params = params.set('q', query.trim()); return this.http.get<Page<Activity>>(`${API_URL}/activities`, { params }); }
  get(id: number): Observable<Activity> { return this.http.get<Activity>(`${API_URL}/activities/${id}`); }
}
