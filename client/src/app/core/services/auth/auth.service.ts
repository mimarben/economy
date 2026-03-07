import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { environment } from '@environments/environment';
import { ApiResponse } from '@core_models/apiResponse';

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
            localStorage.setItem('refresh_token', refreshToken);
          }
          if(tokenType){
            localStorage.setItem('token_type', tokenType);
          }
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
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem('refresh_token');
    this.isLoggedInSubject.next(false);
  }

  hasToken(): boolean {
    return !!localStorage.getItem(this.tokenKey);
  }

  refreshToken(): Observable<ApiResponse<LoginTokens>> {
    const refreshToken = localStorage.getItem('refresh_token');
    
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
             localStorage.setItem('refresh_token', newRefreshToken);
          }
          this.isLoggedInSubject.next(true);
        }
      })
    );
  }
}
