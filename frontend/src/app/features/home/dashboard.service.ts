import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { Activity } from '../activities/activities.service';

export interface DashboardSummary {
  readonly date: string;
  readonly people: { readonly active: number; readonly members: number; readonly musicians: number; readonly students: number; readonly teachers: number; readonly sections: number };
  readonly school: { readonly active_courses: number; readonly active_enrollments: number; readonly enrolled_students: number; readonly lessons_this_month: number; readonly attendance_rate: number | null };
  readonly upcoming_activities: { readonly id: number; readonly title: string; readonly type: Activity['type']; readonly status: Activity['status']; readonly starts_at: string; readonly location: string | null; readonly participant_count: number }[];
  readonly today_lessons: { readonly id: number; readonly course_id: number; readonly course_name: string; readonly course_color: string; readonly teacher_name: string; readonly starts_at: string; readonly ends_at: string | null; readonly status: 'planned' | 'completed' | 'cancelled'; readonly students: number; readonly recorded: number }[];
  readonly course_students: { readonly course_id: number; readonly students: number }[];
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);

  summary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>('/api/v1/dashboard/summary');
  }
}
