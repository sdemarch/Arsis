import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, forkJoin, map, switchMap } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = 'http://localhost:8000/api/v1';

export interface Person {
  readonly id: number;
  readonly first_name: string;
  readonly last_name: string;
  readonly email: string | null;
  readonly phone: string | null;
  readonly updated_at: string;
  readonly archived_at: string | null;
}

export interface PersonDetail extends Person {
  readonly birth_date: string | null;
  readonly birth_place: string | null;
  readonly tax_code: string | null;
  readonly residence_address: string | null;
  readonly notes: string | null;
  readonly version: number;
}

export interface PersonCreate {
  readonly first_name: string;
  readonly last_name: string;
  readonly email?: string | null;
  readonly phone?: string | null;
  readonly notes?: string | null;
}

export interface PersonRole {
  readonly role_type: string;
}

export interface PersonListItem extends Person {
  readonly roles: string[];
}

@Injectable({ providedIn: 'root' })
export class PeopleService {
  constructor(private readonly http: HttpClient) {}

  listPeople(query: string): Observable<Page<PersonListItem>> {
    let params = new HttpParams().set('page_size', '100').set('include_archived', 'true');
    if (query.trim()) params = params.set('q', query.trim());

    return this.http.get<Page<Person>>(`${API_URL}/people`, { params }).pipe(
      switchMap((page) =>
        forkJoin(
          page.items.map((person) =>
            this.http
              .get<PersonRole[]>(`${API_URL}/people/${person.id}/roles`)
              .pipe(map((roles) => ({ ...person, roles: roles.map((role) => role.role_type) }))),
          ),
        ).pipe(map((items) => ({ ...page, items }))),
      ),
    );
  }

  getPerson(personId: number): Observable<PersonDetail> {
    return this.http.get<PersonDetail>(`${API_URL}/people/${personId}`);
  }

  listRoles(personId: number): Observable<PersonRole[]> {
    return this.http.get<PersonRole[]>(`${API_URL}/people/${personId}/roles`);
  }

  createPerson(payload: PersonCreate): Observable<PersonDetail> {
    return this.http.post<PersonDetail>(`${API_URL}/people`, payload);
  }
}
