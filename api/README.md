http://localhost:8000/docs
http://localhost:8000/redoc

# Documentation

[Pydantic and SqlAlchemi](https://medium.com/@melthaw/using-pydantic-for-data-validation-with-sqlalchemy-b15e4497cfb4)

for babel



1️⃣ Extraer

```python
pybabel extract -F babel.cfg -o messages.pot .
```

✔ Se crea/actualiza:

/api/messages.pot

2️⃣ Actualizar idiomas

```python
pybabel update -i messages.pot -d i18n
```

✔ Actualiza:

/api/i18n/en/LC_MESSAGES/messages.po
/api/i18n/es/LC_MESSAGES/messages.po

Crea los mo
pybabel compile -d /home/miguel/src/economy/api/i18n


```python
pybabel compile -d /home/miguel/src/economy/api/i18n
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d i18n
```

## Solo la pimera vez.

```python
pybabel init -i messages.pot -d translations -l en
pybabel init -i messages.pot -d translations -l es
```

```python
pybabel init -i messages.pot -d /home/miguel/src/economy/api/i18n -l en
pybabel init -i messages.pot -d /home/miguel/src/economy/api/i18n -l es
```

# Compile to view the text modifications

```python
pybabel compile -d /home/miguel/src/economy/api/i18n
```




# ALEMBIC

```

for alembic cuando no hay base  de datos

```python
 alembic init alembic
 alembic revision --autogenerate -m "Name nullable-false"
 alembic upgrade head
```

 # Upgrade to the latest revision

```python
alembic upgrade head
```

# Upgrade to a specific revision
```python
alembic upgrade <revision_id>
```

# Check current revision

```python
alembic current
```

# Downgrade to a specific revision

```python
alembic downgrade <revision_id>
```

# Pydantic

https://stackoverflow.com/questions/67699451/make-every-field-as-optional-with-pydantic


# UV VENV

```python
uv venv /home/miguel/venvs/economy-env --python 3.13.7

source /home/miguel/venvs/economy-env/bin/activate

uv sync --active
```

python app.py tiene que tener la ruta de la base de datos en la variable de entrono.

No funciona bien el uv en nfs ni samba o no lo he conseguido arreglar


```python
uv pip compile pyproject.toml --output-file requirements.txt  
```

Con Docker

```python
docker build -t flask-dev .
docker run --rm -p 5001:5001 --env-file .env flask-dev
```

# Estructura y patrones.

- Definir contratos formales

- Aplicar Interface Segregation Principle (ISP)

- Aplicar Dependency Inversion Principle (DIP)

- Aplicar Single Responsibility Principle (SRP)

- Aplicar inyección de dependencias (Dependency Injection)



También existen dos tipos de objetos de datos:

Schemas (Pydantic) → Models (SQLAlchemy) → Database


---

# Estructura de carpetas relevante

routers/
user_router.py

services/
core/

interfaces.py

base_service.py

users/
user_service.py

repositories/

core/
base_repository.py

users/
user_repository.py

models/
user.py

schemas/users/
user_schema.py


---

# 1. interfaces.py

Archivo:



Define **interfaces de servicio**.

Ejemplo:

```python
class IReadService(ABC, Generic[TRead]):

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[TRead]:
        pass

``` 

Estas interfaces definen el contrato que debe cumplir un servicio.

Todo CRUD Service debe tener:
- create
- get_by_id
- get_all
- update
- delete
- search
- count

ISP (Interface Segregation Principle)

Un cliente puede depender solo de lo que usa.

Un servicio de reporting podría usar solo:

- IReadService
- ISearchService

sin depender de:

- create
- update
- delete

# 2. base_service.py

services/core/base_service.py

```python
class BaseService(
    ICRUDService[ReadT, CreateT, UpdateT],
    Generic[ModelT, ReadT, CreateT, UpdateT]
):

``` 

BaseService:

Implementa la interfaz ICRUDService

Usa generics para poder reutilizarse con cualquier modelo.

Ejemplo de uso:

- UserService
- ProductService
- OrderService

 ## Constructor de BaseService

```python
def __init__(
    self,
    db: Session,
    model: Type[ModelT],
    repository: Any,
    read_schema: Type[ReadT]
):
``` 

**Aquí se inyectan dependencias.**

- db
- model
- repository
- read_schema

Ejemplo:

```python
  db = Session
  model = User
  repository = UserRepository
  read_schema = UserRead
```

# 3. user_service.py


```python
class UserService(BaseService[User, UserRead, UserCreate, UserUpdate]):
``` 

UserService HEREDA de BaseService

Por tanto ya tiene **implementado**:

- create
- get_by_id
- get_all
- update
- delete
- search
- count

Inyección de dependencias en UserService

```python
def __init__(self, db: Session):
    super().__init__(
        db=db,
        model=User,
        repository=UserRepository(db),
        read_schema=UserRead
    )
``` 

Aquí ocurre la inyección de dependencias.

Se inyecta:
- db session
- repository
- model
- schema

Sobreescritura de métodos

UserService puede añadir lógica de negocio.

def create(self, data: UserCreate) -> UserRead:

Luego se delega al BaseService.

```python
return super().create(data)
``` 

# 4. user_repository.py

habla con la base de datos. Aquí viven las consultas SQLAlchemy.

```python
def find_by_dni(self, dni: str):
    stmt = self._base_query().where(User.dni == dni)
    return self.db.execute(stmt).scalar_one_or_none()
```

- queries
- persistencia
- transacciones

# 5. base_repository.py

Implementa operaciones CRUD genéricas.

- create
- get_by_id
- get_all
- update
- delete
- search
- count


# 6. user_router.py

```python
@router.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create(data)
```

# Herencias dos capas.

Correcto, y es un punto importante que conviene dejar claro en la documentación.
En tu arquitectura hay dos jerarquías de herencia principales:

1️⃣ Services

2️⃣ Repositories


# Herencia en la capa Repository

Los repositories siguen una estructura similar a los services:  
existe una **clase base genérica** que implementa operaciones comunes y luego cada entidad tiene su repository específico.


Esto significa que UserRepository ya tiene todas las operaciones CRUD implementadas por BaseRepository.

Relación entre Service y Repository

El service usa el repository para acceder a los datos.

class UserService(BaseService[User, UserRead, UserCreate, UserUpdate]):

```python
    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=User,
            repository=UserRepository(db),
            read_schema=UserRead
        )
```
Aquí ocurre una inyección de dependencias.

- db
- repository
- model
- schema

Resumen de herencia
### Services

ICRUDService (interface) <- BaseService (class) <- UserService (class)

### Repositories

BaseRepository <- UserRepository (class) 



# Ruta peticiones

## Petición del frontend

```bash
POST /users
GET /users/1
```

Router --> UserService --> BaseService --> UserRepository --> BaseRepository --> SQLAlchemy --> Database


