import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

const API_URL = '/api/v1';

export interface GeneralSettings {
  readonly organization_name: string;
  readonly organization_name_version: number;
  readonly archive_google_drive_url: string;
  readonly archive_google_drive_url_version: number;
  readonly default_theme: 'light' | 'dark';
  readonly default_theme_version: number;
}

export interface ResponsibleUser {
  readonly id: number;
  readonly email: string;
  readonly display_name: string;
  readonly is_active: boolean;
  readonly last_login_at: string | null;
  readonly version: number;
}

@Injectable({ providedIn: 'root' })
export class SettingsService {
  readonly general = signal<GeneralSettings | null>(null);

  constructor(private readonly http: HttpClient) {}

  loadGeneral(): Observable<GeneralSettings> {
    return this.http.get<GeneralSettings>(`${API_URL}/settings/general`).pipe(
      tap((settings) => this.general.set(settings)),
    );
  }

  saveGeneral(settings: GeneralSettings): Observable<GeneralSettings> {
    return this.http.put<GeneralSettings>(`${API_URL}/settings/general`, settings).pipe(
      tap((updated) => this.general.set(updated)),
    );
  }

  responsibleUsers(): Observable<ResponsibleUser[]> {
    return this.http.get<ResponsibleUser[]>(`${API_URL}/settings/responsible-users`);
  }

  addResponsibleUser(payload: { email: string; display_name: string; password: string }): Observable<ResponsibleUser> {
    return this.http.post<ResponsibleUser>(`${API_URL}/settings/responsible-users`, payload);
  }

  updateResponsibleUser(id: number, payload: { is_active: boolean; version: number }): Observable<ResponsibleUser> {
    return this.http.patch<ResponsibleUser>(`${API_URL}/settings/responsible-users/${id}`, payload);
  }
}
