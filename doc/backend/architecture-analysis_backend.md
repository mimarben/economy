# Workspace Architecture Analysis

## High-level layering

### Runtime/deployment layer
- `docker-compose.yml` defines two deployable units (`backend` and `frontend`) connected via one bridge network.
- The backend is Flask + SQLAlchemy, the frontend is Angular served with `ng serve`.

### Backend layers (`/api`)
- **Application entry/config layer**: `app.py` wires Flask, CORS, i18n, blueprint registration and global exception handling.
- **Transport layer**: `routers/*.py` expose HTTP endpoints by aggregate/resource.
- **Validation/contract layer**: `schemas/*.py` define Pydantic DTOs and validation logic.
- **Domain/persistence layer**: `models/models.py` declares SQLAlchemy entities and relationships.
- **Infrastructure/services layer**: `db/database.py` handles engine/session lifecycle, and `services/*` hosts utility services (`Response`, `UserService`, logging).

### Frontend layers (`/client/src/app`)
- **Composition/routing layer**: `app.routes.ts`, `app.config.ts`.
- **Feature/page layer**: `components/pages/*` for screen-specific flows.
- **Shared UI layer**: reusable primitives (`generic-form`, `generic-table`, dialog).
- **Client data-access layer**: `services/*` (HTTP API clients).
- **UI metadata/factory layer**: `factories/forms/form-factory.service.ts` for centralized dynamic form/table configuration.

## Domain boundaries

Backend resource boundaries are mostly REST-oriented and map directly to entity tables: users, banks/accounts, households/members, incomes/categories, expenses/categories, sources, savings/logs, investments/categories/logs, financial summaries.

Boundaries are represented by one router + schema + model trio per resource. This is clear structurally, but there is no explicit application service/use-case boundary between router and persistence; routers perform orchestration and persistence directly.

## Coupling analysis

### Strong couplings
- **Router ↔ ORM coupling**: routers import SQLAlchemy models and run query/commit logic directly.
- **Schema ↔ DB coupling**: some Pydantic validators require DB session context for FK checks.
- **Frontend page ↔ concrete service coupling**: page components inject concrete API services directly.
- **Frontend form system ↔ domain key strings coupling**: form/table generation relies on string keys in a large config map.

### Cross-layer coupling concerns
- Endpoint naming and payload shape are tightly coupled between Angular services and Flask routers (no adapter layer or shared typed contract generation).
- Backend mixes transport concerns and domain/data access concerns inside route functions.

## Design patterns observed

- **Component-based UI architecture** (Angular standalone components).
- **Repository-like behavior absent**; data access is Active Record-ish via direct ORM session usage in routers.
- **Factory/metadata-driven UI**: form and table definitions are generated from a centralized `FormFactoryService`.
- **Template/generic component pattern**: `GenericTableComponent<T>` and `GenericFormComponent` provide reusable behavior with configurable metadata.
- **Service layer (partial)**: utility services exist (`Response`, `UserService`), but business services are not uniformly applied across resources.
- **Facade-like API client services** in frontend (`BankService`, `UserService`, etc.).

## SOLID evaluation

### Single Responsibility Principle (SRP)
Potential violations:
- Route handlers perform request parsing, validation orchestration, persistence, error mapping, and response formatting in one function.
- `db/database.py` mixes engine/session config with DB bootstrapping/sample seed behavior.
- `FormFactoryService` carries extensive configuration for many domains, plus formatting and option-generation logic.

### Open/Closed Principle (OCP)
Potential violations:
- Adding new resource types requires editing centralized registries (`routers/__init__.py`, `FormFactoryService` type unions/config maps), rather than extension by plugin/module registration.

### Liskov Substitution Principle (LSP)
- Not a major issue in current code because inheritance hierarchies are minimal.

### Interface Segregation Principle (ISP)
Potential issues:
- Frontend service interfaces are coarse per resource and not abstracted behind narrower interfaces for read/write/query variants.
- Consumers depend on concrete services instead of interfaces.

### Dependency Inversion Principle (DIP)
Potential violations:
- High-level route logic depends directly on low-level ORM/session details.
- Frontend feature components depend on concrete HTTP service classes.
- No explicit domain ports/adapters for persistence or external systems.

## Practical recommendations

1. Introduce backend application services/use-cases (e.g., `CreateUserUseCase`) and keep routers thin.
2. Add repository interfaces and adapter implementations around SQLAlchemy sessions.
3. Standardize a base CRUD service usage in frontend to reduce duplicate concrete services.
4. Split `FormFactoryService` by bounded context (banking, household, cashflow, investments) to reduce god-service risk.
5. Add contract tests between frontend API clients and backend endpoints.
6. Centralize error taxonomy and HTTP mapping so routers stop duplicating error handling.


Router (HTTP)
   ↓
Service (lógica de negocio)
   ↓
Repository (acceso a datos)
   ↓
SQLAlchemy


# 🧱 1️⃣ Router = Solo HTTP

Archivo: expense_router.py

Ahora el router:

✅ Valida formato (Pydantic)

✅ Maneja códigos HTTP

✅ Traduce errores a respuestas JSON

❌ No hace lógica de negocio

❌ No accede directamente a la DB

```python
service = ExpenseService(db)
result = service.create_expense(expense_data)
``` 

# 🧠 2️⃣ Service = Lógica de negocio

Archivo: expense_service.py

Aquí vive ahora:

Validación de reglas de negocio

Orquestación

Transformación entre modelos y schemas

Casos de uso reales

```python
is_valid, error = self.repository.validate_foreign_keys(...)
``` 

# 3️⃣ Repository = Acceso a datos

Archivo: expense_repository.py

Este solo:

Ejecuta queries

Hace filtros

Accede a tablas

NO sabe nada de HTTP

NO sabe nada de schemas

```python
return self.db.query(Expense).filter(Expense.user_id == user_id).all()
```

# 🎯 El cambio más importante

Antes probablemente tenías algo así en un schema:

@validator("user_id")
def validate_user_exists(...)


Eso está mal arquitectónicamente porque:

Un schema no debería necesitar una Session

Pydantic no debería depender de SQLAlchemy

Mezcla validación estructural con persistencia

Ahora:

Schema → solo valida formato
Service → valida reglas
Repository → valida existencia en DB

Esto es mucho más limpio.

# 📐 Qué patrón te ha aplicado

Lo que te ha montado es esto:

Service Layer Pattern

Centraliza la lógica de negocio en una capa intermedia.

Repository Pattern

Abstrae el acceso a datos detrás de una clase.

SRP (Single Responsibility Principle)

Cada clase tiene una única razón para cambiar.


# 🎯 ¿Qué estamos intentando lograr?

Que el router no conozca SQLAlchemy.

Que el router no conozca reglas de negocio.

Que el service no conozca HTTP.

Que el repository no conozca Pydantic.

Separación de responsabilidades clara.
