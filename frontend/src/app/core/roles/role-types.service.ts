import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

const API_URL = '/api/v1/role-types';

/** A role people can hold (RB-21). Built-in ones drive school, band and member data. */
export interface RoleType {
  readonly id: number;
  readonly code: string;
  readonly name: string;
  readonly plural_name: string;
  readonly description: string | null;
  readonly is_system: boolean;
  readonly display_order: number;
  readonly active_people: number;
  readonly archived_at: string | null;
  readonly version: number;
}

export interface RoleTypeWrite {
  readonly name?: string;
  readonly plural_name?: string;
  readonly description?: string | null;
  readonly display_order?: number;
}

/**
 * The role catalogue, loaded once and shared: labels and options everywhere come
 * from here. Archived roles are kept so past assignments still read well.
 */
@Injectable({ providedIn: 'root' })
export class RoleTypesService {
  private readonly http = inject(HttpClient);
  private readonly all = signal<RoleType[]>([]);
  private requested = false;

  /** Roles that can be assigned, in display order. */
  readonly active = computed(() => this.all().filter((role) => !role.archived_at));
  readonly archived = computed(() => this.all().filter((role) => role.archived_at));

  /** Starts loading on first use; later calls are no-ops unless `refresh()` is used. */
  ensureLoaded(): void {
    if (this.requested) return;
    this.requested = true;
    this.refresh().subscribe({ error: () => (this.requested = false) });
  }

  refresh(): Observable<RoleType[]> {
    const params = new HttpParams().set('include_archived', true);
    return this.http.get<RoleType[]>(API_URL, { params }).pipe(tap((roles) => this.all.set(roles)));
  }

  label(code: string): string {
    return this.find(code)?.name ?? code;
  }

  pluralLabel(code: string): string {
    return this.find(code)?.plural_name ?? code;
  }

  create(payload: RoleTypeWrite): Observable<RoleType> {
    return this.http.post<RoleType>(API_URL, payload);
  }

  update(id: number, payload: RoleTypeWrite & { version: number }): Observable<RoleType> {
    return this.http.patch<RoleType>(`${API_URL}/${id}`, payload);
  }

  archive(id: number, version: number): Observable<RoleType> {
    return this.http.delete<RoleType>(`${API_URL}/${id}`, { params: new HttpParams().set('version', version) });
  }

  private find(code: string): RoleType | undefined {
    this.ensureLoaded();
    return this.all().find((role) => role.code === code);
  }
}
