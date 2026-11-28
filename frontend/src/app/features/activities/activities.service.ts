import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1';

export interface Activity {
  readonly id: number; readonly type: 'rehearsal' | 'concert' | 'event'; readonly title: string;
  readonly description: string | null; readonly starts_at: string; readonly ends_at: string | null;
  readonly location: string | null; readonly status: 'planned' | 'confirmed' | 'cancelled' | 'completed';
  readonly place_id: number | null; readonly place: ActivityPlace | null;
  readonly notes: string | null; readonly archived_at: string | null; readonly version: number;
  readonly participant_count: number; readonly present_count: number; readonly absent_count: number;
  readonly reimbursement_flat: string; readonly reimbursement_mileage: string;
  readonly reimbursement_highway: string; readonly reimbursement_total: string;
  readonly driver_count: number; readonly passenger_count: number;
  readonly series_id: number | null; readonly series: ActivitySeriesSummary | null;
}
/** The series an activity belongs to (RB-22), with its position in it. */
export interface ActivitySeriesSummary {
  readonly id: number; readonly frequency: Frequency; readonly interval: number; readonly weekdays: number[];
  readonly starts_on: string; readonly ends_on: string; readonly description: string;
  readonly occurrence_count: number; readonly position: number;
}
export type Frequency = 'weekly' | 'monthly';
/** Weekdays are ISO numbers: 1 = Monday … 7 = Sunday. */
export interface Recurrence { readonly frequency: Frequency; readonly interval: number; readonly weekdays: number[] | null; readonly ends_on: string; }
export interface SeriesPreview { readonly dates: string[]; readonly description: string; }
export interface SeriesBulkResult { readonly updated: number; readonly archived: number; readonly kept: number; }
export type SeriesFollowingWrite = Partial<Pick<ActivityWrite, 'type' | 'title' | 'status' | 'location' | 'place_id' | 'notes' | 'description' | 'recalculate_refunds'>>;
export interface ActivitySeriesWrite extends Omit<ActivityWrite, 'starts_at' | 'version' | 'recalculate_refunds'> {
  readonly starts_on: string; readonly recurrence: Recurrence;
  /** One local-midnight timestamp per preview date, with the browser's own UTC offset. */
  readonly occurrences: string[];
}
export interface ActivityPlace {
  readonly id: number; readonly name: string; readonly distance_km: number;
  readonly highway_cost: string; readonly archived: boolean;
}
export type Attendance = 'present' | 'absent';
export interface Participant {
  readonly person_id: number;
  readonly person_name: string;
  readonly attendance: Attendance | null;
  readonly attendance_recorded_at: string | null;
  readonly is_driver: boolean;
  readonly passenger_count: number | null;
  readonly refund_flat_amount: string;
  readonly refund_distance_km: number | null;
  readonly refund_bonus_pct: number | null;
  readonly refund_mileage_amount: string;
  readonly refund_highway_amount: string;
  readonly refund_total: string;
  readonly version: number;
}
export interface AttendanceWrite {
  readonly person_id: number;
  readonly attendance: Attendance | null;
  readonly is_driver?: boolean;
  readonly passenger_count?: number | null;
}
export interface Participation {
  readonly activity_id: number;
  readonly title: string;
  readonly type: Activity['type'];
  readonly starts_at: string;
  readonly status: Activity['status'];
  readonly attendance: Attendance | null;
  readonly is_driver: boolean;
  readonly passenger_count: number | null;
  readonly distance_km: number | null;
  readonly reimbursement_flat: string;
  readonly reimbursement_mileage: string;
  readonly reimbursement_highway: string;
  readonly reimbursement_amount: string;
}
export interface RefundSummaryRow {
  readonly person_id: number;
  readonly person_name: string;
  readonly rehearsal: string;
  readonly concert: string;
  readonly event: string;
  readonly mileage: string;
  readonly highway: string;
  readonly distance_km: number;
  readonly total: string;
}
export interface ActivityWrite { readonly type: Activity['type']; readonly title: string; readonly starts_at: string; readonly status?: Activity['status']; readonly location?: string | null; readonly place_id?: number | null; readonly recalculate_refunds?: boolean; readonly description?: string | null; readonly notes?: string | null; readonly version?: number; }

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

  previewSeries(startsOn: string, recurrence: Recurrence): Observable<SeriesPreview> { return this.http.post<SeriesPreview>(`${API_URL}/activities/series/preview`, { starts_on: startsOn, recurrence }); }
  createSeries(payload: ActivitySeriesWrite): Observable<Activity[]> { return this.http.post<Activity[]>(`${API_URL}/activities/series`, payload); }
  /** Same changes on this occurrence and all the following ones of its series. */
  updateFollowing(id: number, payload: SeriesFollowingWrite): Observable<SeriesBulkResult> { return this.http.patch<SeriesBulkResult>(`${API_URL}/activities/${id}/following`, payload); }
  /** Archive the occurrences after this one; those with recorded attendance stay. */
  endSeries(id: number): Observable<SeriesBulkResult> { return this.http.post<SeriesBulkResult>(`${API_URL}/activities/${id}/end-series`, {}); }

  participants(id: number): Observable<Participant[]> { return this.http.get<Participant[]>(`${API_URL}/activities/${id}/participants`); }
  saveAttendance(id: number, rows: AttendanceWrite[]): Observable<Participant[]> { return this.http.put<Participant[]>(`${API_URL}/activities/${id}/attendances`, { rows }); }
  participations(personId: number): Observable<Participation[]> { return this.http.get<Participation[]>(`${API_URL}/activities/participations`, { params: new HttpParams().set('person_id', personId) }); }
  refundSummary(): Observable<RefundSummaryRow[]> { return this.http.get<RefundSummaryRow[]>(`${API_URL}/activities/refund-summary`); }
}
