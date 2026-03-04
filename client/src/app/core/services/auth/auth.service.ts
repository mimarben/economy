import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { environment } from '@environments/environment';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user_id: string;
  role: string;
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

  login(credentials: { email: string; password: string }): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, credentials).pipe(
      tap((response) => {
        if (response && response.access_token) {
          localStorage.setItem(this.tokenKey, response.access_token);
          if (response.refresh_token) {
            localStorage.setItem('refresh_token', response.refresh_token);
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
}
