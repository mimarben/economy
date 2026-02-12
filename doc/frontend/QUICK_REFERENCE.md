# 🎯 Quick Reference Card - Angular Services

## Service Lifecycle

```
              ┌─────────────────────────────┐
              │   Create New Service        │
              └──────────────┬──────────────┘
                             ↓
         ┌──────────────────────────────────────┐
         │ export class [Entity]Service         │
         │   extends BaseCrudService<[Entity]> │
         │ {                                    │
         │   constructor(http: HttpClient) {   │
         │     super(http, '[api_endpoint]')   │
         │   }                                  │
         │ }                                    │
         └──────────────┬───────────────────────┘
                        ↓
         ┌──────────────────────────────────────┐
         │ Service Ready with 5 CRUD Methods   │
         │ - getAll()                           │
         │ - getById(id)                        │
         │ - create(item)                       │
         │ - update(id, item)                   │
         │ - delete(id)                         │
         └──────────────────────────────────────┘
```

---

## 5-Method CRUD Pattern

### Available in Every Service

```typescript
// 1️⃣  READ ALL
service.getAll(): Observable<ApiResponse<T[]>>

// 2️⃣  READ ONE
service.getById(id: number): Observable<ApiResponse<T>>

// 3️⃣  CREATE
service.create(item: T): Observable<ApiResponse<T>>

// 4️⃣  UPDATE
service.update(id: number, item: T): Observable<ApiResponse<T>>

// 5️⃣  DELETE
service.delete(id: number): Observable<ApiResponse<any>>
```

---

## Service Usage Examples

### In Component

```typescript
import { Component } from '@angular/core';
import { UserService } from '@services/user.service';

@Component({
  selector: 'app-users',
  template: `
    <div *ngFor="let user of (users$ | async)?.data">
      {{ user.name }}
    </div>
  `
})
export class UsersComponent {
  // ✅ Observable - No unsubscribe needed
  users$ = this.userService.getAll();

  constructor(private userService: UserService) {}
}
```

---

## HTTP Interceptor - Automatic

```
┌────────────────────────────────────────────┐
│ Every HTTP Request                         │
├────────────────────────────────────────────┤
│ ✅ Auth Header Injected                    │
│    Authorization: Bearer [token]           │
│ ✅ Content-Type Set                        │
│    application/json                        │
│ ✅ Request Logged (Dev Mode)               │
│ ✅ Response Logged (Dev Mode)              │
│ ✅ Errors Caught & Handled                 │
└────────────────────────────────────────────┘
```

**No manual header injection needed!**

---

## Error Handler - Automatic

```
HTTP Error (e.g., 404)
        ↓
ErrorHandlerService.handleError()
        ↓
┌─────────────────────────────────────┐
│ 1. Parse Error Details              │
│ 2. Map Status → User Message        │
│ 3. Show Toast Notification          │
│ 4. Log to Console (Dev)             │
│ 5. Propagate to Component (optional)│
└─────────────────────────────────────┘
        ↓
User sees: "Requested item not found"
Developer sees: Full error in console
```

**Errors are handled automatically!**

---

## Common Error Responses

| Status | Meaning | Auto Message |
|--------|---------|--------------|
| 400 | Bad Request | "Please check your input" |
| 401 | Unauthorized | "You are not authorized" |
| 403 | Forbidden | "Access denied" |
| 404 | Not Found | "Requested item not found" |
| 409 | Conflict | "Item already exists" |
| 422 | Invalid | "Validation error" |
| 500 | Server Error | "Server error" |
| 503 | Unavailable | "Service unavailable" |

---

## Authentication Token

```typescript
// ✅ LOGIN - Save token
localStorage.setItem('auth_token', jwtToken);

// ✅ API CALLS - Token auto-injected
this.userService.getAll().subscribe(...);  // Token included!

// ✅ LOGOUT - Remove token
localStorage.removeItem('auth_token');
```

**💡 Token automatically in every request after login!**

---

## 15 Available Services

```
Financial          Categories         Transactions        Household
┌─────────────┐   ┌──────────────┐   ┌───────────────┐  ┌──────────────┐
│ Account     │   │ Expense Cat  │   │ Expense       │  │ Household    │
│ Bank        │   │ Income Cat   │   │ Income        │  │ HHold Member │
│ Source      │   │ Investment C │   │ Saving Log    │  └──────────────┘
└─────────────┘   └──────────────┘   │ Investment Log│
                                      │ Saving        │
                                      │ Investment    │
                                      └───────────────┘
```

**All 15 services work the same way!**

---

## Creating New Services (3 Steps)

### Step 1: Service File
```typescript
// src/app/services/new-entity.service.ts
@Injectable({ providedIn: 'root' })
export class NewEntityService extends BaseCrudService<NewEntity> {
  constructor(protected override http: HttpClient) {
    super(http, 'new_endpoint');
  }
}
```

### Step 2: Import in Component
```typescript
constructor(private newEntityService: NewEntityService) {}
```

### Step 3: Use CRUD Methods
```typescript
this.newEntityService.getAll().subscribe(response => {
  this.items = response.data;
});
```

**✅ Done! Service ready to use!**

---

## Common Patterns

### Load All Items
```typescript
// Component
items$ = this.itemService.getAll();

// Template
<div *ngFor="let item of (items$ | async)?.data">
  {{ item.name }}
</div>
```

### Load Single Item
```typescript
item$ = this.itemService.getById(this.id);

<div *ngIf="(item$ | async) as response">
  {{ response.data.name }}
</div>
```

### Create Item
```typescript
this.itemService.create(newItem).subscribe({
  next: (response) => console.log('Created:', response.data),
  error: (err) => { /* Auto-handled by ErrorHandler */ }
});
```

### Update Item
```typescript
this.itemService.update(id, updatedItem).subscribe({
  next: (response) => console.log('Updated:', response.data)
});
```

### Delete Item
```typescript
this.itemService.delete(id).subscribe({
  next: () => console.log('Deleted')
});
```

---

## Async Pipe Benefits

```typescript
// ✅ GOOD - Using async pipe
users$ = this.userService.getAll();
Template: *ngFor="let u of (users$ | async)?.data"

Benefits:
✓ Auto unsubscribe on destroy
✓ No manual subscription
✓ Less boilerplate
✓ Better memory management
```

```typescript
// ❌ BAD - Manual subscription
users: User[] = [];
ngOnInit() {
  this.userService.getAll().subscribe(r => {
    this.users = r.data;
  });
}

Problems:
✗ Must manually unsubscribe
✗ Memory leak risk
✗ More code
✗ Manual cleanup needed
```

---

## Response Structure

```typescript
// All API responses follow this structure:
export interface ApiResponse<T> {
  success: boolean;
  status: number;
  message: string;
  data: T;         // ← Your actual data
}

// Usage:
this.userService.getAll().subscribe(response => {
  console.log(response.success);    // true
  console.log(response.status);     // 200
  console.log(response.message);    // "OK"
  console.log(response.data);       // User[] ← actual data
});

// With async pipe:
<div *ngIf="(users$ | async) as response">
  <div *ngFor="let user of response.data">
    {{ user.name }}
  </div>
</div>
```

---

## ISP Pattern (Why It Matters)

```
Before: All services had ALL methods (created/get/update/delete)
Problem: Code duplication, maintenance nightmare

After: BaseCrudService provides all, services just extend
Benefit: DRY principle, single source of truth, less bugs
```

---

## File Structure Reference

```
src/app/
├── services/
│   ├── interfaces.ts                 ← ISP Interfaces
│   ├── base-crud.service.ts          ← Generic CRUD
│   ├── error-handler.service.ts      ← Error Handling
│   ├── http.interceptor.ts           ← HTTP Intercept
│   ├── user.service.ts               ← 15 Services...
│   ├── account.service.ts
│   ├── expense.service.ts
│   └── ...
├── models/
│   ├── UserBase.ts
│   └── [Entity]Base.ts
├── components/
│   ├── user/
│   ├── account/
│   └── [entity]/
└── app.config.ts                     ← Global Config
```

---

## Debugging Checklist

```
Issue: "Service method not found"
□ Check service extends BaseCrudService
□ Verify correct method name (getAll not getUsers)

Issue: "Token not sent with request"
□ Check localStorage has auth_token key
□ Verify token format: "Bearer [token]"

Issue: "Error not showing to user"
□ Check ErrorHandlerService registered in app.config.ts
□ Verify status code maps to a message

Issue: "Components still subscribed after destroy"
□ Use async pipe instead of manual subscribe
□ Or use takeUntil(destroy$) pattern

Issue: "Service not injected"
□ Verify @Injectable({ providedIn: 'root' })
□ Check service imported in component
□ Verify dependency injection syntax
```

---

## Performance Tips

```
✅ DO
   • Use async pipe in templates
   • Use shareReplay(1) for multiple subscribers
   • Unsubscribe from manual subscriptions
   • Lazy load feature modules
   
❌ DON'T
   • Subscribe multiple times for same data
   • Forget to unsubscribe on destroy
   • Use real-time APIs for all data
   • Create services outside of root
```

---

## TypeScript Generics

```typescript
BaseCrudService<User>           // Service for User entity
BaseCrudService<Account>        // Service for Account entity
BaseCrudService<Expense>        // Service for Expense entity

// Generic = type-safe, reusable, one implementation
// Result = no duplicate code
```

---

## Status Codes Reference

```
2xx = Success
└─ 200 OK          (GET/POST/PUT)
   201 Created     (POST new item)
   204 No Content  (DELETE)

4xx = Client Error
├─ 400 Bad Request     (Invalid input)
├─ 401 Unauthorized    (Need login)
├─ 403 Forbidden       (No permission)
├─ 404 Not Found       (Item missing)
├─ 409 Conflict        (Duplicate)
└─ 422 Validation      (Field errors)

5xx = Server Error
├─ 500 Internal Error  (Server bug)
└─ 503 Unavailable     (Maintenance)
```

---

## One-Minute Overview

```
1. Every service extends BaseCrudService<T>
2. Get 5 methods for free: getAll, getById, create, update, delete
3. Use in component: constructor(service: MyService) {}
4. Call method: this.service.getAll()
5. Get Observable: map to async pipe or subscribe
6. Errors auto-handled: Shows toast, logs to console
7. Auth auto-injected: No manual header work
8. No duplicate code: Just extend BaseCrudService

Result: Write less, achieve more! 🚀
```

---

## Quick Links

📖 [DEVELOPMENT_GUIDE.md](#)  
📊 [REFACTORING_SUMMARY.md](#)  
📋 [EXECUTIVE_SUMMARY.md](#)  

**Print this card and keep on your desk! 📌**
