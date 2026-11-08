import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

const API_URL = '/api/v1';

export interface LessonAttendance {
  readonly student_person_id: number;
  readonly student_name: string;
  readonly attendance: 'present' | 'absent' | null;
  readonly recorded_at: string | null;
  readonly version: number | null;
}

export interface AttendanceResult { readonly lesson_id: number; readonly processed_rows: number; }

@Injectable({ providedIn: 'root' })
export class AttendanceService {
  constructor(private readonly http: HttpClient) {}

  list(lessonId: number): Observable<LessonAttendance[]> { return this.http.get<LessonAttendance[]>(`${API_URL}/lessons/${lessonId}/attendances`); }
  save(lessonId: number, rows: Pick<LessonAttendance, 'student_person_id' | 'attendance'>[]): Observable<AttendanceResult> { return this.http.put<AttendanceResult>(`${API_URL}/lessons/${lessonId}/attendances`, { rows }); }
  template(lessonId: number): Observable<Blob> { return this.http.get(`${API_URL}/lessons/${lessonId}/attendances/template`, { responseType: 'blob' }); }
  import(lessonId: number, file: File): Observable<AttendanceResult> { const form = new FormData(); form.append('file', file); return this.http.post<AttendanceResult>(`${API_URL}/lessons/${lessonId}/attendances/import`, form); }
}
