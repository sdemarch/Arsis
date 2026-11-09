import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1';

export interface Activity {
  readonly id: number; readonly type: 'rehearsal' | 'concert' | 'event'; readonly title: string;
  readonly description: string | null; readonly starts_at: string; readonly ends_at: string | null;
  readonly location: string | null; readonly status: 'planned' | 'confirmed' | 'cancelled' | 'completed';
  readonly notes: string | null; readonly archived_at: string | null; readonly version: number;
  readonly participant_count: number; readonly present_count: number; readonly absent_count: number;
}
export type Attendance = 'present' | 'absent';
export interface Participant {
  readonly person_id: number;
  readonly person_name: string;
  readonly source: 'automatic' | 'manual';
  readonly attendance: Attendance | null;
  readonly attendance_recorded_at: string | null;
  readonly version: number;
}
export interface Participation {
  readonly activity_id: number;
  readonly title: string;
  readonly type: Activity['type'];
  readonly starts_at: string;
  readonly status: Activity['status'];
  readonly source: Participant['source'];
  readonly attendance: Attendance | null;
}
export interface ActivityWrite { readonly type: Activity['type']; readonly title: string; readonly starts_at: string; readonly status?: Activity['status']; readonly location?: string | null; readonly description?: string | null; readonly notes?: string | null; readonly version?: number; }

@Injectable({ providedIn: 'root' })
export class ActivitiesService {
  constructor(private readonly http: HttpClient) {}
  list(query = ''): Observable<Page<Activity>> { let params = new HttpParams().set('page_size', '100'); if (query.trim()) params = params.set('q', query.trim()); return this.http.get<Page<Activity>>(`${API_URL}/activities`, { params }); }
  /** Activities whose local start date falls between two `YYYY-MM-DD` days, inclusive. */
  listBetween(from: string, to: string): Observable<Page<Activity>> { return this.http.get<Page<Activity>>(`${API_URL}/activities`, { params: new HttpParams().set('page_size', '100').set('starts_from', from).set('starts_to', to).set('sort', 'starts_at') }); }
  get(id: number): Observable<Activity> { return this.http.get<Activity>(`${API_URL}/activities/${id}`); }
  create(payload: ActivityWrite): Observable<Activity> { return this.http.post<Activity>(`${API_URL}/activities`, payload); }
  update(id: number, payload: ActivityWrite): Observable<Activity> { return this.http.patch<Activity>(`${API_URL}/activities/${id}`, payload); }
  archive(id: number, version: number): Observable<Activity> { return this.http.delete<Activity>(`${API_URL}/activities/${id}`, { params: new HttpParams().set('version', version) }); }

  participants(id: number): Observable<Participant[]> { return this.http.get<Participant[]>(`${API_URL}/activities/${id}/participants`); }
  addParticipant(id: number, personId: number): Observable<Participant> { return this.http.post<Participant>(`${API_URL}/activities/${id}/participants`, { person_id: personId }); }
  removeParticipant(id: number, personId: number): Observable<void> { return this.http.delete<void>(`${API_URL}/activities/${id}/participants/${personId}`); }
  convokeMusicians(id: number): Observable<Participant[]> { return this.http.post<Participant[]>(`${API_URL}/activities/${id}/participants/musicians`, {}); }
  saveAttendance(id: number, rows: { person_id: number; attendance: Attendance | null }[]): Observable<Participant[]> { return this.http.put<Participant[]>(`${API_URL}/activities/${id}/attendances`, { rows }); }
  participations(personId: number): Observable<Participation[]> { return this.http.get<Participation[]>(`${API_URL}/activities/participations`, { params: new HttpParams().set('person_id', personId) }); }
}
