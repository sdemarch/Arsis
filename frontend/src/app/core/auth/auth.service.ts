import { HttpClient } from '@angular/common/http';
import { Injectable, computed, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

const API_URL = 'http://localhost:8000/api/v1';

export interface AuthUser {
  readonly id: number;
  readonly email: string;
  readonly display_name: string;
  readonly role: 'responsible';
  readonly last_login_at: string | null;
  readonly version: number;
}

interface TokenResponse {
  readonly access_token: string;
  readonly token_type: 'bearer';
  readonly expires_in: number;
  readonly user: AuthUser;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly accessToken = signal<string | null>(null);
  readonly user = signal<AuthUser | null>(null);
  readonly isAuthenticated = computed(() => this.accessToken() !== null && this.user() !== null);

  constructor(private readonly http: HttpClient) {}

  login(email: string, password: string): Observable<TokenResponse> {
    return this.http
      .post<TokenResponse>(`${API_URL}/auth/login`, { email, password }, { withCredentials: true })
      .pipe(tap((response) => this.setSession(response)));
  }

  refresh(): Observable<TokenResponse> {
    return this.http
      .post<TokenResponse>(`${API_URL}/auth/refresh`, {}, { withCredentials: true })
      .pipe(tap((response) => this.setSession(response)));
  }

  logout(): Observable<void> {
    return this.http
      .post<void>(`${API_URL}/auth/logout`, {}, { withCredentials: true })
      .pipe(tap(() => this.clearSession()));
  }

  token(): string | null {
    return this.accessToken();
  }

  clearSession(): void {
    this.accessToken.set(null);
    this.user.set(null);
  }

  private setSession(response: TokenResponse): void {
    this.accessToken.set(response.access_token);
    this.user.set(response.user);
  }
}
