# ⚡ SRP Refactoring: Quick Reference Card

## 🎯 Lo que Hicimos con Income

```
✅ Creamos: api/repositories/income_repository.py
✅ Creamos: api/services/income_service.py
✅ Limpiamos: api/schemas/income_schema.py
✅ Refactorizamos: api/routers/income_router.py
✅ Patrón es REUTILIZABLE
```

---

## 📋 Checklist para Otros Dominios

Cuando refactorices **Expense, Investment, Saving, etc.**:

### Step 1: Crear Repository
```python
# File: api/repositories/{domain}_repository.py

from repositories.base_repository import BaseRepository
from models.models import {DomainModel}, ...

class {Domain}Repository(BaseRepository[{DomainModel}]):
    def __init__(self, db: Session):
        super().__init__(db, {DomainModel})
    
    # Custom queries for this domain
    def get_by_user(self, user_id: int):
        return self.db.query(self.model).filter(...).all()
    
    # FK validation (moved from schema validators)
    def validate_foreign_keys(self, **kwargs) -> tuple[bool, Optional[str]]:
        # Validator for each FK
        if 'user_id' in kwargs and not self.user_exists(kwargs['user_id']):
            return False, "USER_NOT_FOUND"
        # ... more validators
        return True, None
```

✅ **Responsabilidad única:** Data access

---

### Step 2: Crear Service
```python
# File: api/services/{domain}_service.py

from repositories.{domain}_repository import {Domain}Repository
from schemas.{domain}_schema import {Domain}Create, {Domain}Read, {Domain}Update

class {Domain}Service:
    def __init__(self, db: Session):
        self.db = db
        self.repository = {Domain}Repository(db)
    
    def create_{domain}(self, data: {Domain}Create) -> {Domain}Read:
        # 1. Validate
        is_valid, error = self.repository.validate_foreign_keys(**data.model_dump())
        if not is_valid:
            raise ValueError(error)
        
        # 2. Create
        instance = self.repository.create(**data.model_dump())
        
        # 3. Return
        return {Domain}Read.model_validate(instance)
    
    def get_{domain}(self, id: int) -> Optional[{Domain}Read]:
        instance = self.repository.get_by_id(id)
        return {Domain}Read.model_validate(instance) if instance else None
    
    def update_{domain}(self, id: int, data: {Domain}Update) -> Optional[{Domain}Read]:
        update_data = data.model_dump(exclude_unset=True)
        instance = self.repository.update(id, **update_data)
        return {Domain}Read.model_validate(instance) if instance else None
    
    def delete_{domain}(self, id: int) -> bool:
        return self.repository.delete(id)
```

✅ **Responsabilidad única:** Business logic & orchestration

---

### Step 3: Limpiar Schema
```python
# File: api/schemas/{domain}_schema.py
# BEFORE: Tenía @field_validator con db.query()
# AFTER:

class {Domain}Create(BaseModel):
    field1: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    # NO validators that query DB
    
    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        # ONLY format validation
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
```

✅ **Responsabilidad única:** Format validation only

---

### Step 4: Refactorizar Router
```python
# File: api/routers/{domain}_router.py

@router.post("/{domains}")
def create_{domain}():
    db: Session = next(get_db())
    
    try:
        # ✅ ONLY format validation
        data = {Domain}Create.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    
    try:
        # ✅ DELEGATE to service
        service = {Domain}Service(db)
        result = service.create_{domain}(data)
        return Response._ok_data(result.model_dump(), _("{DOMAIN}_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("FK_ERROR"), str(e), 400, name)

@router.get("/{domains}/<int:{domain}_id>")
def get_{domain}({domain}_id):
    db: Session = next(get_db())
    service = {Domain}Service(db)
    result = service.get_{domain}({domain}_id)
    if not result:
        return Response._error(_("{DOMAIN}_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(result.model_dump(), _("{DOMAIN}_FOUND"), 200, name)

@router.patch("/{domains}/<int:{domain}_id>")
def update_{domain}({domain}_id):
    db: Session = next(get_db())
    try:
        data = {Domain}Update.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    
    service = {Domain}Service(db)
    result = service.update_{domain}({domain}_id, data)
    if not result:
        return Response._error(_("{DOMAIN}_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(result.model_dump(), _("{DOMAIN}_UPDATED"), 200, name)

@router.delete("/{domains}/<int:{domain}_id>")
def delete_{domain}({domain}_id):
    db: Session = next(get_db())
    service = {Domain}Service(db)
    success = service.delete_{domain}({domain}_id)
    if not success:
        return Response._error(_("{DOMAIN}_NOT_FOUND"), _("NONE"), 404, name)
    return Response._error(_("{DOMAIN}_DELETED"), _("NONE"), 204, name)

@router.get("/{domains}")
def list_{domains}():
    db: Session = next(get_db())
    service = {Domain}Service(db)
    results = service.list_{domains}()
    if not results:
        return Response._error(_("{DOMAIN}_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(
        [r.model_dump() for r in results],
        _("{DOMAIN}_FOUND"),
        200,
        name
    )
```

✅ **Responsabilidad única:** HTTP handling

---

## 🔄 Flow Recap

```
HTTP Request
    ↓
Router (Parse HTTP) → Validate format only
    ↓
Service (Business Logic) → Orchestrate & validate rules
    ↓
Repository (Data Access) → Query DB & FK validation
    ↓
Database
    ↓ (Response)
Service (Format DTO)
    ↓
Router (Format HTTP)
    ↓
HTTP Response
```

**Key:** Each layer has ONE clear responsibility.

---

## 🚀 Domains to Refactor (In Order)

| Priority | Domain | Files to Change | Time | FK Count |
|:---:|---|---|:---:|:---:|
| 1 | ExpensesCategory | 2 (schema, router) | 15m | 0 |
| 2 | IncomesCategory | 2 (schema, router) | 15m | 0 |
| 3 | InvestmentsCategory | 2 (schema, router) | 15m | 0 |
| 4 | Bank | 4 (repo, service, schema, router) | 30m | 0 |
| 5 | Source | 4 (repo, service, schema, router) | 30m | 0 |
| 6 | **Expense** | 4 (repo, service, schema, router) | 45m | 4 |
| 7 | **Investment** | 4 (repo, service, schema, router) | 60m | 4 |
| 8 | **Saving** | 4 (repo, service, schema, router) | 60m | 4 |
| 9 | Account | 4 (repo, service, schema, router) | 45m | 2 |
| 10 | SavingLog | 4 (repo, service, schema, router) | 45m | 2 |
| 11 | InvestmentLog | 4 (repo, service, schema, router) | 45m | 2 |
| 12 | Household | 4 (repo, service, schema, router) | 45m | 0 |
| 13 | HouseholdMember | 4 (repo, service, schema, router) | 45m | 2 |
| 14 | FinancialSummary | 4 (repo, service, schema, router) | 60m | 2 |
| 15 | **User** | 4 (repo, service, schema, router) | 90m | 0 |

**Total: ~12 hours for complete refactor**

---

## ✅ Signs You're Doing It Right

### Repository should:
- ✅ Only contain `self.db.query(...)` calls
- ✅ Only return models or lists of models
- ✅ Have 1-3 custom query methods (domain-specific)
- ✅ Have FK validation methods
- ✅ NOT know about HTTP, schemas, or business logic

### Service should:
- ✅ Only contain business logic
- ✅ Use repository for data access
- ✅ Validate FK constraints
- ✅ Raise `ValueError` for business errors
- ✅ Return DTOs (schemas)
- ✅ NOT know about HTTP

### Router should:
- ✅ Only parse HTTP requests
- ✅ Only format HTTP responses
- ✅ Only validate **format** (using schema)
- ✅ Delegate everything to service
- ✅ Catch service exceptions
- ✅ NOT query database directly

### Schema should:
- ✅ Only validate **format** (types, ranges, lengths)
- ✅ NOT query database
- ✅ NOT need context={'db': db}
- ✅ Simple, focused validators
- ✅ Used for both input and output

---

## 🔍 Common Mistakes to Avoid

### ❌ Don't do this:

```python
# Wrong: Service queries DB directly
class ExpenseService:
    def create_expense(self, data):
        user = self.db.query(User).filter(...)  # ❌ Use repository!
        return Expense(...)

# Wrong: Router validates FK
@router.post(...)
def create_expense():
    if not db.query(Source).filter(...).first():  # ❌ Use repository!
        return error

# Wrong: Schema has business logic
class ExpenseCreate:
    @field_validator('amount')
    def check_budget(cls, v, info):  # ❌ Belongs in service!
        # Complex business logic here
```

### ✅ Do this instead:

```python
# Right: Service uses repository
class ExpenseService:
    def create_expense(self, data):
        is_valid, error = self.repository.validate_foreign_keys(...)
        instance = self.repository.create(...)
        return ExpenseRead.model_validate(instance)

# Right: Router only validates format
@router.post(...)
def create_expense():
    data = ExpenseCreate.model_validate(request.json)  # Format only
    service = ExpenseService(db)
    result = service.create_expense(data)

# Right: Schema only validates format
class ExpenseCreate:
    amount: float = Field(..., gt=0)  # Format validation only
```

---

## 📊 Testing Checklist

For each refactored domain:

```python
# Test Repository
✅ test_create()
✅ test_get_by_id()
✅ test_get_all()
✅ test_update()
✅ test_delete()
✅ test_get_by_user()
✅ test_validate_foreign_keys()

# Test Service
✅ test_create_{domain}_success()
✅ test_create_{domain}_fk_validation_error()
✅ test_get_{domain}()
✅ test_update_{domain}()
✅ test_delete_{domain}()

# Test Router
✅ test_post_{domain}() - POST success
✅ test_post_{domain}_validation_error() - Format validation
✅ test_post_{domain}_fk_error() - FK validation
✅ test_get_{domain}() - GET by id
✅ test_patch_{domain}() - PATCH
✅ test_delete_{domain}() - DELETE
✅ test_list_{domains}() - GET all
```

Use mocks for tests, no real DB!

---

## 📚 Files to Reference

```
✅ ARCHITECTURE_SRP_REFACTOR.md    ← Explanation
✅ COMPARISON_BEFORE_AFTER.md      ← Visual comparison
✅ REPLICATION_GUIDE_SRP.md        ← Step-by-step guide
✅ TESTING_EXAMPLE_SRP.md          ← How to test
✅ income_repository.py            ← Template (copy & adapt)
✅ income_service.py               ← Template (copy & adapt)
```

---

## 🔧 Commands

```bash
# Create new repository from template
cp api/repositories/income_repository.py api/repositories/expense_repository.py

# Run tests for one domain
pytest api/repositories/test_expense_repository.py -v
pytest api/services/test_expense_service.py -v
pytest api/routers/test_expense_router.py -v

# Run all tests
pytest api/ -v

# Check code quality
flake8 api/repositories/ api/services/ --max-line-length=120
mypy api/repositories/ api/services/

# Count lines changed
git diff --stat api/routers/ api/schemas/ api/services/ api/repositories/
```

---

## ⏱️ Estimated Time

- **Quick category domains** (0 FKs): 15 min each × 3 = 45 min
- **Simple domains** (0-2 FKs): 30 min each × 2 = 60 min
- **Medium domains** (2-4 FKs): 45 min each × 6 = 270 min
- **Complex domains** (4+ FKs, User): 90 min each × 2 = 180 min
- **Testing all**: +2-3 hours

**Total: ~12 hours** (can be done in parallel)

---

## 💡 Pro Tips

1. **Use Find & Replace** - Replace `{domain}` with actual domain name
2. **Copy-Paste Templates** - Don't rewrite, adapt templates
3. **Test as You Go** - Test each domain after refactoring
4. **Git Commits** - One domain per commit for easy revert
5. **Code Review** - Ask colleague to review pattern consistency
6. **Incremental** - You don't need to do all at once!

---

## 📞 Quick Answers

**Q: Can I deploy while refactoring?**
A: Yes! Income is done → Deploy. Expense partial → Don't deploy yet.

**Q: Will this break the API?**
A: No. Routes & request/response format unchanged. Only internal code.

**Q: Do I need to change models?**
A: No. Models stay the same, only usage changes.

**Q: What if I make mistakes?**
A: Tests will catch them. Run tests after each domain.

