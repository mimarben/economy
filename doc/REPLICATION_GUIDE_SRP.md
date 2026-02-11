# 📋 Guía: Cómo Replicar el Patrón SRP en Otros Routers

Has visto el ejemplo con **Income**. Ahora vamos a replicarlo para todos los dominios.

---

## Checklist: Pasos a Seguir

### Para CADA dominio (Expense, Investment, Saving, etc):

#### ✅ Step 1: Crear Repository
**Archivo:** `api/repositories/{domain}_repository.py`

```python
from repositories.base_repository import BaseRepository

class {Domain}Repository(BaseRepository[{DomainModel}]):
    """Repository for {Domain} entity."""
    
    def __init__(self, db: Session):
        super().__init__(db, {DomainModel})
    
    # Métodos custom para este dominio
    def get_by_user(self, user_id: int):
        return self.db.query(self.model).filter(...).all()
    
    # ⭐ IMPORTANTE: Mover todos los validadores FK aquí
    def user_exists(self, user_id: int) -> bool:
        return self.db.query(User).filter(...).first() is not None
    
    def validate_foreign_keys(self, **kwargs):
        """Validar todas las FKs de este dominio."""
        for field, value in kwargs.items():
            if not self._validate_fk(field, value):
                return False, f"{field.upper()}_NOT_FOUND"
        return True, None
```

#### ✅ Step 2: Crear Service
**Archivo:** `api/services/{domain}_service.py`

```python
class {Domain}Service:
    """Service for {Domain} domain logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = {Domain}Repository(db)
    
    def create_{domain}(self, data: {Domain}Create) -> {Domain}Read:
        """Create with FK validation."""
        is_valid, error = self.repository.validate_foreign_keys(...)
        if not is_valid:
            raise ValueError(error)
        
        instance = self.repository.create(**data.model_dump())
        return {Domain}Read.model_validate(instance)
    
    def get_{domain}(self, id: int) -> Optional[{Domain}Read]:
        instance = self.repository.get_by_id(id)
        return {Domain}Read.model_validate(instance) if instance else None
    
    # ... resto de CRUD
```

#### ✅ Step 3: Limpiar Schema
**Archivo actualizado:** `api/schemas/{domain}_schema.py`

```python
# ❌ ELIMINAR: Validadores que queryaban BD
# ✅ MANTENER: Solo validación de formato

class {Domain}Create(BaseModel):
    field1: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    # No @field_validator con BD queries
```

#### ✅ Step 4: Refactorizar Router
**Archivo actualizado:** `api/routers/{domain}_router.py`

```python
@router.post("/{domains}")
def create_{domain}():
    db: Session = next(get_db())
    
    try:
        # ✅ Solo validación de formato
        data = {Domain}Create.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400)
    
    try:
        # ✅ Delegar al servicio
        service = {Domain}Service(db)
        result = service.create_{domain}(data)
        return Response._ok_data(result.model_dump(), _("{DOMAIN}_CREATED"), 201)
    except ValueError as e:
        return Response._error(_("FK_ERROR"), str(e), 400)
```

---

## Dominios a Refactorizar (Priority Order)

Por orden de complejidad y impacto:

| # | Dominio | Complejidad | Modelos Implicados |
|---|---------|:-----------:|---|
| 1 | **Expense** | Baja | Expense, ExpensesCategory, Source, User, Account |
| 2 | **Investment** | Media | Investment, InvestmentsCategory, User, Account, InvestmentLog |
| 3 | **Saving** | Media | Saving, Source, User, Account, SavingLog |
| 4 | **Account** | Media | Account, Bank, User |
| 5 | **Bank** | Baja | Bank |
| 6 | **Source** | Baja | Source |
| 7 | **Category** | Muy Baja | ExpensesCategory, IncomesCategory, InvestmentsCategory |
| 8 | **Household** | Media | Household, HouseholdMember, User |
| 9 | **User** | Alta | User (god object - requiere refactor mayor) |
| 10 | **FinancialSummary** | Alta | FinancialSummary (read-only, requiere cálculos) |

---

## Plantilla: Template Copy-Paste

### Repository Template
```python
# api/repositories/{domain}_repository.py

from typing import Optional, List
from sqlalchemy.orm import Session
from models.models import {DomainModel}, User, ...
from repositories.base_repository import BaseRepository

class {Domain}Repository(BaseRepository[{DomainModel}]):
    """Repository for {Domain} entity with custom queries."""
    
    def __init__(self, db: Session):
        super().__init__(db, {DomainModel})
    
    # Custom queries
    def get_by_user(self, user_id: int) -> List[{DomainModel}]:
        return self.db.query(self.model).filter(self.model.user_id == user_id).all()
    
    # FK validation methods
    def user_exists(self, user_id: int) -> bool:
        return self.db.query(User).filter(User.id == user_id).first() is not None
    
    def validate_foreign_keys(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate all FKs. Returns (is_valid, error_message)"""
        # Implementar validaciones específicas para este dominio
        pass
```

### Service Template
```python
# api/services/{domain}_service.py

from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.{domain}_repository import {Domain}Repository
from schemas.{domain}_schema import {Domain}Create, {Domain}Read, {Domain}Update
from models.models import {DomainModel}

class {Domain}Service:
    def __init__(self, db: Session):
        self.db = db
        self.repository = {Domain}Repository(db)
    
    def create_{domain}(self, data: {Domain}Create) -> {Domain}Read:
        is_valid, error = self.repository.validate_foreign_keys(**data.model_dump())
        if not is_valid:
            raise ValueError(error)
        
        instance = self.repository.create(**data.model_dump())
        return {Domain}Read.model_validate(instance)
    
    def get_{domain}(self, id: int) -> Optional[{Domain}Read]:
        instance = self.repository.get_by_id(id)
        return {Domain}Read.model_validate(instance) if instance else None
    
    def list_{domains}(self) -> List[{Domain}Read]:
        instances = self.repository.get_all()
        return [self.get_{domain}(i.id) for i in instances]
    
    def update_{domain}(self, id: int, data: {Domain}Update) -> Optional[{Domain}Read]:
        update_data = data.model_dump(exclude_unset=True)
        instance = self.repository.update(id, **update_data)
        return {Domain}Read.model_validate(instance) if instance else None
    
    def delete_{domain}(self, id: int) -> bool:
        return self.repository.delete(id)
```

### Router Template
```python
# api/routers/{domain}_router.py

from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.{domain}_schema import {Domain}Create, {Domain}Update
from services.{domain}_service import {Domain}Service
from db.database import get_db
from services.response_service import Response

router = Blueprint('{domains}', __name__)
name = "{domains}"

@router.post("/{domains}")
def create_{domain}():
    db: Session = next(get_db())
    try:
        data = {Domain}Create.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    
    try:
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
    
    try:
        service = {Domain}Service(db)
        result = service.update_{domain}({domain}_id, data)
        if not result:
            return Response._error(_("{DOMAIN}_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("{DOMAIN}_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)

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

---

## Quick Wins (Fáciles de implementar primero)

Recomendación: Empieza con estos para ganar confianza:

### 1. **Category Routers** (ExpensesCategory, IncomesCategory, etc)
- Muy simples, pocas FKs
- ~15 minutos cada uno
- Te familiariza con el patrón

### 2. **Bank & Source**
- Simples, pocas relaciones
- ~20 minutos cada uno

### 3. **Account**
- Mediano, 2 FKs
- ~30 minutos

Después: Expense, Investment, Saving.

Last: User, FinancialSummary (complejos).

---

## Próximos Pasos Después de Refactoriz

Cuando hayas refactorizado todos los routers:

1. **Crear Factory** para simplificar inyección de dependencias:
   ```python
   class ServiceFactory:
       def __init__(self, db: Session):
           self.db = db
       
       def income_service(self) -> IncomeService:
           return IncomeService(self.db)
       
       def expense_service(self) -> ExpenseService:
           return ExpenseService(self.db)
   ```

2. **Dependency Injection Middleware**:
   ```python
   @app.before_request
   def inject_services():
       g.services = ServiceFactory(next(get_db()))
   
   # En router:
   def create_income():
       service = g.services.income_service()
   ```

3. **Crear Base Tests** reutilizable:
   ```python
   class BaseRepositoryTests:
       """Tests genéricos para todo repository."""
       def test_create(self): ...
       def test_get_by_id(self): ...
   ```

---

## Indicadores de Éxito ✅

Cuando hayas terminado, deberías tener:

- ✅ **Routers simples**: Solo HTTP concerns
- ✅ **Services enfocados**: Solo lógica de negocio
- ✅ **Repositories claros**: Solo acceso a datos
- ✅ **Schemas simples**: Solo validación de formato
- ✅ **Modelos limpios**: Solo data structure
- ✅ **Tests rápidos**: Mock-based, no BD real
- ✅ **Cambios localizados**: Un cambio = un archivo
- ✅ **Código reutilizable**: Services desde múltiples fuentes

---

## Comandos Útiles

```bash
# Crear archivo de repository desde template
cp api/repositories/income_repository.py api/repositories/expense_repository.py
# ... Editar con placeholders

# Testear los cambios
pytest api/repositories/test_expense_repository.py -v
pytest api/services/test_expense_service.py -v
pytest api/routers/test_expense_router.py -v

# Lint
flake8 api/repositories/ api/services/ --max-line-length=120

# Type check
mypy api/repositories/ api/services/
```

---

## Preguntas Frecuentes

**P: ¿Necesito refactorizar TODO antes de deployar?**
A: No. Puedes hacerlo gradualmente. Income está hecho → funciona. Después Expense, etc.

**P: ¿Afecta a la base de datos?**
A: No. Los modelos (Base) no cambian, solo la arquitectura del código.

**P: ¿Cuánto tiempo toma?**
A: ~100 minutos para todos los dominios si usas la plantilla.

**P: ¿Breaking changes?**
A: No. Las rutas HTTP siguen siendo iguales. Solo cambió el código interno.

