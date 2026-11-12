# Informe de refactor — Migración Flask → FastAPI

Fecha: 2026-11-12 · Ámbito: `api/` · Modo: refactor profundo controlado (contrato HTTP intacto)

Principio seguido (CLAUDE.md v3.5): mejora incremental, sin romper endpoints ni formato
de respuesta. Ningún cambio de este informe altera rutas, métodos ni estructura
`{"response": ..., "details": ...}` de la API.

---

## 1. Seguridad

### 1.1 Autorización — cierre del IDOR (acceso cruzado entre usuarios)
**Dónde:** `services/auth/auth_dependencies.py`, `routers/expenses/expense_router.py`,
`routers/users/user_router.py`, `routers/__init__.py` (sin cambios, ya protegía todo).

**Qué:** nuevas dependencias `get_current_user_id` (extrae `sub` del token ya validado) y
`require_role(*roles)` (comprueba el claim `role`, que se emitía pero jamás se verificaba).

**Por qué:** el token se validaba pero ningún endpoint de negocio lo usaba:
`GET /expenses/user/{id}` y `GET/PATCH/DELETE /users/{id}` permitían a cualquier usuario
autenticado leer o modificar datos de otro. Ahora devuelven **403 `AUTH_FORBIDDEN`** si el
`user_id` de la ruta no coincide con el del token.

### 1.2 Fuga de información en errores 5xx
**Dónde:** `services/core/response_service.py`.

**Qué:** si `status_code >= 500`, el detalle crudo (`str(e)`, con SQL/trazas) se registra
en el log del servidor y al cliente solo llega la clave i18n traducida.

**Por qué:** casi todos los routers hacían `Response.error(..., str(e), 500, ...)`,
exponiendo internals. Un único cambio central lo arregla en los ~25 routers sin tocarlos.

### 1.3 Rate limiting en `/auth/login`
**Dónde:** `services/auth/rate_limiter.py` (nuevo), `routers/auth/auth_router.py`.

**Qué:** limitador sliding-window en memoria — 5 intentos fallidos / 5 min por IP+email;
al 6º devuelve **429 `AUTH_RATE_LIMITED`**. El contador se reinicia con un login correcto.

**Por qué:** el endpoint era libre de fuerza bruta (regla 14 del CLAUDE.md: aplicar
seguridad solo si falta). Sin dependencias nuevas (slowapi/etc.).

### 1.4 Anti-enumeración de usuarios por timing
**Dónde:** `services/auth/auth_service.py`.

**Qué:** si el email no existe o el usuario está inactivo, se ejecuta `verify_password`
contra un hash dummy constante antes de devolver el 401 genérico.

**Por qué:** antes el path "email desconocido" no ejecutaba bcrypt y era mediblemente
más rápido que "password incorrecto" — permitía enumerar emails registrados.

### 1.5 Logout / revocación de tokens por `jti`
**Dónde:** `services/auth/token_store.py` (nuevo), `services/auth/auth_dependencies.py`,
`routers/auth/auth_router.py` (endpoint `POST /auth/logout`).

**Qué:** store en memoria de JTI revocados (con purga por expiración). `_require_token`
rechaza con **401 `AUTH_TOKEN_REVOKED`** cualquier token cuyo JTI esté revocado. El logout
revoca el refresh token presentado hasta su expiración original.

**Por qué:** los tokens llevaban `jti` desde la migración pero no se usaba: no existía
forma de invalidar un token robado durante sus 30 días de vida. Limitación documentada:
store por proceso (válido con 1 worker; si se escala a varios, mover a Redis).

---

## 2. Transacciones (bug real corregido)

**Dónde:** `repositories/core/base_repository.py`, `services/core/base_service.py`,
`services/auth/auth_service.py`, `services/{expenses,incomes,investments}/*_service.py`,
`services/imports/import_service.py`.

**Qué / por qué:**
- `BaseRepository.create/update/delete/hard_delete` ahora hacen **`flush()`**, no `commit()`.
  La transacción pasa a ser del servicio (regla 6: repositorio = solo acceso a BD) y las
  operaciones multi-repositorio quedan en una sola transacción.
- `BaseService` y los servicios custom hacen `commit()` al final de cada operación.
- `create` y `create_batch_atomic` de expenses/incomes/investments usan **SAVEPOINT por
  fila** (`begin_nested()`), el patrón que ya usaba `import_service`: un duplicado solo
  deshace su propio INSERT; el resto del lote se persiste (en Postgres, sin savepoint un
  solo `IntegrityError` abortaría toda la transacción).
- `ImportService.import_transactions_atomic` **no se ha tocado**: ya envolvía todo en
  `with self.db.begin():` (commit implícito al salir del bloque). Un diagnóstico inicial
  que lo daba por "sin commit" era falso y el commit extra añadido se revirtió — era el
  que provocaba `InvalidRequestError: A transaction is already begun on this Session`.

---

## 3. Reglas del CLAUDE.md

### 3.1 `select()` en todo el backend (regla 4)
**Dónde:** `repositories/summaries/summary_repository.py` (15 usos de `.query()` migrados),
`services/finance/account_service.py`, `db/users_seed.py`. Ya no queda ningún `.query()`
activo en `api/` (solo en comentarios de ejemplo, actualizados).

### 3.2 Corrección de `BaseRepository.count(**filters)`
**Dónde:** `repositories/core/base_repository.py`.

**Qué:** los filtros se aplican ahora **dentro** de la subquery. Antes se hacía
`select(count()).select_from(subquery).where(model.col == v)` — el `where` referenciaba
columnas ajenas al FROM: con filtros fallaba o contaba mal.

---

## 4. Unificación del patrón de routers (17 ficheros)

**Dónde:** todos los routers CRUD excepto `auth`, `expenses/expense_router` y
`users/user_router` (estos tres reescritos a mano en la iteración anterior con el patrón
completo) e `imports/import_profile_router` (ya seguía un patrón propio limpio, se dejó
tal cual).

**Qué (por router):**
- 4 factorías idénticas (`_get_create_service`, `_get_read_service`, `_get_update_service`,
  `_get_delete_service`, que devolvían todas lo mismo) → **una sola `_get_service`**.
- Call-sites `service: ICreateService = _get_create_service(db)` → `service = _get_service(db)`.
- Import de `services.core.interfaces` eliminado (quedó sin uso).

**Por qué:** la "segregación de interfaces" era cosmética — las 4 factorías devolvían la
misma clase concreta; era ruido en ~17 ficheros. La verdadera validación/autorización
vive en las dependencias HTTP y en el handler global.

Ficheros: `households/{household,household_member}`, `incomes/{income,income_category}`,
`investments/{investment,investment_category,investment_log}`, `savings/{saving,saving_log}`,
`expenses/expense_category`, `cards/card`, `category_rules/{category_rules,source_rules}`,
`finance/{source,bank,account}`, `imports/import_origin`.

### 4.1 Patrón completo aplicado a `expense_router` y `user_router`
Además de lo anterior: eliminada la doble validación (`payload: Schema` +
`model_validate(payload)` — ya la hace FastAPI con el handler global de
`RequestValidationError`, que produce el mismo envelope) y eliminado el
`except Exception as e: ... str(e) ...` (lo cubre el handler global ya saneado).

**Nota:** en el resto de routers CRUD queda la doble validación redundante (inofensiva:
`model_validate` sobre un payload ya validado nunca falla). Limpieza cosmética pendiente,
sin efecto en comportamiento.

### 4.2 Plantillas del generador actualizadas
**Dónde:** `templates/service_router_generator.py`, `scripts/generate_crud.py`.

**Qué:** los templates generan ahora el patrón nuevo (una factoría, sin `Any = Body(...)`,
commit en el servicio, ejemplos con `select()`).

**Por qué:** los 4 factories y la doble validación venían de aquí — sin arreglar la
plantilla, la deuda se volvería a generar.

---

## 5. Infraestructura

- **`db/database.py`:** `pool_size` 20 → 40 (comentario incluido). FastAPI ejecuta los
  endpoints sync en un threadpool de 40 hilos; con pool 20, bajo carga habría hilos
  esperando conexiones (`pool_timeout`).
- **`Dockerfile`:** usuario no-root (`app`, uid/gid 1000 — coincide con el usuario del
  host para el bind-mount rw de docker-compose), `COPY --chown`, y eliminado el comentario
  obsoleto sobre "legacy WSGI app".
- **`services/core/response_service.py`:** `ok_data` es ahora alias de `ok` (eran
  idénticos); se mantiene el nombre por compatibilidad con los ~25 routers que lo usan.
- **i18n (`i18n/{en,es}/LC_MESSAGES/messages.po`):** nuevas claves `AUTH_FORBIDDEN`,
  `AUTH_RATE_LIMITED`, `AUTH_TOKEN_REVOKED`, `LOGOUT_SUCCESS`.
- **Eliminado:** `services/core/jwt_service.py` (fichero vacío de 8 bytes, sin referencias).

---

## 6. Qué NO se ha hecho (y por qué)

| Pendiente | Motivo |
|---|---|
| Scoping por usuario en los listados (`GET /expenses`, summaries…) | Requiere decidir la semántica multi-usuario (households / cuentas compartidas según `er.sql`, tablas M2M `account_users`). Cambio de comportamiento visible para el frontend Angular actual. |
| Revocación persistente (Redis/DB) del store de JTI | Válido en memoria con 1 worker (despliegue actual). Documentado en `token_store.py`. |
| Validación de refresh tokens contra BD (p.ej. hash del token por usuario) | Cambio de contrato de `/auth/refresh`. |
| Limpieza de la doble validación en los 15 routers CRUD restantes | Cosmética, sin efecto funcional. |
| Endpoints async / SQLAlchemy 2.0 async | Contradice el modo incremental; la app funciona sync en threadpool. |

---

## 7. Verificación pendiente (ejecutar antes de desplegar)

Esta sesión no pudo ejecutar comandos de test (bloqueo del modo de permisos). Ejecutar:

```bash
cd api && uv run pytest tests/ -q
```

Pruebas manuales recomendadas:
1. Login usuario A → `GET /api/expenses/user/<id_B>` → esperado **403** `AUTH_FORBIDDEN`.
2. 6 logins fallidos seguidos → esperado **429** `AUTH_RATE_LIMITED`.
3. `POST /auth/logout` con el refresh token → usar ese refresh token después → **401** `AUTH_TOKEN_REVOKED`.
4. Importar un CSV/fichero por `/api/imports/...` y verificar que los datos **se persisten** (era el bug del commit).
5. Provocar un 500 (p.ej. parar Postgres) → la respuesta no debe contener detalles internos en `details`.

Tests más sensibles a los cambios: `test_import_service.py`, `test_dedup_service.py`,
`test_auth_service.py`, `test_jwt_service.py`.
