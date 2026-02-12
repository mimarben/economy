# Refactorización ISP - Guía Completa

## ✅ Completado

### Interfaces Segregadas
- ✅ `repositories/interfaces.py` - Interfaces para repositorios
- ✅ `services/interfaces.py` - Interfaces para servicios  
- ✅ `di/container.py` - Contenedor de inyección de dependencias

### Base Repository
- ✅ `repositories/base_repository.py` - Implementa `ICRUDRepository`

### Repositorios Creados
- ✅ `repositories/expense_repository.py`
- ✅ `repositories/user_repository.py`
- ✅ `repositories/bank_repository.py`
- ✅ `repositories/account_repository.py`
- ✅ `repositories/source_repository.py`

### Servicios Refactorizados
- ✅ `services/expense_service.py` - Implementa `ICRUDService`
- ✅ `services/user_service.py` - Implementa `ICRUDService`
- ✅ `services/bank_service.py` - Implementa `ICRUDService`
- ✅ `services/account_service.py` - Implementa `ICRUDService`
- ✅ `services/source_service.py` - Implementa `ICRUDService`

### Routers Refactorizados (ISP - Dependency Injection)
- ✅ `routers/expense_router.py`
- ✅ `routers/user_router.py`
- ✅ `routers/bank_router.py`
- ✅ `routers/account_router.py`

---

## 📋 Por Hacer

### Servicios y Repositorios a Crear

Sigue el patrón con estas entidades:

```
ExpensesCategory
IncomesCategory
Income
Saving
SavingLog
InvestmentsCategory
Investment
InvestmentLog
FinancialSummary
Household
HouseholdMember
```

### Template para Repositório

```python
"""Repository for {ENTITY} entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import {ENTITY}


class {ENTITY}Repository(BaseRepository[{ENTITY}]):
    """Repository for {ENTITY} with custom queries."""

    def __init__(self, db):
        super().__init__(db, {ENTITY})

    # Add custom queries here if needed
```

### Template para Servicio

```python
"""Service for {ENTITY} implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.{entity}_repository import {ENTITY}Repository
from schemas.{entity}_schema import {ENTITY}Create, {ENTITY}Read, {ENTITY}Update
from models.models import {ENTITY}
from services.interfaces import ICRUDService


class {ENTITY}Service(ICRUDService[{ENTITY}Read, {ENTITY}Create, {ENTITY}Update]):
    """Service for {ENTITY} implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = {ENTITY}Repository(db)

    # ICreateService
    def create(self, data: {ENTITY}Create) -> {ENTITY}Read:
        obj = self.repository.create(**data.model_dump())
        return {ENTITY}Read.model_validate(obj)

    # IReadService
    def get_by_id(self, id: int) -> Optional[{ENTITY}Read]:
        obj = self.repository.get_by_id(id)
        return {ENTITY}Read.model_validate(obj) if obj else None

    def get_all(self) -> List[{ENTITY}Read]:
        return [{ENTITY}Read.model_validate(obj) for obj in self.repository.get_all()]

    # IUpdateService
    def update(self, id: int, data: {ENTITY}Update) -> Optional[{ENTITY}Read]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return {ENTITY}Read.model_validate(obj) if obj else None

    # IDeleteService
    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    # ISearchService
    def search(self, **filters) -> List[{ENTITY}Read]:
        return [{ENTITY}Read.model_validate(obj) for obj in self.repository.search(**filters)]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
```

### Template para Router

```python
"""Router for {ENTITY} endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.{entity}_schema import {ENTITY}Create, {ENTITY}Update
from services.{entity}_service import {ENTITY}Service
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint('{plural}', __name__)
name = "{plural}"


# Dependency Injection
def _get_create_service(db: Session) -> ICreateService:
    return {ENTITY}Service(db)

def _get_read_service(db: Session) -> IReadService:
    return {ENTITY}Service(db)

def _get_update_service(db: Session) -> IUpdateService:
    return {ENTITY}Service(db)

def _get_delete_service(db: Session) -> IDeleteService:
    return {ENTITY}Service(db)


@router.post("/{plural}")
def create():
    db: Session = next(get_db())
    try:
        data = {ENTITY}Create.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("{ENTITY_UPPER}_CREATED"), 201, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/{plural}/<int:id>")
def get_by_id(id):
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(id)
    if not result:
        return Response._error(_("{ENTITY_UPPER}_NOT_FOUND"), _("NONE"), 404, name)
    return Response._ok_data(result.model_dump(), _("{ENTITY_UPPER}_FOUND"), 200, name)


@router.get("/{plural}")
def list_all():
    db: Session = next(get_db())
    service: IReadService = _get_read_service(db)
    results = service.get_all()
    return Response._ok_data([r.model_dump() for r in results], _("{ENTITY_UPPER}_LIST"), 200, name)


@router.patch("/{plural}/<int:id>")
def update(id):
    db: Session = next(get_db())
    try:
        data = {ENTITY}Update.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)
        if not result:
            return Response._error(_("{ENTITY_UPPER}_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_data(result.model_dump(), _("{ENTITY_UPPER}_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/{plural}/<int:id>")
def delete(id):
    db: Session = next(get_db())
    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)
        if not success:
            return Response._error(_("{ENTITY_UPPER}_NOT_FOUND"), _("NONE"), 404, name)
        return Response._ok_message(_("{ENTITY_UPPER}_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
```

---

## 🎯 Beneficios Conseguidos

### 1. **Segregación de Interfaces (ISP)**
Cada endpoint depende solo de lo que necesita:
- POST → ICreateService
- GET → IReadService 
- PATCH → IUpdateService
- DELETE → IDeleteService

### 2. **Invertir Dependencias (DIP)**
Los routers dependen de interfaces, no de implementaciones:
```python
# ❌ Antes
service = ExpenseService(db)  # Depende de implementación

# ✅ Ahora
service: ICreateService = _get_create_service(db)  # Depende de interfaz
```

### 3. **Mayor Testabilidad**
Puedes mockear solo la interfaz que necesitas:
```python
class MockCreateService(ICreateService):
    def create(self, data) -> ExpenseRead:
        return ExpenseRead(id=1, ...)
    # Sin implementar get_by_id, delete, update...
```

### 4. **Claridad Arquitectónica**
Cada clase tiene una responsabilidad única:
- **Router**: HTTP request/response
- **Service**: Lógica de negocio
- **Repository**: Acceso a datos

### 5. **Desacoplamiento**
Cambios en métodos de lectura no afectan endpoints de escritura:
```python
# Cambiar IReadService NO afecta POST/PATCH/DELETE endpoints
# porque estos dependen solo de ICreateService/IUpdateService/IDeleteService
```

---

## 📝 Checklist de Implementación

- [ ] Crear repositorio para cada entidad
- [ ] Crear servicio para cada entidad
- [ ] Refactorizar router para cada entidad
- [ ] Actualizar `routers/__init__.py` si es necesario
- [ ] Probar endpoints con Postman/cURL
- [ ] Validar que los tests pasen

---

## 🚀 Próximos Pasos (Opcional)

1. **Usar un DI Framework**: Considera `injector` o `punq` para automatizar DI
2. **Crear Base Service**: Clase base reutilizable para todos los servicios
3. **Agregar validaciones de FK**: En servicios, valida que FK exista en BD
4. **Unit Tests**: Testa servicios y routers con mocks de interfaces

---

## 📚 Referencia Rápida

| Patrón | Ubicación | Propósito |
|--------|-----------|----------|
| ISP | `services/interfaces.py` | Segregar en interfaces pequeñas |
| DIP | `routers/*.py` | Depender de interfaces, no de implementaciones |
| SRP | Cada clase tiene una responsabilidad | Router ≠ Service ≠ Repository |
| Repository | `repositories/*.py` | Abstrae acceso a datos |
| Service | `services/*.py` | Lógica de negocio y orquestación |
