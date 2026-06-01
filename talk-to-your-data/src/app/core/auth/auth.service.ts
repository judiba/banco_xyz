import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, catchError, map, tap, throwError } from 'rxjs';
import { ApiConfig } from '../api/api-config.service';
import {
  AuthTokens,
  BootstrapResponse,
  LoginResponse,
  User,
} from '../api/api.types';
import { SessionApiService } from '../api/session-api.service';

const ACCESS_TOKEN_KEY = 'ttyd_access_token';
const REFRESH_TOKEN_KEY = 'ttyd_refresh_token';
const USER_KEY = 'ttyd_user';
const ASSISTANT_NAME_KEY = 'ttyd_assistant_name';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiConfig);
  private readonly router = inject(Router);
  private readonly sessionApi = inject(SessionApiService);

  readonly user = signal<User | null>(this.loadUser());
  readonly assistantDisplayName = signal<string>(
    sessionStorage.getItem(ASSISTANT_NAME_KEY) ?? 'RecordAI',
  );
  readonly isAuthenticated = signal<boolean>(!!this.getAccessToken());

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(this.api.auth.login(), {
        username: username.trim(),
        password,
      })
      .pipe(
        tap((res) => {
          this.persistSession(res.tokens, res.user);
        }),
      );
  }

  refresh(): Observable<AuthTokens> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token'));
    }
    return this.http
      .post<{ tokens: AuthTokens }>(this.api.auth.refresh(), { refreshToken })
      .pipe(
        map((r) => r.tokens),
        tap((tokens) => this.persistTokens(tokens)),
      );
  }

  logout(): Observable<void> {
    const refreshToken = this.getRefreshToken();
    const body = refreshToken ? { refreshToken } : {};
    return this.http.post<void>(this.api.auth.logout(), body).pipe(
      catchError(() => throwError(() => new Error('logout failed'))),
      tap({
        next: () => this.clearSession(),
        error: () => this.clearSession(),
      }),
    );
  }

  logoutAndRedirect(): void {
    this.logout().subscribe({
      complete: () => this.router.navigateByUrl('/'),
      error: () => this.router.navigateByUrl('/'),
    });
  }

  bootstrap(page = 1, pageSize = 50): Observable<BootstrapResponse> {
    return this.sessionApi.getBootstrap(page, pageSize).pipe(
      tap((res) => {
        this.user.set(res.user);
        sessionStorage.setItem(USER_KEY, JSON.stringify(res.user));
        this.assistantDisplayName.set(res.assistant.displayName);
        sessionStorage.setItem(ASSISTANT_NAME_KEY, res.assistant.displayName);
      }),
    );
  }

  getAccessToken(): string | null {
    return sessionStorage.getItem(ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return sessionStorage.getItem(REFRESH_TOKEN_KEY);
  }

  getDisplayName(): string {
    return this.user()?.displayName ?? 'Usuário';
  }

  /** Tokens retornados pelo callback SAML (`/login?token=...&refresh=...`). */
  setTokens(accessToken: string, refreshToken?: string): void {
    this.persistTokens({
      accessToken,
      refreshToken: refreshToken ?? '',
      expiresIn: 3600,
      tokenType: 'Bearer',
    });
  }

  private persistSession(tokens: AuthTokens, user: User): void {
    this.persistTokens(tokens);
    this.user.set(user);
    sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    this.isAuthenticated.set(true);
  }

  private persistTokens(tokens: AuthTokens): void {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken);
    sessionStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
    this.isAuthenticated.set(true);
  }

  clearSession(): void {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
    sessionStorage.removeItem(ASSISTANT_NAME_KEY);
    this.user.set(null);
    this.isAuthenticated.set(false);
  }

  private loadUser(): User | null {
    const raw = sessionStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  }
}
