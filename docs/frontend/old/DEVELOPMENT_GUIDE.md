# 📖 Development Guide - Frontend Architecture

## Quick Start

### Understanding the Service Layer

Every service in the economy app follows the same pattern:

```typescript
/**
 * [Entity] Service - Extends BaseCrudService following ISP pattern
 * Provides CRUD operations for [Entity] entities
 */

import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { [EntityBase] as [Entity] } from '@models/[EntityBase]';

@Injectable({
  providedIn: 'root'
})
export class [Entity]Service extends BaseCrudService<[Entity]> {
  constructor(protected override http: HttpClient) {
    super(http, '[api_endpoint]');
  }
  
  // Optional: Add custom methods here
  // getAllActive(): Observable<ApiResponse<[Entity][]>> {
  //   return this.http.get<ApiResponse<[Entity][]>>(`${this.apiUrl}/active`);
  // }
}
```

---

## 🎯 Service Usage Pattern

### Read Operations
```typescript
// Get all items
this.userService.getAll()
  .subscribe({
    next: (response: ApiResponse<User[]>) => {
      this.users = response.data;
    },
    error: (error) => {
      // Auto-handled by ErrorHandlerService
    }
  });

// Get single item
this.userService.getById(userId)
  .subscribe({
    next: (response: ApiResponse<User>) => {
      this.user = response.data;
    }
  });
```

### Create Operations
```typescript
const newUser: User = {
  name: 'John',
  email: 'john@example.com'
};

this.userService.create(newUser)
  .subscribe({
    next: (response: ApiResponse<User>) => {
      console.log('User created:', response.data);
    }
  });
```

### Update Operations
```typescript
const updatedUser: User = {
  ...this.user,
  name: 'Jane'
};

this.userService.update(userId, updatedUser)
  .subscribe({
    next: (response: ApiResponse<User>) => {
      console.log('User updated:', response.data);
    }
  });
```

### Delete Operations
```typescript
this.userService.delete(userId)
  .subscribe({
    next: (response: ApiResponse<any>) => {
      console.log('User deleted');
    }
  });
```

---

## 🔧 Creating a New Service

### Step 1: Create the Service File
```typescript
// src/app/services/new-entity.service.ts

import { Injectable } from '@angular/core';
import { BaseCrudService } from './base-crud.service';
import { HttpClient } from '@angular/common/http';
import { NewEntityBase as NewEntity } from '@models/NewEntityBase';

@Injectable({
  providedIn: 'root'
})
export class NewEntityService extends BaseCrudService<NewEntity> {
  constructor(protected override http: HttpClient) {
    super(http, 'new_entities');
  }
}
```

### Step 2: Create the Service Test
```typescript
// src/app/services/new-entity.service.spec.ts

import { TestBed } from '@angular/core/testing';
import { NewEntityService } from './new-entity.service';

describe('NewEntityService', () => {
  let service: NewEntityService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NewEntityService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should provide getAll method', () => {
    expect(service.getAll).toBeDefined();
  });
});
```

### Step 3: Use in Components
```typescript
import { Component, OnInit } from '@angular/core';
import { NewEntityService } from '@services/new-entity.service';

@Component({
  selector: 'app-new-entity',
  template: `...`
})
export class NewEntityComponent implements OnInit {
  entities$ = this.newEntityService.getAll();

  constructor(private newEntityService: NewEntityService) {}

  ngOnInit() {
    // Data loaded via async pipe in template
  }
}
```

---

## 🌐 HTTP Interceptor Details

### Automatic Behavior

The `HttpInterceptorService` automatically:

1. **Adds Headers**
   ```typescript
   // For All Requests
   Content-Type: application/json
   
   // For Authenticated Requests
   Authorization: Bearer [token_from_localStorage]
   ```

2. **Logs Requests** (Development only)
   ```
   [APP] HTTP Request: GET /api/users
   [APP] Headers: { Authorization: Bearer ... }
   ```

3. **Logs Responses** (Development only)
   ```
   [APP] HTTP Response: 200 OK
   [APP] Response Time: 234ms
   ```

4. **Handles Errors**
   - Delegates to `ErrorHandlerService`
   - Shows user-friendly toast notifications
   - Logs errors to console (development)

### Setting/Getting Auth Token

```typescript
// Set token (typically in login)
localStorage.setItem('auth_token', 'your_jwt_token_here');

// Token is automatically injected in all requests
// No need to manually add it to headers!

// Clear token (typically in logout)
localStorage.removeItem('auth_token');
```

---

## 🚨 Error Handler Details

### Error Mapping

The `ErrorHandlerService` automatically maps HTTP status codes:

| Status | Message | Action |
|--------|---------|--------|
| 400 | "Please check your input" | Show validation errors |
| 401 | "You are not authorized" | Redirect to login |
| 403 | "Access denied" | Show permission error |
| 404 | "Requested item not found" | Show not found |
| 409 | "Item already exists" | Show conflict error |
| 422 | "Validation error" | Show field errors |
| 500 | "Server error" | Show server error |
| 503 | "Service unavailable" | Show maintenance message |

### Error Handling in Components

```typescript
// Errors are auto-handled by ErrorHandlerService
// But you can still add custom logic:

this.userService.create(user).subscribe({
  next: (response) => {
    // Success handling
  },
  error: (error) => {
    // Custom error handling (in addition to auto-handling)
    if (error.status === 409) {
      // Custom logic for duplicate item
    }
  }
});
```

### Custom Error Handler

```typescript
// Extend ErrorHandlerService for custom behavior
import { ErrorHandlerService } from '@services/error-handler.service';

@Injectable({
  providedIn: 'root'
})
export class CustomErrorHandler extends ErrorHandlerService {
  override handleError(error: Error): void {
    // Custom logging
    console.custom('Custom error:', error);
    
    // Call parent implementation
    super.handleError(error);
  }
}
```

---

## 🏗️ Adding Custom Methods to Services

### Extend Within Service
```typescript
@Injectable({
  providedIn: 'root'
})
export class UserService extends BaseCrudService<User> {
  constructor(protected override http: HttpClient) {
    super(http, 'users');
  }

  // Add custom method
  getUsersByRole(role: string): Observable<ApiResponse<User[]>> {
    return this.http.get<ApiResponse<User[]>>(
      `${this.apiUrl}/by-role/${role}`
    );
  }

  // Override if needed
  override getAll(): Observable<ApiResponse<User[]>> {
    return super.getAll().pipe(
      tap(response => console.log('Users loaded:', response.data))
    );
  }
}
```

### Using Custom Methods
```typescript
// Standard inherited methods
this.userService.getAll().subscribe(...);
this.userService.getById(id).subscribe(...);

// Custom methods
this.userService.getUsersByRole('admin').subscribe(users => {
  this.admins = users.data;
});
```

---

## 📱 Reactive Pattern with Async Pipe

### Template
```html
<!-- Load data and let Angular handle subscription/cleanup -->
<div *ngIf="users$ | async as users">
  <div *ngFor="let user of users">
    {{ user.name }}
  </div>
</div>
```

### Component
```typescript
export class UsersComponent {
  // Observable directly from service
  users$: Observable<ApiResponse<User[]>> = 
    this.userService.getAll();

  constructor(private userService: UserService) {}
}
```

**Benefits**:
- ✅ Automatic subscription/unsubscription
- ✅ Better memory management
- ✅ Less boilerplate code
- ✅ Better change detection

---

## 🧩 Common Component Patterns

### Page Component (List View)
```typescript
@Component({
  selector: 'app-users',
  template: `
    <div *ngIf="(users$ | async) as response">
      <div *ngFor="let user of response.data">
        {{ user.name }}
      </div>
    </div>
  `
})
export class UsersComponent {
  users$ = this.userService.getAll();

  constructor(
    private userService: UserService
  ) {}
}
```

### Form Component (Create/Edit)
```typescript
@Component({
  selector: 'app-user-form'
})
export class UserFormComponent {
  form = this.FB.group({
    name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]]
  });

  onSubmit() {
    if (this.form.valid) {
      const newUser = this.form.value;
      this.userService.create(newUser).subscribe({
        next: (response) => {
          // Navigate or show success
        }
      });
    }
  }

  constructor(
    private userService: UserService,
    private FB: FormBuilder
  ) {}
}
```

### Detail Component (View/Edit)
```typescript
@Component({
  selector: 'app-user-detail'
})
export class UserDetailComponent implements OnInit {
  user$!: Observable<ApiResponse<User>>;

  constructor(
    private userService: UserService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    this.user$ = this.userService.getById(Number(id));
  }
}
```

---

## 🔍 Debugging Tips

### Enable Request/Response Logging

The interceptor automatically logs in development. Check browser console:

```
[APP] HTTP Request: POST /api/users
[APP] Headers: { Authorization: Bearer ..., Content-Type: application/json }
[APP] Method: POST
[APP] URL: http://localhost:4200/api/users

[APP] HTTP Response: 201 Created
[APP] Response Time: 145ms
[APP] Status: 201
```

### Check Auth Token

```typescript
// In browser console
localStorage.getItem('auth_token')
```

### Inspect Service Methods

```typescript
// In component or browser console
this.userService.getAll()
// Returns: Observable<ApiResponse<User[]>>
```

### Test Error Scenarios

```typescript
// Simulate 401 error
this.http.get('/api/protected').subscribe({
  error: (err) => {
    // Will be caught by ErrorHandlerService
    // And show "You are not authorized"
  }
});
```

---

## 📋 Checklist for New Feature

When adding a new entity/feature:

- [ ] Create `[Entity]Base` model in `models/`
- [ ] Create API schema in `schemas/`
- [ ] Create `[Entity]Service` extends `BaseCrudService`
- [ ] Create list component using `getAll()`
- [ ] Create detail component using `getById()`
- [ ] Create form component using `create()` and `update()`
- [ ] Add routing for list/detail/form pages
- [ ] Test CRUD operations in component
- [ ] Verify error handling with invalid data
- [ ] Document custom methods in service

---

## 🚀 Performance Tips

### 1. Use Async Pipe
```typescript
// ✅ Good
template: 'users$ | async'

// ❌ Bad
ngOnInit() {
  this.userService.getAll().subscribe(r => this.users = r.data);
}
```

### 2. Use RxJS Operators
```typescript
// ✅ Good - Only load when component is visible
users$ = this.userService.getAll().pipe(
  shareReplay(1),  // Cache result
  takeUntil(this.destroy$)  // Unsubscribe on destroy
);

// ❌ Bad - Multiple subscriptions
getUsers() {
  return this.userService.getAll();
}
```

### 3. Implement OnDestroy for Manual Subscriptions
```typescript
export class MyComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.userService.getAll()
      .pipe(takeUntil(this.destroy$))
      .subscribe(r => this.users = r.data);
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

---

## 📚 File Structure

```
src/app/
├── services/
│   ├── interfaces.ts                 # ISP interfaces
│   ├── base-crud.service.ts          # Generic CRUD implementation
│   ├── error-handler.service.ts      # Global error handling
│   ├── http.interceptor.ts           # HTTP interception
│   ├── user.service.ts               # User CRUD
│   ├── account.service.ts            # Account CRUD
│   ├── expense.service.ts            # Expense CRUD
│   └── [13+ other services]
├── models/
│   ├── UserBase.ts
│   ├── AccountBase.ts
│   └── [20+ other models]
├── schemas/
│   ├── user.schema.ts
│   ├── account.schema.ts
│   └── [20+ other schemas]
└── components/
    ├── user/
    ├── account/
    ├── expense/
    └── [other components]
```

---

## 🤔 FAQ

**Q: Do I have to use async pipe?**
A: No, but it's recommended for better memory management.

**Q: Can I add authentication headers manually?**
A: No need - the interceptor adds them automatically from localStorage.

**Q: What if API doesn't follow ApiResponse format?**
A: Modify `http.interceptor.ts` or transform in the service using `map()`.

**Q: How do I handle real-time updates?**
A: Consider WebSockets or polling - extend the service with a subscription-based method.

**Q: Can I add state management?**
A: Yes! Consider NgRx or Akita for complex state - services remain unchanged.

---

**Version**: 1.0.0  
**Last Updated**: $(date)  
**Audience**: Frontend developers  
**Status**: ✅ Ready for use
