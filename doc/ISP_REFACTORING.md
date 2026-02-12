# Interface Segregation Principle (ISP) Refactoring

## Overview
Este refactor aplica ISP (uno de los principios SOLID) para mejorar la arquitectura de la API Flask. 

**ISP dice**: Clientes no deberían depender de interfaces que no usan.

## Problema Original
```python
# ❌ Router dependía de toda la clase service
service = ExpenseService(db)
result = service.create_expense(expense_data)  # Solo necesitaba create
result = service.get_expense(expense_id)       # Solo necesitaba read
result = service.update_expense(...)           # Solo necesitaba update
```

Aunque funciona, el router está acoplado a **más métodos de los que realmente necesita**.

## Solución: Segregar Interfaces

### 1. Interfaces de Repositorio (repositories/interfaces.py)
```python
class IReadRepository(ABC, Generic[T]):
    """Solo lectura"""
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]: pass
    
    @abstractmethod
    def get_all(self) -> List[T]: pass

class IWriteRepository(ABC, Generic[T]):
    """Solo escritura"""
    @abstractmethod
    def create(self, obj: T) -> T: pass
    
    @abstractmethod
    def update(self, id: int, **kwargs) -> Optional[T]: pass
    
    @abstractmethod
    def delete(self, id: int) -> bool: pass

class ISearchRepository(ABC, Generic[T]):
    """Solo búsqueda"""
    @abstractmethod
    def search(self, **filters) -> List[T]: pass
    
    @abstractmethod
    def count(self, **filters) -> int: pass

class ICRUDRepository(IReadRepository[T], IWriteRepository[T], ISearchRepository[T]):
    """Combina todas cuando es necesario"""
    pass
```

### 2. Interfaces de Servicio (services/interfaces.py)
```python
class IReadService(ABC, Generic[T]):
    """Servicio solo de lectura"""
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]: pass
    
    @abstractmethod
    def get_all(self) -> List[T]: pass

class ICreateService(ABC, Generic[U, T]):
    """Servicio solo de creación"""
    @abstractmethod
    def create(self, data: U) -> T: pass

class IUpdateService(ABC, Generic[U, T]):
    """Servicio solo de actualización"""
    @abstractmethod
    def update(self, id: int, data: U) -> Optional[T]: pass

class IDeleteService(ABC):
    """Servicio solo de borrado"""
    @abstractmethod
    def delete(self, id: int) -> bool: pass

class ISearchService(ABC, Generic[T]):
    """Servicio solo de búsqueda"""
    @abstractmethod
    def search(self, **filters) -> List[T]: pass
    
    @abstractmethod
    def count(self, **filters) -> int: pass

class ICRUDService(IReadService[T], ICreateService[U, T], IUpdateService[U, T], 
                   IDeleteService, ISearchService[T]):
    """Interfaz completa cuando se necesita"""
    pass
```

## Implementación en servicios

### Antes (monolítico)
```python
class ExpenseService:
    def create_expense(self, data): ...
    def get_expense(self, id): ...
    def update_expense(self, id, data): ...
    def delete_expense(self, id): ...
```

### Ahora (segregado)
```python
class ExpenseService(ICRUDService[ExpenseRead, ExpenseCreate, ExpenseUpdate]):
    """Implementa todas las interfaces segregadas"""
    
    # ICreateService
    def create(self, data: ExpenseCreate) -> ExpenseRead: ...
    
    # IReadService
    def get_by_id(self, id: int) -> Optional[ExpenseRead]: ...
    def get_all(self) -> List[ExpenseRead]: ...
    
    # IUpdateService
    def update(self, id: int, data: ExpenseUpdate) -> Optional[ExpenseRead]: ...
    
    # IDeleteService
    def delete(self, id: int) -> bool: ...
    
    # ISearchService
    def search(self, **filters) -> List[ExpenseRead]: ...
    def count(self, **filters) -> int: ...
```

## Inyección de Dependencias en Routers

### Funciones Helper (Dependency Injection)
```python
def _get_create_service(db: Session) -> ICreateService:
    """El router depende SOLO de ICreateService"""
    return ExpenseService(db)

def _get_read_service(db: Session) -> IReadService:
    """El router depende SOLO de IReadService"""
    return ExpenseService(db)

def _get_update_service(db: Session) -> IUpdateService:
    """El router depende SOLO de IUpdateService"""
    return ExpenseService(db)
```

### Uso en Endpoints
```python
@router.post("/expenses")
def create_expense():
    db = next(get_db())
    
    # ✅ El router solo sabe que necesita crear (ISP)
    service: ICreateService = _get_create_service(db)
    result = service.create(expense_data)
    return Response._ok_data(result.model_dump(), ...)

@router.get("/expenses/<int:expense_id>")
def get_expense(expense_id):
    db = next(get_db())
    
    # ✅ El router solo sabe que necesita leer (ISP)
    service: IReadService = _get_read_service(db)
    result = service.get_by_id(expense_id)
    return Response._ok_data(result.model_dump(), ...)
```

## Beneficios

### 1. **Explicititud** 
Cada endpoint declara exactamente qué métodos necesita:
```python
# POST /expenses necesita crear
service: ICreateService = _get_create_service(db)

# GET /expenses/:id necesita leer
service: IReadService = _get_read_service(db)

# DELETE /expenses/:id necesita borrar
service: IDeleteService = _get_delete_service(db)
```

### 2. **Testabilidad**
Mocks más pequeños y específicos:
```python
class MockCreateService(ICreateService):
    def create(self, data) -> ExpenseRead:
        return ExpenseRead(id=1, amount=100, ...)
    # Sin necesidad de implementar get_by_id, delete, etc.
```

### 3. **Mantenibilidad**
Cambios en métodos de lectura no afectan endpoints de escritura:
```python
# Si cambio IReadService.get_all(), solo afecta GET endpoints
# Los POST/PATCH/DELETE no se entran
```

### 4. **Extensibilidad**
Fácil crear nuevos servicios especializado:
```python
class ExpenseReportService(IReadService[ExpenseReport], ISearchService):
    """Solo lee y busca, no puede crear/actualizar/borrar"""
    pass
```

## Cómo aplicar a otros servicios

### Template para nuevos servicios
```python
from services.interfaces import ICRUDService

class UserService(ICRUDService[UserRead, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)
    
    # ICreateService
    def create(self, data: UserCreate) -> UserRead:
        user = self.repository.create(**data.model_dump())
        return UserRead.model_validate(user)
    
    # IReadService
    def get_by_id(self, id: int) -> Optional[UserRead]:
        user = self.repository.get_by_id(id)
        return UserRead.model_validate(user) if user else None
    
    def get_all(self) -> List[UserRead]:
        users = self.repository.get_all()
        return [UserRead.model_validate(u) for u in users]
    
    # IUpdateService
    def update(self, id: int, data: UserUpdate) -> Optional[UserRead]:
        user = self.repository.update(id, **data.model_dump(exclude_unset=True))
        return UserRead.model_validate(user) if user else None
    
    # IDeleteService
    def delete(self, id: int) -> bool:
        return self.repository.delete(id)
    
    # ISearchService
    def search(self, **filters) -> List[UserRead]:
        users = self.repository.search(**filters)
        return [UserRead.model_validate(u) for u in users]
    
    def count(self, **filters) -> int:
        return self.repository.count(**filters)
```

### Template para routers
```python
from services.interfaces import IReadService, ICreateService

@router.post("/users")
def create_user():
    db = next(get_db())
    service: ICreateService = UserService(db)
    result = service.create(UserCreate.model_validate(request.json))
    return Response._ok_data(result.model_dump(), ...)

@router.get("/users/<int:user_id>")
def get_user(user_id):
    db = next(get_db())
    service: IReadService = UserService(db)
    result = service.get_by_id(user_id)
    return Response._ok_data(result.model_dump(), ...)
```

## Resumen de archivos creados/modificados

| Archivo | Cambio |
|---------|--------|
| `repositories/interfaces.py` | ✨ NUEVO - Interfaces segregadas para repositorios |
| `repositories/base_repository.py` | 🔄 Implementa `ICRUDRepository` |
| `services/interfaces.py` | ✨ NUEVO - Interfaces segregadas para servicios |
| `services/expense_service.py` | 🔄 Implementa `ICRUDService` con métodos segregados |
| `routers/expense_router.py` | 🔄 Depende solo de interfaces específicas (ISP) |
| `di/container.py` | ✨ NUEVO - Contenedor DI reutilizable |

## Próximos pasos

1. Aplicar el mismo patrón a otros servicios:
   - `UserService`
   - `BankService` 
   - `AccountService`
   - `SavingService`
   - `InvestmentService`
   - etc.

2. Usar `ServiceContainer` en routers para inyección consistente

3. Considerar un framework DI completo (e.g., `injector`) si crece mucho
