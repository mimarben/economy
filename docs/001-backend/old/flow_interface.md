POSTMAN: GET http://localhost:8000/expenses-categories/
    ↓
1. FastAPI router recibe petición
    ↓
2. Endpoint llama: service.get_all()
    ↓ Depends(db)
3. FastAPI crea/injecta: db = Session()
    ↓
4. Endpoint: service = ExpensesCategoryService(db)
    ↓
5. ExpensesCategoryService.__init__(db)
    ↓ super().__init__(...)
6. BaseService.__init__(
       db=db,
       model=ExpensesCategory,
       repository=ExpensesCategoryRepository(db),
       read_schema=ExpenseCategoryRead
   )
    ↓
7. repository = ExpensesCategoryRepository(db)
    ↓
8. BaseService.get_all():
    objs = repository.get_all()  ← SQL ejecutado
    ↓
9. ExpensesCategoryRepository.get_all():
    return db.query(ExpensesCategory).all()
    ↓ SQLAlchemy → SELECT * FROM expenses_categories
10. DB devuelve: [ExpensesCategory(id=1,name="Comida"), ...]
    ↓
11. BaseService:
    return [ExpenseCategoryRead.model_validate(o) for o in objs]
    ↓ Pydantic convierte ORM → schemas
12. Endpoint recibe: [ExpenseCategoryRead(id=1,name="Comida"), ...]
    ↓ response_model
13. FastAPI serializa → JSON
    ↓
POSTMAN: 200 OK
[
  {"id":1,"name":"Comida","description":"Gastos comida"},
  {"id":2,"name":"Transporte","description":"Gastos transporte"}
]


1. POSTMAN: GET http://localhost:5000/banks

2. app.py → Blueprint 'banks' (routes/banks.py)

3. ROUTER Línea 64: @router.get("/banks")

4. ROUTER Línea 65: def list_all():

5. ROUTER Línea 66: db = next(get_db()) → db/database.py

6. ROUTER Línea 67: service: IReadService = _get_read_service(db)

7. ROUTER Línea 29: return BankService(db)

8. SERVICES/bank_service.py Línea 25: BankService.__init__(db)

9. SERVICES/bank_service.py Línea 26: super().__init__()

10. SERVICES/base_service.py Línea 25: BaseService.__init__(db, model=Bank ← models/models.py,    repository=BankRepository(db) ← repositories/bank_repository.py Línea 15,
    read_schema=BankRead ← schemas/bank_schema.py Línea 10

11. ROUTER Línea 68: results = service.get_all()

12. BankService.get_all() → base_service.py Línea 45: def get_all()

13. BASESERVICE Línea 46: objs = self.repository.get_all()

14. REPOSITORY/bank_repository.py Línea 15 → BaseRepository.get_all()

15. SQLAlchemy: self.db.query(Bank).all()

16. BASE DE DATOS: SELECT * FROM banks

17. DB → [Bank ORM objects (id=1,name="BBVA"), ...]

18. BASESERVICE Línea 48: [self.read_schema.model_validate(o) for o]

19. SCHEMAS/bank_schema.py Línea 5: BankRead.model_validate()

20. ROUTER Línea 69: jsonify([r.model_dump() for r in results])

21. SCHEMAS/bank_schema.py Línea 20: r.model_dump() → dict

22. POSTMAN: [{"id":1,"name":"BBVA","active":true}, ...]


| Fichero                         | Para qué sirve         | Líneas clave que se ejecutan            |
| ------------------------------- | ---------------------- | --------------------------------------- |
| repositories/bank_repository.py | Habla SOLO con BD      | super().__init__(db, Bank) → delega SQL |
| services/interfaces.py          | Contratos (NO ejecuta) | IReadService → IDE/mypy valida tipos    |
| services/base_service.py        | Lógica CRUD genérica   | Líneas 45-48: get_all()                 |
| services/bank_service.py        | Configura BaseService  | Líneas 25-30: pasa model/repo/schema    |
| schemas/bank_schema.py          | Valida/serializa JSON  | model_validate(), model_dump()          |
| routes/banks.py                 | HTTP + ISP             | Líneas 64-70: _get_read_service()       |

REPOSITORIES ✅ Hablan con BD (SQLAlchemy)
   - Solo saben de models (Bank)
   - NO saben de Pydantic (BankRead)

BASESERVICE ✅ Lógica reutilizable  
   - Convierte ORM→Pydantic
   - Funciona para Bank/User/Product...

BankService ✅ "Adaptador específico"
   - Dice: "usa Bank + BankRepo + BankRead"

INTERFACES ✅ Seguridad tipo (runtime NO)
   - Router pide IReadService → IDE valida que tenga get_all()
   - ISP = Router crea servicio específico por operación

ROUTER ✅ HTTP + validación
   - Valida request.json con BankCreate.model_validate()
   - ISP: cada endpoint pide SU interfaz
