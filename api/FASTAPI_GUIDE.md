# Guía de la API FastAPI

Este documento explica cómo se inicia y organiza la API, cómo probar sus
endpoints y qué aporta FastAPI en este proyecto.

## Dónde está la documentación

Con la API en ejecución en el puerto `5001`:

- **Swagger UI:** <http://localhost:5001/docs>
- **ReDoc:** <http://localhost:5001/redoc>
- **Especificación OpenAPI en JSON:** <http://localhost:5001/openapi.json>
- **Comprobación de salud:** <http://localhost:5001/health>

Swagger y ReDoc se generan a partir de la aplicación y sus rutas. En Swagger
se pueden consultar los métodos y parámetros, probar solicitudes y autorizarse
con un token JWT. La guía rápida y los comandos de inicio también están en
[README.md](./README.md).

## Cómo iniciar la API

Desde la carpeta `api`:

```bash
uvicorn app:app --host 0.0.0.0 --port 5001 --reload
```

`app:app` significa que Uvicorn importa el módulo `app.py` y sirve el objeto
FastAPI llamado `app`. `--reload` reinicia el proceso cuando detecta cambios y
es apropiado para desarrollo local.

La imagen Docker también inicia Uvicorn en el puerto `5001`. Para conectarse a
la base de datos se utilizan las variables de entorno configuradas en la API;
PostgreSQL es una opción soportada.

## Qué ocurre al recibir una petición

El recorrido general es:

```text
Cliente Angular
    ↓ HTTP
Uvicorn
    ↓ ASGI
Middleware de idioma y CORS
    ↓
Router FastAPI (/api/...)
    ↓ dependencias: JWT y sesión de base de datos
Endpoint
    ↓
Servicio → repositorio → SQLAlchemy → base de datos
    ↓
Respuesta JSON
```

### 1. Creación de la aplicación

En [app.py](./app.py), `create_app()` crea la instancia FastAPI, configura CORS,
el middleware de idioma, las rutas de salud y los manejadores de errores.
Después llama a `register_routers()` para registrar los endpoints.

Las rutas de negocio se montan bajo el prefijo `/api`, definido por la
configuración de desarrollo. Por ejemplo, el login está en
`POST /api/auth/login`.

### 2. Routers y endpoints

Cada área funcional define un `APIRouter` en
[routers/](./routers). Los decoradores describen el método y la ruta, por
ejemplo `@router.get(...)` o `@router.post(...)`.

Los parámetros de ruta, query y cuerpo se declaran en la firma del endpoint.
Cuando el cuerpo usa un esquema Pydantic, FastAPI valida y convierte los datos
antes de ejecutar la función. Si no cumplen el esquema, la petición se rechaza
con un error de validación.

### 3. Dependencias y base de datos

`Depends(...)` permite que FastAPI proporcione recursos al endpoint. En esta
API se usa, por ejemplo, para:

- Obtener una sesión SQLAlchemy mediante `get_db()` en
  [db/database.py](./db/database.py). Se crea una sesión para la petición y se
  cierra al terminar; ante una excepción se hace rollback.
- Verificar JWT mediante las dependencias de
  [auth_dependencies.py](./services/auth/auth_dependencies.py).

La lógica de negocio sigue en los servicios y el acceso a datos en los
repositorios. La migración a FastAPI cambia la capa HTTP; no sustituye ese
flujo.

### 4. Autenticación

El router de autenticación está registrado sin la dependencia global de acceso:

- `POST /api/auth/register` y `POST /api/auth/login` son públicos.
- `POST /api/auth/refresh` requiere un token de tipo refresh.
- `GET /api/auth/me` requiere un token de acceso.

Los demás routers registrados en
[routers/__init__.py](./routers/__init__.py) requieren un token de acceso.
En Swagger, se puede pulsar **Authorize** y proporcionar el JWT de acceso para
probar esas rutas.

### 5. Respuestas, idioma y errores

Las respuestas de la API conservan el sobre existente:

```json
{
  "response": "USER_FOUND",
  "details": "User found."
}
```

`response` es un código estable que el cliente puede interpretar; `details` es
el mensaje legible. La clase `Response` centraliza ese formato en
[response_service.py](./services/core/response_service.py).

El idioma puede seleccionarse con `?lang=es` o mediante la cabecera
`Accept-Language: es`. Si no se solicita español, se usa inglés. Los
catálogos están en [i18n/](./i18n), y se leen desde los archivos `.po` al
iniciar la aplicación.

Los errores de validación, autenticación y excepciones generales tienen
manejadores en [app.py](./app.py). La API traduce los mensajes destinados al
cliente y evita incluir en ellos el texto de excepciones internas.

## Qué mejora FastAPI en esta aplicación

- **Documentación navegable y ejecutable:** `/docs` y `/redoc` se generan desde
  las rutas, sin mantener manualmente una especificación independiente.
- **Validación integrada:** FastAPI usa los esquemas Pydantic y los tipos de
  los endpoints para validar solicitudes y generar parte del contrato OpenAPI.
- **Inyección de dependencias:** la sesión de base de datos y la autenticación
  se declaran junto al endpoint, con ciclo de vida centralizado.
- **Errores HTTP centralizados:** los errores de validación y las excepciones
  comunes pueden mantener una respuesta y localización consistentes.
- **Compatibilidad con ASGI:** el framework admite endpoints asíncronos y
  middleware ASGI, lo que permite adoptar operaciones async cuando las
  dependencias de la aplicación también lo soporten.
- **Menos código de infraestructura HTTP:** rutas, validación, dependencias y
  documentación forman parte del mismo framework.

La mejora inmediata más visible es la validación y documentación automática,
además de una integración clara de dependencias. Esto **no significa que las
consultas actuales sean automáticamente más rápidas**: los endpoints y el
acceso a SQLAlchemy de este proyecto son síncronos. Para obtener beneficios de
I/O asíncrono habría que migrar coordinadamente las rutas y las dependencias de
base de datos.

## Notas sobre la configuración actual

La instancia global se crea con `app = create_app()`. `create_app()` resuelve la
configuración con `get_config()` ([config.py](./config.py)): la variable de
entorno `APP_ENV` selecciona `DevelopmentConfig` (valor por defecto),
`TestingConfig` o `ProductionConfig`. Con `APP_ENV=production`, `create_app()`
ejecuta `ProductionConfig.validate()`, que exige `JWT_SECRET_KEY` y hace fallar
el arranque si falta. En despliegue, fija `APP_ENV=production` (por ejemplo en
docker-compose o en el `.env`).

La configuración de desarrollo activa `INIT_DB_ON_STARTUP` y el seed de datos.
`create_app()` ejecuta esa inicialización desde el ciclo de vida de FastAPI
cuando esa opción está habilitada. La configuración de producción declara
migraciones como estrategia de esquema y se selecciona con `APP_ENV=production`
(ver la sección siguiente).

## Correcciones tras la auditoría de la migración

Noviembre de 2026: auditoría de la migración Flask → FastAPI y tres correcciones
aplicadas sobre el código migrado.

### 1. Parámetro de ruta en `PATCH /banks/{id}` y `DELETE /banks/{id}`

FastAPI resuelve los parámetros del endpoint **por nombre**: el parámetro de la
función debe llamarse igual que la variable declarada en la ruta. Los handlers
declaraban la ruta con `{id:int}` pero el parámetro `bank_id`, de modo que
FastAPI interpretaba `bank_id` como un query param obligatorio y ambas
operaciones fallaban con 400 para cualquier cliente normal. Se renombró
`bank_id` → `id` en [bank_router.py](./routers/finance/bank_router.py), igual
que ya hacía `get_by_id` en el mismo router.

Regla para nuevos endpoints: el nombre entre llaves de la ruta y el del
parámetro de la función deben coincidir (el resto de routers ya lo cumplían).

### 2. Secreto JWT sin fallback silencioso

Antes `_secret_key()` ([jwt_service.py](./services/auth/jwt_service.py)) caía al
secreto de desarrollo committeado cuando faltaba `JWT_SECRET_KEY`, también en
producción: un despliegue sin la variable habría firmado y aceptado tokens con
un secreto público. Ahora:

- `get_config()` ([config.py](./config.py)) selecciona la configuración con
  `APP_ENV`: `development` (por defecto), `testing` o `production`.
- `_secret_key()` usa el secreto de la configuración seleccionada y lanza
  `RuntimeError` si no existe fuera de desarrollo; nunca firma en silencio con
  el secreto de desarrollo.
- `create_app()` ejecuta `ProductionConfig.validate()` al construir la
  aplicación: con `APP_ENV=production` y sin `JWT_SECRET_KEY` el arranque falla
  de forma visible en lugar de arrancar vulnerable.

En desarrollo el comportamiento no cambia: sin variable de entorno se sigue
usando el secreto de desarrollo de `DevelopmentConfig`.

### 3. Tokens emitidos por la API Flask anterior

Se verificó contra el código fuente de `flask-jwt-extended` 4.7.1 (la librería
de la API Flask) que sus tokens incluyen los claims `fresh`, `iat`, `jti`,
`type` (`"access"` o `"refresh"`), `sub`, `nbf` y `exp`, y que el antiguo
`AuthService` añadía `role` y `email` al access token. La implementación PyJWT
actual usa exactamente los mismos nombres de claims, por lo que los refresh
tokens emitidos antes de la migración siguen siendo válidos siempre que se
conserve el mismo `JWT_SECRET_KEY`; no hizo falta modificar `decode_token`.

El test de regresión [tests/test_jwt_service.py](./tests/test_jwt_service.py)
construye tokens con la forma exacta de flask-jwt-extended y comprueba que se
aceptan con su tipo correcto, que un refresh no sirve como access, y el
comportamiento de `_secret_key()` según `APP_ENV`.
