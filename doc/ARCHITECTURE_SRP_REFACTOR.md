# Refactorización SRP: Single Responsibility Principle

## Problema Original ❌

### Router hacía todo (5+ responsabilidades)
```python
@router.post("/incomes")
def create_income():
    # 1. Parse HTTP
    db: Session = next(get_db())
    
    # 2. Validar datos (incluyendo BD)
    income_data = IncomeCreate.model_validate(request.json, context={"db": db})
    
    # 3. Crear objeto ORM
    new_income = Income(**income_data.model_dump())
    
    # 4. Persistir
    db.add(new_income)
    db.commit()
    
    # 5. Formatear respuesta
    return Response._ok_data(...)
```

**Razones para cambiar:**
1. ¿Cambia el formato HTTP? → Cambios en router
2. ¿Cambia la validación? → Cambios en router
3. ¿Cambia la lógica de negocio? → Cambios en router
4. ¿Cambia la persistencia? → Cambios en router
5. ¿Cambia el formato de respuesta? → Cambios en router

### Schemas validaban formato AND BD ❌
```python
class IncomeCreate(IncomeBase):
    @field_validator('source_id')
    def validate_foreign_key(cls, v, info):
        db = info.context.get('db')
        # ❌ Responsabilidad 1: Validar formato
        # ❌ Responsabilidad 2: Queryar BD
        if not db.query(Source).filter(...).first():
            raise PydanticCustomError(...)
```

**Problema:** Schemas son para DTOs, no para lógica de BD.

---

## Solución: Separación de Responsabilidades ✅

### 1️⃣ **Income Repository** (Data Access Layer)
**Responsabilidad única:** Acceso a datos

```python
class IncomeRepository(BaseRepository[Income]):
    def validate_foreign_keys(self, user_id, source_id, category_id, account_id):
        # ✅ Solo responsable de validar FKs contra BD
        is_valid, error = ...
        return is_valid, error
    
    def get_by_user(self, user_id):
        # ✅ Solo responsable de queries
        return self.db.query(Income).filter(...)
```

**Razones para cambiar:** Solo si cambia cómo accedemos a datos.

---

### 2️⃣ **Income Service** (Business Logic Layer)
**Responsabilidad única:** Orquestar lógica de negocio

```python
class IncomeService:
    def __init__(self, db: Session):
        self.repository = IncomeRepository(db)
    
    def create_income(self, income_data: IncomeCreate) -> IncomeRead:
        # 1. Validar constraints de negocio (con repository)
        is_valid, error = self.repository.validate_foreign_keys(...)
        if not is_valid:
            raise ValueError(error)
        
        # 2. Crear a través del repository
        income = self.repository.create(**income_data.model_dump())
        
        # 3. Retornar serializado
        return IncomeRead.model_validate(income)
    
    def calculate_total_income(self, user_id, start, end):
        # ✅ "Orquesta" operaciones, contiene lógica de negocio
        incomes = self.repository.get_by_date_range(user_id, start, end)
        return sum(inc.amount for inc in incomes)
```

**Razones para cambiar:** Solo si cambia la lógica de negocio de ingresos.

---

### 3️⃣ **Income Schema** (Format Validation Only)
**Responsabilidad única:** Validar formato de datos

```python
class IncomeCreate(IncomeBase):
    # ✅ SOLO validación de formato
    pass

class IncomeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    date: datetime
    
    @field_validator('amount')
    def amount_must_be_positive(cls, v):
        # ✅ Solo valida formato, no BD
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
```

**Razones para cambiar:** Solo si cambia el formato de entrada.

---

### 4️⃣ **Income Router** (HTTP Handling)
**Responsabilidad única:** Manejar HTTP

```python
@router.post("/incomes")
def create_income():
    db: Session = next(get_db())
    
    try:
        # ✅ Solo valida formato (sin DB)
        income_data = IncomeCreate.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)
    
    try:
        # ✅ Delega al servicio
        service = IncomeService(db)
        result = service.create_income(income_data)
        
        # ✅ Retorna respuesta HTTP
        return Response._ok_data(result.model_dump(), _("INCOME_CREATED"), 201, name)
    except ValueError as e:
        # ✅ Maneja errores de negocio
        return Response._error(_("FK_ERROR"), str(e), 400, name)
```

**Razones para cambiar:** Solo si cambia cómo formateamos HTTP (headers, status codes, etc).

---

## Flujo de Datos

```
HTTP Request (JSON)
    ↓
Router (Parse HTTP)
    ↓
Schema (Validate format)
    ↓
Service (Orchestrate logic)
    ↓
Repository (Validate FK)
    ↓
Database (Persist)
    ↓
Service (Return DTO)
    ↓
Router (Format HTTP response)
    ↓
HTTP Response (JSON)
```

Cada capa tiene **UNA SOLA RESPONSABILIDAD**.

---

## Beneficios ✅

### 1. **Testabilidad** 
```python
# Puedo testear Service sin HTTP
service = IncomeService(mock_db)
result = service.create_income(test_data)
assert result.id > 0

# Puedo testear Repository sin Service
repo = IncomeRepository(mock_db)
assert repo.user_exists(1)
```

### 2. **Cambios Localizados**
| Cambio | Archivo | Impacto |
|--------|---------|--------|
| Formato HTTP cambia | `router.py` | ⬜ Solo 1 archivo |
| Validación formato cambia | `schema.py` | ⬜ Solo 1 archivo |
| Lógica de negocio cambia | `service.py` | ⬜ Solo 1 archivo |
| Estructura BD cambia | `repository.py` | ⬜ Solo 1 archivo |

Antiguamente: **cambio en 1 lugar = cambios en TODOS los archivos** 🚫

### 3. **Reutilización**
```python
# Service puede usarse desde diferentes routers
class IncomeRouter:
    service = IncomeService(db)
    service.create_income(...)  # POST

class IncomeWSHandler:  # WebSocket
    service = IncomeService(db)
    service.create_income(...)  # Mismo servicio

class IncomeJob:  # Background job
    service = IncomeService(db)
    service.calculate_total_income(...)  # Mismo servicio
```

### 4. **Mantenibilidad**
Cada clase es **simple y enfocada**. Más fácil de entender, debuggear y mantener.

---

## Resumen: Razones para Cambiar Cada Componente

| Componente | Razón(es) para cambiar |
|---|---|
| **Router** | Cambia formato HTTP (headers, status, paths) |
| **Schema** | Cambia formato de datos (tipos, validaciones de formato) |
| **Service** | Cambia lógica de negocio (reglas, cálculos) |
| **Repository** | Cambia estructura de BD (queries, relaciones) |

**SRP = Una razón para cambiar = Una responsabilidad**.

---

## Próximos Pasos

1. ✅ **Refactorizar Income** (hecho)
2. ⏳ **Replicar patrón** para otros dominios:
   - Expenses → ExpenseService + ExpenseRepository
   - Investments → InvestmentService + InvestmentRepository
   - Savings → SavingService + SavingRepository
3. ⏳ **Crear Factory** para simplificar inyección de dependencias
4. ⏳ **Mejorar Modelos** para reducir acoplamiento (separar User en 3 bounded contexts)

