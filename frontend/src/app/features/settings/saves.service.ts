import { HttpClient, HttpResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

const API_URL = '/api/v1/maintenance/saves';

export interface SaveSummary {
  readonly created_at: string;
  readonly organization_name: string | null;
  readonly contents: {
    readonly people: number;
    readonly activities: number;
    readonly courses: number;
    readonly accounting_movements: number;
    readonly responsible_users: number;
    readonly attachments: number;
  };
  readonly pending_migrations: number;
}

export interface SaveImportResult {
  readonly summary: SaveSummary;
  readonly backup_file: string;
  readonly applied_migrations: readonly string[];
}

@Injectable({ providedIn: 'root' })
export class SavesService {
  private readonly http = inject(HttpClient);

  exportSave(): Observable<HttpResponse<Blob>> {
    return this.http.get(`${API_URL}/export`, { observe: 'response', responseType: 'blob' });
  }

  inspect(file: File): Observable<SaveSummary> {
    return this.http.post<SaveSummary>(`${API_URL}/inspect`, this.form(file));
  }

  importSave(file: File, password: string): Observable<SaveImportResult> {
    const body = this.form(file);
    body.append('password', password);
    return this.http.post<SaveImportResult>(`${API_URL}/import`, body);
  }

  private form(file: File): FormData {
    const body = new FormData();
    body.append('file', file, file.name);
    return body;
  }
}

/** File name sent by the server, or a dated fallback. */
export function downloadName(response: HttpResponse<Blob>): string {
  const header = response.headers.get('Content-Disposition') ?? '';
  return /filename="?([^";]+)"?/.exec(header)?.[1] ?? 'arsis.arsis-save';
}
