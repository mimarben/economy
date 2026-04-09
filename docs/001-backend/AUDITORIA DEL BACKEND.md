## Resumen General

La arquitectura del backend está **muy bien planteada**. La separación en capas (Router → Service → Repository → Model → Schema) es correcta, tiene interfaces abstractas (ISP), generics en [BaseService](file:///home/martinm/src/economy/api/services/core/base_service.py#11-63)/[BaseRepository](file:///home/martinm/src/economy/api/repositories/core/base_repository.py#8-75), i18n con Babel, y un logger propio. **Hay muchas cosas que NO hay que tocar**. A continuación, lo que está bien y lo que se debe mejorar.

---

## ✅ Lo que está BIEN (no tocar)

| Área | Detalle |
|---|---|
| **Arquitectura por capas** | Router → Service → Repository → Model es exactamente lo que pide la spec |
| **Interfaces ISP** | [IReadService](file:///home/martinm/src/economy/api/services/core/interfaces.py#10-19), [ICreateService](file:///home/martinm/src/economy/api/services/core/interfaces.py#35-42), [IUpdateService](file:///home/martinm/src/economy/api/services/core/interfaces.py#44-51), [IDeleteService](file:///home/martinm/src/economy/api/services/core/interfaces.py#53-60) + [ICRUDService](file:///home/martinm/src/economy/api/services/core/interfaces.py#62-71) compuesto. Lo mismo en Repository |
| **BaseService / BaseRepository genéricos** | Usan `TypeVar` y `Generic`. Bien cohesionados, CRUD reutilizable |
| **Schemas Pydantic separados** | [ExpenseCreate](file:///home/martinm/src/economy/api/schemas/expenses/expense_schema.py#40-46), [ExpenseRead](file:///home/martinm/src/economy/api/schemas/expenses/expense_schema.py#31-38), [ExpenseUpdate](file:///home/martinm/src/economy/api/schemas/expenses/expense_schema.py#48-60) — exactamente la separación entrada/salida que pide la spec |
| **Validación FK en Service (no en Schema)** | Correcto: los schemas solo validan formato; el service valida reglas de negocio |
| **Enums centralizados** | [CurrencyEnum](file:///home/martinm/src/economy/api/models/core/enums.py#4-20), [RoleEnum](file:///home/martinm/src/economy/api/models/core/enums.py#22-27), [SourceTypeEnum](file:///home/martinm/src/economy/api/models/core/enums.py#29-35), [ActionEnum](file:///home/martinm/src/economy/api/models/core/enums.py#37-44), [UserRoleEnum](file:///home/martinm/src/economy/api/models/core/enums.py#46-51) en un solo lugar |
| **Organización por dominio** | [expenses/](file:///home/martinm/src/economy/api/routers/expenses/expense_router.py#85-99), `incomes/`, `investments/`, `savings/`, `finance/`, `households/`, `summaries/` — bien modularizado |
| **i18n con Flask-Babel** | Mensajes traducibles con [_()](file:///home/martinm/src/economy/api/services/core/response_service.py#19-27) en routers |
| **Logger con rotación diaria** | `TimedRotatingFileHandler` en [logger_service.py](file:///home/martinm/src/economy/api/services/logs/logger_service.py) |
| **Global error handler** | [app.py](file:///home/martinm/src/economy/api/app.py) captura `Exception`, `HTTPException`, `SQLAlchemyTimeoutError` |
| **CORS configurado** | Origins, methods y headers en [config.py](file:///home/martinm/src/economy/api/config.py) |
| **Soporte SQLite + PostgreSQL** | [config.py](file:///home/martinm/src/economy/api/config.py) maneja ambos motores |
| **Blueprint registration centralizado** | [routers/__init__.py](file:///home/martinm/src/economy/api/routers/__init__.py) con [register_blueprints()](file:///home/martinm/src/economy/api/routers/__init__.py#20-30) |

---

## 🔴 Lo que hay que MEJORAR

### 1. Modelos — Columnas de auditoría ausentes (PRIORIDAD ALTA)

**Problema**: Ningún modelo tiene `created_at`, `updated_at`, ni `deleted_at`.

**Solución**: Crear un mixin `TimestampMixin` en [models/core/base.py](file:///home/martinm/src/economy/api/models/core/base.py):

```python
from sqlalchemy import Column, DateTime, func

class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Para soft delete
```

Y aplicarlo a **todos** los modelos: `class Expense(TimestampMixin, Base):`

---

### 2. Modelos — `Float` para dinero (PRIORIDAD ALTA)

**Problema**: [amount](file:///home/martinm/src/economy/api/schemas/expenses/expense_schema.py#22-29), `balance`, `currentValue`, `pricePerUnit`, `total_amount`, `net_worth`, `total_income`, [total_expenses](file:///home/martinm/src/economy/api/services/expenses/expense_service.py#60-77), etc. usan `Float`.  
`Float` introduce errores de precisión flotante (ej: `0.1 + 0.2 != 0.3`).

**Solución**: Usar `Numeric(precision=12, scale=2)`:

```diff
-amount = Column(Float, nullable=False)
+amount = Column(Numeric(12, 2), nullable=False)
```

**Archivos afectados**: [expense_model.py](file:///home/martinm/src/economy/api/models/expenses/expense_model.py), [income_model.py](file:///home/martinm/src/economy/api/models/incomes/income_model.py), [saving_model.py](file:///home/martinm/src/economy/api/models/savings/saving_model.py), [saving_log_model.py](file:///home/martinm/src/economy/api/models/savings/saving_log_model.py), [investment_log_model.py](file:///home/martinm/src/economy/api/models/investments/investment_log_model.py), [account_model.py](file:///home/martinm/src/economy/api/models/finance/account_model.py), [financial_summary_model.py](file:///home/martinm/src/economy/api/models/summaries/financial_summary_model.py)

---

### 3. Modelos — Naming inconsistente (PRIORIDAD MEDIA)

**Problema**: [InvestmentLog](file:///home/martinm/src/economy/api/models/investments/investment_log_model.py#8-23) usa camelCase en columnas: `currentValue`, `pricePerUnit`, `unitsBought`.

**Solución**: Renombrar a `current_value`, `price_per_unit`, `units_bought` (snake_case como pide la spec).

---

### 4. Modelos — Relationships nombradas en plural donde debería ser singular (PRIORIDAD BAJA)

**Problema**: Un [Expense](file:///home/martinm/src/economy/api/models/expenses/expense_model.py#8-28) pertenece a **un** User, pero la relationship se llama `users`:
```python
users = relationship('User', back_populates='expenses')  # debería ser 'user'
```

Esto afecta a TODOS los modelos: `users`, `sources`, `categories`, `accounts`, `banks`, `households`, `investments`, `savings`.

> [!WARNING]
> Este cambio es cosmético pero consistente con convenciones SQLAlchemy. Requiere actualizar las back_populates correspondientes en ambos lados de cada relación. Puede esperar a una fase posterior.

---

### 5. Modelos — `declarative_base()` deprecated (PRIORIDAD BAJA)

**Problema**: [models/core/base.py](file:///home/martinm/src/economy/api/models/core/base.py) usa `from sqlalchemy.ext.declarative import declarative_base` que está deprecated desde SQLAlchemy 2.0.

**Solución**:
```diff
-from sqlalchemy.ext.declarative import declarative_base
-Base = declarative_base()
+from sqlalchemy.orm import DeclarativeBase
+class Base(DeclarativeBase):
+    pass
```

---

### 6. Modelos — `Source.type` es `String` en vez de [SourceTypeEnum](file:///home/martinm/src/economy/api/models/core/enums.py#29-35) (PRIORIDAD MEDIA)

**Problema**: Ya existe [SourceTypeEnum](file:///home/martinm/src/economy/api/models/core/enums.py#29-35) en [enums.py](file:///home/martinm/src/economy/api/models/core/enums.py), pero `Source.type` es `Column(String)`.

**Solución**: `type = Column(SQLEnum(SourceTypeEnum), default=SourceTypeEnum.income, nullable=False)`

---

### 7. Modelos — Faltan índices en ForeignKeys (PRIORIDAD MEDIA)

**Problema**: La spec pide índices en `user_id`, `account_id`, `category_id`, `household_id`, [date](file:///home/martinm/src/economy/api/services/core/base_service.py#49-53). Ningún FK tiene `index=True`.

**Solución**: Añadir `index=True` a las FK más consultadas:
```python
user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
```

---

### 8. Repository — Usa `session.query()` legacy (PRIORIDAD MEDIA)

**Problema**: Todos los repositories usan el estilo antiguo `self.db.query(Model).filter(...)` que la spec pide evitar.

**Solución**: Migrar al estilo SQLAlchemy 2.0 con `select()`:
```diff
-return self.db.query(Expense).filter(Expense.user_id == user_id).all()
+stmt = select(Expense).where(Expense.user_id == user_id)
+return self.db.execute(stmt).scalars().all()
```

---

### 9. Router — [get_db()](file:///home/martinm/src/economy/api/db/database.py#32-43) se usa con `next()` sin cerrar sesión (PRIORIDAD ALTA)

**Problema**: En los routers, `db = next(get_db())` extrae la sesión del generador pero **nunca ejecuta el bloque `finally`** de [get_db()](file:///home/martinm/src/economy/api/db/database.py#32-43), por lo que la sesión no se cierra correctamente. Esto causa **memory/connection leaks**.

**Solución**: Usar un context manager o Flask `@app.teardown_appcontext`:
```python
# Opción 1: Context manager en cada router
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 10. Seguridad — No hay autenticación ninguna (PRIORIDAD ALTA)

**Problema**: No hay JWT, ni tokens, ni middleware de autenticación. Cualquier endpoint es público. El modelo [User](file:///home/martinm/src/economy/api/models/users/user_model.py#8-29) tiene campo `password` pero no se usa para auth.

**Solución (Fase 2 según roadmap)**:
- Implementar `flask-jwt-extended`
- Crear `auth_routes.py` con login/register/refresh
- Añadir decorator `@jwt_required()` a los endpoints protegidos
- Hashear passwords con `bcrypt` o `argon2`

---

### 11. Seguridad — Password almacenado en texto plano (PRIORIDAD ALTA)

**Problema**: `User.password = Column(String, nullable=False)` — no hay hashing ni salt.

**Solución**: Integrar `werkzeug.security.generate_password_hash` / `check_password_hash` o `argon2-cffi`.

---

### 12. Router — No hay paginación (PRIORIDAD MEDIA)

**Problema**: [get_all()](file:///home/martinm/src/economy/api/services/core/base_service.py#45-48) devuelve TODOS los registros sin límite. Con miles de gastos, esto es un problema de rendimiento grave.

**Solución**: Añadir paginación en `BaseRepository.get_all()`:
```python
def get_all(self, page: int = 1, per_page: int = 20) -> List[T]:
    return self.db.query(self.model).offset((page - 1) * per_page).limit(per_page).all()
```

---

### 13. Repository — Hard delete en vez de soft delete (PRIORIDAD MEDIA)

**Problema**: `BaseRepository.delete()` hace `self.db.delete(obj)` — eliminación física. Con la columna `deleted_at` propuesta, se debería hacer soft delete.

**Solución**:
```python
def delete(self, id: int) -> bool:
    obj = self.get_by_id(id)
    if obj:
        obj.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
    return False
```

Y en [get_all()](file:///home/martinm/src/economy/api/services/core/base_service.py#45-48) / [get_by_id()](file:///home/martinm/src/economy/api/services/core/interfaces.py#12-15) filtrar por `deleted_at IS NULL`.

---

### 14. Config — `SECRET_KEY` por defecto insegura (PRIORIDAD MEDIA)

**Problema**: `SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'` — si no se define la env var, usa una clave **hardcoded**.

**Solución**: En producción, lanzar error si no está definida:
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY and not DEBUG:
    raise ValueError("SECRET_KEY must be set in production")
```

---

### 15. [database.py](file:///home/martinm/src/economy/api/db/database.py) — [init_db()](file:///home/martinm/src/economy/api/db/database.py#45-111) con datos hardcoded (PRIORIDAD BAJA)

**Problema**: [init_db()](file:///home/martinm/src/economy/api/db/database.py#45-111) crea un usuario con datos fake (`"12345678Z"`, `"example@email.com"`) directamente en código. Esto debería ser un seed script separado.

**Solución**: Mover a `scripts/seed.py` y no ejecutarlo en [init_db()](file:///home/martinm/src/economy/api/db/database.py#45-111).

---

### 16. [database.py](file:///home/martinm/src/economy/api/db/database.py) — `echo=True` en producción (PRIORIDAD BAJA)

**Problema**: `engine = create_engine(DATABASE_URL, echo=True, ...)` — logs de SQL visibles siempre.

**Solución**: `echo=Config.DEBUG`

---

## 🟡 Tablas que FALTAN o SOBRAN

### Tabla que podrías necesitar: `recurring_transactions`

Para gastos/ingresos recurrentes (alquiler, nómina, suscripciones Netflix, etc.):

| Campo | Tipo |
|---|---|
| [id](file:///home/martinm/src/economy/api/services/core/interfaces.py#12-15) | Integer PK |
| `name` | String |
| [amount](file:///home/martinm/src/economy/api/schemas/expenses/expense_schema.py#22-29) | Numeric(12,2) |
| `frequency` | Enum (daily, weekly, monthly, yearly) |
| `type` | Enum (income, expense) |
| `next_execution_date` | Date |
| `category_id` | FK |
| `account_id` | FK |
| `user_id` | FK |
| `active` | Boolean |

### Tabla que podrías necesitar: `budgets`

Para definir presupuestos mensuales por categoría:

| Campo | Tipo |
|---|---|
| [id](file:///home/martinm/src/economy/api/services/core/interfaces.py#12-15) | Integer PK |
| `category_id` | FK |
| `user_id` | FK |
| `amount_limit` | Numeric(12,2) |
| `month` | Integer |
| `year` | Integer |

### Tabla `savings` — le falta [category](file:///home/martinm/src/economy/api/repositories/expenses/expense_repository.py#18-21)

A diferencia de Expenses e Incomes, [Saving](file:///home/martinm/src/economy/api/models/savings/saving_model.py#8-24) no tiene `category_id` ni `source_id` como FK (el source está en [SavingLog](file:///home/martinm/src/economy/api/models/savings/saving_log_model.py#7-22)). Valora si el ahorro necesita una categoría (ej: "fondo de emergencia", "vacaciones", "educación").

### Tabla `financial_summary` — ¿sobra?

[FinancialSummary](file:///home/martinm/src/economy/api/models/summaries/financial_summary_model.py#7-23) almacena totales precalculados. Esto se puede calcular al vuelo con queries sobre las tablas transaccionales. Si el volumen de datos es bajo (<100k registros), probablemente sobra y añade riesgo de inconsistencia. Alternativamente, si se mantiene, debería regenerarse automáticamente (no manualmente).

---

## 📋 Resumen por prioridad

| Prioridad | Nº | Cambio |
|---|---|---|
| 🔴 ALTA | 1 | Columnas `created_at`, `updated_at`, `deleted_at` |
| 🔴 ALTA | 2 | `Float` → `Numeric(12,2)` para dinero |
| 🔴 ALTA | 9 | Fix [get_db()](file:///home/martinm/src/economy/api/db/database.py#32-43) / session leak |
| 🔴 ALTA | 10-11 | Autenticación JWT + hash passwords |
| 🟠 MEDIA | 3 | snake_case en [InvestmentLog](file:///home/martinm/src/economy/api/models/investments/investment_log_model.py#8-23) |
| 🟠 MEDIA | 6 | `Source.type` → usar [SourceTypeEnum](file:///home/martinm/src/economy/api/models/core/enums.py#29-35) |
| 🟠 MEDIA | 7 | Índices en FKs |
| 🟠 MEDIA | 8 | Migrar a `select()` style SQLAlchemy 2.0 |
| 🟠 MEDIA | 12 | Paginación |
| 🟠 MEDIA | 13 | Soft delete |
| 🟠 MEDIA | 14 | `SECRET_KEY` segura |
| 🟢 BAJA | 4 | Relationship names singular/plural |
| 🟢 BAJA | 5 | `DeclarativeBase` moderno |
| 🟢 BAJA | 15-16 | Seed data separado, `echo=DEBUG` |

## Verification Plan

Este documento es solo una auditoría/análisis. No hay cambios de código que verificar. Cuando decidamos qué implementar, crearemos un plan de implementación específico con sus tests.
