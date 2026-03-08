# Backend Architecture

Este proyecto utiliza una arquitectura en capas inspirada en **Clean
Architecture** y **Service Layer + Repository Pattern**.

Objetivos:

-   separación de responsabilidades
-   reutilización de código
-   desacoplamiento
-   testabilidad
-   escalabilidad

También se aplican principios **SOLID**, especialmente:

-   **ISP --- Interface Segregation Principle**
-   **DIP --- Dependency Inversion Principle**

------------------------------------------------------------------------

# Arquitectura general

Flujo de una petición:

Frontend → Router → Service → Repository → Database

Arquitectura real del proyecto:

Frontend → user_router.py → UserService → BaseService → UserRepository →
BaseRepository → SQLAlchemy → Database

------------------------------------------------------------------------

# Estructura del proyecto

routers/ user_router.py

services/ core/ interfaces.py base_service.py users/ user_service.py

repositories/ core/ base_repository.py users/ user_repository.py

schemas/ users/ user_schema.py

models/ user.py

------------------------------------------------------------------------

# Router Layer

Ejemplo: routers/user_router.py

Responsabilidades:

-   definir endpoints HTTP
-   validar requests
-   devolver responses

Ejemplo:

@router.post("/users") def create_user(data: UserCreate, db: Session =
Depends(get_db)): service = UserService(db) return service.create(data)

Conversión automática:

JSON → Pydantic Schema

------------------------------------------------------------------------

# Inyección de dependencias

El router inyecta la sesión de base de datos.

db: Session = Depends(get_db)

Luego crea el servicio:

service = UserService(db)

Esto es **Dependency Injection**.

El servicio no crea la conexión, la recibe.

------------------------------------------------------------------------

# Service Layer

Archivo: services/users/user_service.py

class UserService(BaseService\[User, UserRead, UserCreate,
UserUpdate\]):

El Service contiene:

-   lógica de negocio
-   validaciones
-   reglas de dominio

Ejemplo:

def create(self, data: UserCreate) -\> UserRead:

    if self.repository.find_by_dni(data.dni):
        raise ValueError("User with this DNI already exists")

    data.password = hash_password(data.password)

    return super().create(data)

------------------------------------------------------------------------

# BaseService

Archivo: services/core/base_service.py

class BaseService( ICRUDService\[ReadT, CreateT, UpdateT\],
Generic\[ModelT, ReadT, CreateT, UpdateT\] ):

BaseService implementa CRUD genérico.

Dependencias del constructor:

-   db
-   model
-   repository
-   read_schema

Ejemplo:

super().\_\_init\_\_( db=db, model=User, repository=UserRepository(db),
read_schema=UserRead )

Responsabilidades:

-   lógica CRUD genérica
-   conversión ORM ↔ schema
-   delegar persistencia al repository

------------------------------------------------------------------------

# Repository Layer

Archivo: repositories/users/user_repository.py

class UserRepository(BaseRepository\[User\]):

UserRepository hereda de BaseRepository.

Operaciones ya disponibles:

-   create
-   get_by_id
-   get_all
-   update
-   delete
-   search
-   count

Ejemplo de consulta específica:

def find_by_dni(self, dni: str): stmt =
self.\_base_query().where(User.dni == dni) return
self.db.execute(stmt).scalar_one_or_none()

------------------------------------------------------------------------

# BaseRepository

Archivo: repositories/core/base_repository.py

Implementa CRUD genérico usando SQLAlchemy.

Ejemplo:

def create(self, obj): self.db.add(obj) self.db.commit()
self.db.refresh(obj) return obj

Responsabilidades:

-   persistencia
-   queries
-   transacciones

------------------------------------------------------------------------

# Modelos de datos

Existen tres representaciones de datos.

JSON (API)

{ "name": "Juan", "email": "juan@gmail.com", "dni": "12345678A" }

Schemas (Pydantic)

UserCreate UserUpdate UserRead

Models (SQLAlchemy)

User

------------------------------------------------------------------------

# Flujo de datos

JSON ↓ UserCreate (Pydantic) ↓ User (SQLAlchemy Model) ↓ Database ↓ User
(ORM) ↓ UserRead (Pydantic) ↓ JSON response

------------------------------------------------------------------------

# Interfaces y ISP

Archivo: services/core/interfaces.py

Interfaces definidas:

-   IReadService
-   ICreateService
-   IUpdateService
-   IDeleteService
-   ISearchService

Todas se combinan en:

ICRUDService

Esto aplica **Interface Segregation Principle (ISP)**.

Los clientes dependen solo de lo que necesitan.

------------------------------------------------------------------------

# Dependency Inversion Principle (DIP)

El Service no accede directamente a SQLAlchemy.

Usa un Repository.

Router ↓ Service ↓ Repository ↓ Database

Esto desacopla la lógica de negocio del acceso a datos.

------------------------------------------------------------------------

# Herencia en la arquitectura

Services

ICRUDService ↑ BaseService ↑ UserService

Repositories

BaseRepository ↑ UserRepository

------------------------------------------------------------------------

# Responsabilidades por capa

Router → HTTP

Service → lógica de negocio

BaseService → CRUD genérico

Repository → consultas específicas

BaseRepository → acceso genérico a datos

Database → persistencia

------------------------------------------------------------------------

# Beneficios de la arquitectura

-   código desacoplado
-   reutilización
-   fácil testing
-   escalabilidad
-   arquitectura limpia
