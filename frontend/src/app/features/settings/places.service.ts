import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1';

/** A place activities are held at; km and toll are always round trip. */
export interface Place {
  readonly id: number;
  readonly name: string;
  readonly address: string | null;
  readonly distance_km: number;
  readonly highway_cost: string;
  readonly notes: string | null;
  readonly archived_at: string | null;
  readonly version: number;
}

export interface PlaceWrite {
  readonly name?: string;
  readonly address?: string | null;
  readonly distance_km?: number;
  readonly highway_cost?: string;
  readonly notes?: string | null;
  readonly version?: number;
}

@Injectable({ providedIn: 'root' })
export class PlacesService {
  constructor(private readonly http: HttpClient) {}

  list(includeArchived = false): Observable<Place[]> {
    const params = new HttpParams().set('page_size', '100').set('include_archived', includeArchived);
    return this.http.get<Page<Place>>(`${API_URL}/places`, { params }).pipe(map((page) => page.items));
  }

  create(payload: PlaceWrite): Observable<Place> {
    return this.http.post<Place>(`${API_URL}/places`, payload);
  }

  update(id: number, payload: PlaceWrite & { version: number }): Observable<Place> {
    return this.http.patch<Place>(`${API_URL}/places/${id}`, payload);
  }

  archive(id: number, version: number): Observable<Place> {
    return this.http.delete<Place>(`${API_URL}/places/${id}`, { params: new HttpParams().set('version', version) });
  }
}

export function placeLabel(place: { name: string; distance_km: number; highway_cost: string }): string {
  const toll = Number(place.highway_cost);
  const tollText = toll > 0 ? ` · pedaggio ${new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(toll)}` : '';
  return `${place.name} · ${place.distance_km} km A/R${tollText}`;
}
