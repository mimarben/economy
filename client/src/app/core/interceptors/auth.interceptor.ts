import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { AuthService } from '@auth_services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  
  const isAuthRequest = req.url.includes('/auth/login') || req.url.includes('/auth/refresh');
  const hasAuthorizationHeader = req.headers.has('Authorization');

  if (authService.hasToken() && !req.url.includes('assets') && !isAuthRequest && !hasAuthorizationHeader) {
    const token = localStorage.getItem('auth_token');
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    return next(authReq);
  }
  
  return next(req);
};
