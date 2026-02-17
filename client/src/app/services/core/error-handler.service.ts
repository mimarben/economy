/**
 * Global Error Handler Service
 * Centralized error handling for HTTP requests and business logic
 */

import { Injectable, ErrorHandler, Injector } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@environments/environment';

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  statusCode?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ErrorHandlerService implements ErrorHandler {
  constructor(private injector: Injector) {}

  /**
   * Global error handler - catches all unhandled errors
   */
  handleError(error: Error | HttpErrorResponse): void {
    const apiError = this.parseError(error);
    this.logError(apiError);
    this.showUserNotification(apiError);
  }

  /**
   * Parse error into standardized format
   */
  private parseError(error: Error | HttpErrorResponse): ApiError {
    if (error instanceof HttpErrorResponse) {
      return this.parseHttpError(error);
    }
    return this.parseClientError(error);
  }

  /**
   * Parse HTTP errors (from backend)
   */
  private parseHttpError(error: HttpErrorResponse): ApiError {
    const statusCode = error.status;
    let code = 'HTTP_ERROR';
    let message = 'An unexpected error occurred';

    // Parse backend error response
    if (error.error instanceof Object) {
      code = error.error.code || `HTTP_${statusCode}`;
      message = error.error.message || error.error.detail || error.statusText;
    }

    return {
      code,
      message,
      statusCode,
      details: error.error,
    };
  }

  /**
   * Parse client-side errors
   */
  private parseClientError(error: Error): ApiError {
    return {
      code: 'CLIENT_ERROR',
      message: error.message || 'An unexpected client error occurred',
      details: { stack: error.stack },
    };
  }

  /**
   * Log error to console in development
   */
  private logError(error: ApiError): void {
    if (!environment.production) {
      console.error('[ERROR]', {
        code: error.code,
        message: error.message,
        details: error.details,
        statusCode: error.statusCode,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * Show user-friendly notification
   */
  private showUserNotification(error: ApiError): void {
    const toastService = this.injector.get(ToastService);
    const userMessage = this.getUserFriendlyMessage(error);
    toastService.error(userMessage);
  }

  /**
   * Convert error codes to user-friendly messages
   */
  private getUserFriendlyMessage(error: ApiError): string {
    const messageMap: Record<string, string> = {
      'HTTP_400': 'Please check your input and try again',
      'HTTP_401': 'You are not authorized to perform this action',
      'HTTP_403': 'Access denied',
      'HTTP_404': 'The requested item was not found',
      'HTTP_409': 'This item already exists',
      'HTTP_422': 'Validation error: please check your input',
      'HTTP_500': 'Server error: please try again later',
      'HTTP_503': 'Service unavailable: please try again later',
      'VALIDATION_ERROR': 'Please check your input and try again',
      'NETWORK_ERROR': 'Network connection error: please check your connection',
      'CLIENT_ERROR': 'An unexpected error occurred',
    };

    return messageMap[error.code] || error.message || 'An unexpected error occurred';
  }

  /**
   * Formatted error for debugging
   */
  getFormattedError(error: ApiError): string {
    return `[${error.code}] ${error.message}${
      error.statusCode ? ` (${error.statusCode})` : ''
    }`;
  }
}
