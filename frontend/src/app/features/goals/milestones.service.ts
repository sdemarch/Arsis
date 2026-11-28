import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1/milestones';

export type MilestoneMetric = 'rehearsal_count' | 'concert_count' | 'event_count' | 'attendance_count' | 'reimbursement_total';

export const METRIC_OPTIONS: readonly { value: MilestoneMetric; label: string; unit: string }[] = [
  { value: 'rehearsal_count', label: 'Presenze alle prove', unit: 'prove' },
  { value: 'concert_count', label: 'Presenze ai concerti', unit: 'concerti' },
  { value: 'event_count', label: 'Presenze alle processioni', unit: 'processioni' },
  { value: 'attendance_count', label: 'Presenze totali', unit: 'presenze' },
  { value: 'reimbursement_total', label: 'Rimborsi maturati (€)', unit: '€' },
];

export interface Milestone {
  readonly id: number;
  readonly name: string;
  readonly metric: MilestoneMetric;
  readonly threshold: string;
  readonly notes: string | null;
  readonly archived_at: string | null;
  readonly version: number;
}

export interface MilestoneWrite {
  readonly name?: string;
  readonly metric?: MilestoneMetric;
  readonly threshold?: string;
  readonly notes?: string | null;
}

export interface MilestoneProgress {
  readonly person_id: number;
  readonly person_name: string;
  readonly progress: string;
  readonly remaining: string;
  readonly times_reached: number;
  readonly last_reset_id: number | null;
  readonly last_reset_at: string | null;
}

export interface MilestoneBoardEntry {
  readonly milestone: Milestone;
  readonly reached: MilestoneProgress[];
  readonly in_progress: MilestoneProgress[];
}

@Injectable({ providedIn: 'root' })
export class MilestonesService {
  constructor(private readonly http: HttpClient) {}

  list(includeArchived = false): Observable<Milestone[]> {
    const params = new HttpParams().set('page_size', '100').set('include_archived', includeArchived);
    return this.http.get<Page<Milestone>>(API_URL, { params }).pipe(map((page) => page.items));
  }

  board(): Observable<MilestoneBoardEntry[]> {
    return this.http.get<MilestoneBoardEntry[]>(`${API_URL}/board`);
  }

  create(payload: MilestoneWrite): Observable<Milestone> {
    return this.http.post<Milestone>(API_URL, payload);
  }

  update(id: number, payload: MilestoneWrite & { version: number }): Observable<Milestone> {
    return this.http.patch<Milestone>(`${API_URL}/${id}`, payload);
  }

  archive(id: number, version: number): Observable<Milestone> {
    return this.http.delete<Milestone>(`${API_URL}/${id}`, { params: new HttpParams().set('version', version) });
  }

  reset(id: number, personIds: number[]): Observable<MilestoneBoardEntry> {
    return this.http.post<MilestoneBoardEntry>(`${API_URL}/${id}/resets`, { person_ids: personIds });
  }

  undoReset(id: number, resetId: number): Observable<MilestoneBoardEntry> {
    return this.http.delete<MilestoneBoardEntry>(`${API_URL}/${id}/resets/${resetId}`);
  }
}

/** "10 prove", "150,00 €": a metric value in the unit people read it in. */
export function formatMetric(metric: MilestoneMetric, value: string | number): string {
  const amount = Number(value);
  if (metric === 'reimbursement_total') {
    return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(amount);
  }
  const unit = METRIC_OPTIONS.find((option) => option.value === metric)?.unit ?? '';
  return `${Math.round(amount)} ${unit}`;
}

export function metricLabel(metric: MilestoneMetric): string {
  return METRIC_OPTIONS.find((option) => option.value === metric)?.label ?? metric;
}
