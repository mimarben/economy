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