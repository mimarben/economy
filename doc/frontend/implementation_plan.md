# Economy App Client Implementation Plan

## Goal Description
Refactor the Angular application to follow the documented architectural rules, implement a secure login system with JWT interceptors/guards, and update the application's look and feel to match the "Material Dashboard" visual reference provided (Creative Tim style).

## User Review Required
> [!IMPORTANT]
> The architectural refactoring requires moving many files. I will use a combination of `mv` and script-based import rewriting to group everything under `core`, `shared`, and `features`. Please confirm if you are ok with these heavy directory structure changes.

> [!NOTE]
> For the visual update, I will replicate the "Material Dashboard" design using pure Angular Material components and custom SCSS (floating headers on cards, specific color palettes, sidebar layout).

## Proposed Changes

### 1. Architecture Refactor
Align with the folder structure defined in Rule 11.
- Move `src/app/services` -> `src/app/core/services`
- Move `src/app/components/shared` -> `src/app/shared/components`
- Move `src/app/components/pages/*` -> `src/app/features/*` (e.g., `expenses`, `incomes`, `investments`, `banks` -> `accounts`)
- Move layout components -> `src/app/core/layout` (or keep in `features/layout`)
- Update imports across all [.ts](file:///home/martinm/src/economy/client/src/app/app.routes.ts) and `.scss` files.

### 2. Security Layer
- #### [NEW] `src/app/core/guards/auth.guard.ts`
  Implement an Angular functional `CanActivateFn` guard that checks if a user is logged in (via Auth/Token Service).
- #### [NEW] `src/app/core/interceptors/auth.interceptor.ts`
  Implement an Angular `HttpInterceptorFn` that attaches the `Authorization: Bearer <token>` header to all outgoing API requests.
- #### [NEW] `src/app/core/services/auth.service.ts`
  A service to handle login/logout API calls and token storage (localStorage or session).

### 3. Login Feature
- #### [NEW] `src/app/features/auth/login/login.component.ts|html|css`
  Create a Login page using Angular Material (`mat-card`, `mat-form-field`, `mat-input`, `mat-button`).
- Update [src/app/app.routes.ts](file:///home/martinm/src/economy/client/src/app/app.routes.ts) to include `/login` and protect other routes with `authGuard`.

### 4. Look and Feel (Material Dashboard)
Refactor UI to match [lookandfeel.png](file:///home/martinm/src/economy/.agent/rules/lookandfeel.png).
- **Layout**: Update `side-menu` and `header` to have the specific dark sidebar with active red highlights, and top navigation bar.
- **Global Styles**: Modify `src/styles.scss` to use the grey background (`#eeeeee`), update typography (Roboto), and define CSS variables for the Material Dashboard colors (Red, Orange, Green, Purple).
- **Cards**: Create a generic style or update `generic-form`/`summary-component` to use the "floating colored header" card style seen in the image.

## Verification Plan

### Automated Tests
- Run `npm run build` to ensure the application compiles successfully without import errors after the massive refactor.

### Manual Verification
- Verify the router correctly redirects unauthenticated users to `/login`.
- Verify the login page allows authentication and saves the token.
- Visually inspect the `dashboard` and `expenses` routes to confirm the new layout (sidebar, floating card headers, colors) matches the [lookandfeel.png](file:///home/martinm/src/economy/.agent/rules/lookandfeel.png) reference.
