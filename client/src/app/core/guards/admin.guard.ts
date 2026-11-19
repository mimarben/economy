import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '@auth_services/auth.service';

/**
 * Allows navigation only for administrators.
 * Non-admins (or unauthenticated visitors) are sent home; the layout's
 * authGuard then redirects to login when there is no session at all.
 */
export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.hasToken() && authService.isAdmin()) {
    return true;
  }

  return router.createUrlTree(['/']);
};
