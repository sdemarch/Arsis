import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Page } from '../../core/api/api.types';

const API_URL = '/api/v1';
export interface Section { readonly id:number; readonly name:string; readonly display_order:number; readonly is_active:boolean; readonly archived_at:string|null; readonly version:number; }
export interface Instrument { readonly id:number; readonly name:string; readonly section_id:number; readonly display_order:number; readonly is_active:boolean; readonly archived_at:string|null; readonly version:number; }

@Injectable({providedIn:'root'})
export class CataloguesService {
  constructor(private readonly http:HttpClient) {}
  sections():Observable<Page<Section>> { return this.http.get<Page<Section>>(`${API_URL}/sections`,{params:new HttpParams().set('page_size','100')}); }
  instruments():Observable<Page<Instrument>> { return this.http.get<Page<Instrument>>(`${API_URL}/instruments`,{params:new HttpParams().set('page_size','100')}); }
  addSection(payload:{name:string;display_order:number}):Observable<Section>{return this.http.post<Section>(`${API_URL}/sections`,payload);}
  addInstrument(payload:{name:string;section_id:number;display_order:number}):Observable<Instrument>{return this.http.post<Instrument>(`${API_URL}/instruments`,payload);}
  updateSection(id:number,payload:{name:string;version:number}):Observable<Section>{return this.http.patch<Section>(`${API_URL}/sections/${id}`,payload);}
  updateInstrument(id:number,payload:{name:string;version:number}):Observable<Instrument>{return this.http.patch<Instrument>(`${API_URL}/instruments/${id}`,payload);}
  archiveSection(id:number,version:number):Observable<Section>{return this.http.delete<Section>(`${API_URL}/sections/${id}`,{params:new HttpParams().set('version',version)});}
  archiveInstrument(id:number,version:number):Observable<Instrument>{return this.http.delete<Instrument>(`${API_URL}/instruments/${id}`,{params:new HttpParams().set('version',version)});}
}
