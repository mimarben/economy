/**
 * HTTP Interceptor for centralized request/response handling
 * Handles:
 * - Adding authorization headers
 * - Global request/response logging
 * - Error handling
 * - Request/response transformation
 */

import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpResponse,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@environments/environment';

@Injectable()
export class HttpInterceptorService implements HttpInterceptor {
  constructor(private toastService: ToastService) {}

  /**
   * Intercept all HTTP requests
   */
  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    // Add default headers to all requests
    const modifiedRequest = this.addHeaders(request);

    // Log request in development
    if (!environment.production) {
      this.logRequest(modifiedRequest);
    }

    // Handle request and errors
    return next.handle(modifiedRequest).pipe(
      // Log successful responses
      tap((event) => {
        if (event instanceof HttpResponse) {
          if (!environment.production) {
            this.logResponse(event);
          }
        }
      }),
      // Handle errors globally
      catchError((error: HttpErrorResponse) => {
        this.handleError(error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Add headers to request
   */
  private addHeaders(request: HttpRequest<unknown>): HttpRequest<unknown> {
    let headers = request.headers;

    // Add Content-Type if not already set and it's a POST/PATCH request
    if (!headers.has('Content-Type') && ['POST', 'PATCH'].includes(request.method)) {
      headers = headers.set('Content-Type', 'application/json');
    }

    // Add Authorization header if token exists
    const token = this.getAuthToken();
    if (token && !request.url.includes('assets')) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }

    return request.clone({ headers });
  }

  /**
   * Get auth token from localStorage
   */
  private getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  /**
   * Log request details in development
   */
  private logRequest(request: HttpRequest<unknown>): void {
    console.log('%c[HTTP REQUEST]', 'color: blue; font-weight: bold', {
      method: request.method,
      url: request.url,
      headers: request.headers,
      body: request.body,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Log response details in development
   */
  private logResponse(response: HttpResponse<unknown>): void {
    console.log('%c[HTTP RESPONSE]', 'color: green; font-weight: bold', {
      status: response.status,
      url: response.url,
      body: response.body,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): void {
    let errorMessage = 'An unexpected error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.error?.message) {
        errorMessage = error.error.message;
      } else if (error.error?.detail) {
        errorMessage = error.error.detail;
      } else {
        switch (error.status) {
          case 0:
            errorMessage = 'Network error: unable to connect to server';
            break;
          case 400:
            errorMessage = 'Bad request: please check your input';
            break;
          case 401:
            errorMessage = 'Unauthorized: please log in again';
            this.handleUnauthorized();
            break;
          case 403:
            errorMessage = 'Forbidden: you do not have permission';
            break;
          case 404:
            errorMessage = 'Not found: the requested resource does not exist';
            break;
          case 409:
            errorMessage = 'Conflict: this item already exists';
            break;
          case 422:
            errorMessage = 'Validation error: please check your input';
            break;
          case 500:
            errorMessage = 'Server error: please try again later';
            break;
          case 503:
            errorMessage = 'Service unavailable: please try again later';
            break;
          default:
            errorMessage = `Error ${error.status}: ${error.statusText}`;
        }
      }
    }

    // Log in development
    if (!environment.production) {
      console.error('%c[HTTP ERROR]', 'color: red; font-weight: bold', {
        status: error.status,
        statusText: error.statusText,
        message: errorMessage,
        url: error.url,
        error: error.error,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * Handle 401 Unauthorized
   * Can redirect to login or refresh token
   */
  private handleUnauthorized(): void {
    // Clear auth token
    localStorage.removeItem('auth_token');
    // Could redirect to login page here
    // this.router.navigate(['/login']);
  }
}
