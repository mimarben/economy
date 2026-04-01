import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { environment } from '@env/environment';
import { ApiResponse } from '@app/models/core/APIResponse';

interface LoginTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = environment.apiUrl;
  private readonly tokenKey = 'auth_token';
  private readonly refreshTokenKey = 'refresh_token';
  private readonly tokenTypeKey = 'token_type';
  private readonly lastActivityKey = 'auth_last_activity';
  private readonly idleTimeoutMs = 7 * 24 * 60 * 60 * 1000; // 7 days matching typical refresh token
  private readonly minActivityWriteIntervalMs = 30 * 1000;
  private lastActivityWriteAt = 0;

  // Observable to track login state
  private isLoggedInSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isLoggedIn$ = this.isLoggedInSubject.asObservable();

  constructor(private http: HttpClient) {}

  login(credentials: { email: string; password: string }): Observable<ApiResponse<LoginTokens>> {
    return this.http.post<ApiResponse<LoginTokens>>(`${this.apiUrl}/auth/login`, credentials).pipe(
      tap((res) => {
        const accessToken= res.response.access_token;
        const refreshToken= res.response.refresh_token;
        const tokenType= res.response.token_type;
        if (accessToken) {
          localStorage.setItem(this.tokenKey, accessToken);
          if (refreshToken) {
            localStorage.setItem(this.refreshTokenKey, refreshToken);
          }
          if(tokenType){
            localStorage.setItem(this.tokenTypeKey, tokenType);
          }
          this.updateLastActivity(true);
          this.isLoggedInSubject.next(true);
        }
      }),
      catchError((error) => {
        console.error('Login failed', error);
        return throwError(() => new Error('Login failed. Please check your credentials.'));
      })
    );
  }

  logout(): void {
    this.clearSessionTokens();
    this.isLoggedInSubject.next(false);
  }

  hasToken(): boolean {
    const hasAccessToken = !!localStorage.getItem(this.tokenKey);
    if (!hasAccessToken) {
      return false;
    }

    if (this.isSessionExpiredByInactivity()) {
      this.clearSessionTokens();
      this.isLoggedInSubject.next(false);
      return false;
    }

    return true;
  }

  registerUserActivity(): void {
    if (!localStorage.getItem(this.tokenKey)) {
      return;
    }
    this.updateLastActivity();
  }

  isSessionExpiredByInactivity(): boolean {
    const lastActivity = localStorage.getItem(this.lastActivityKey);
    if (!lastActivity) {
      return false;
    }

    const lastActivityTs = Number(lastActivity);
    if (!Number.isFinite(lastActivityTs)) {
      return false;
    }

    return Date.now() - lastActivityTs >= this.idleTimeoutMs;
  }

  refreshToken(): Observable<ApiResponse<LoginTokens>> {
    if (this.isSessionExpiredByInactivity()) {
      this.clearSessionTokens();
      this.isLoggedInSubject.next(false);
      return throwError(() => new Error('Session expired by inactivity'));
    }

    const refreshToken = localStorage.getItem(this.refreshTokenKey);
    
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${refreshToken}`
    });

    return this.http.post<ApiResponse<LoginTokens>>(`${this.apiUrl}/auth/refresh`, {}, { headers }).pipe(
      tap((res) => {
        const accessToken = res.response?.access_token;
        const newRefreshToken = res.response?.refresh_token;
        
        if (accessToken) {
          localStorage.setItem(this.tokenKey, accessToken);
          if (newRefreshToken) {
             localStorage.setItem(this.refreshTokenKey, newRefreshToken);
          }
          this.updateLastActivity(true);
          this.isLoggedInSubject.next(true);
        }
      })
    );
  }

  private updateLastActivity(forceWrite = false): void {
    const now = Date.now();
    if (!forceWrite && now - this.lastActivityWriteAt < this.minActivityWriteIntervalMs) {
      return;
    }

    localStorage.setItem(this.lastActivityKey, String(now));
    this.lastActivityWriteAt = now;
  }

  private clearSessionTokens(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.tokenTypeKey);
    localStorage.removeItem(this.lastActivityKey);
  }
}
