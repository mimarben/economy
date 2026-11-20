# Auditoría de UX, Productividad e Importación — Economy

- **Fecha de la auditoría:** 2026-11-13
- **Alcance:** auditoría estática de solo lectura del repositorio `/mnt/SRC/dev/economy` (backend FastAPI + SQLAlchemy + PostgreSQL, frontend Angular 21 + Angular Material, IA local llama.cpp).
- **Etiquetas usadas:** [CONFIRMADO] = verificado en código/configuración abierta durante esta auditoría, con ruta y línea; [HIPÓTESIS] = razonado pero no comprobado; [NO VERIFICABLE] = requiere datos de runtime, BD real o extractos reales.
- **Convención de evidencia:** `ruta:línea` + nombre de función/clase/componente. Las rutas son relativas a la raíz del repo.
- **Objetivo del usuario:** importar extractos (ING, Trade Republic y otras entidades) rápido y sin duplicados, revisar solo excepciones, y obtener una visión fiable de gastos, ingresos, ahorro, saldos, patrimonio e inversiones.

> ⚠️ **ADVERTENCIA PREVIA (Paso 0, copia de seguridad).** No he podido confirmar una copia de seguridad reciente de la base de datos. Existe el mecanismo (`backups/backup_postgres.sh`, retención de 7 días vía `find ... -mtime +7 -delete` en backup_postgres.sh:15-16), pero el único dump presente es `economy_2026-06-04_08-51.dump` (solo he consultado nombres y fechas de fichero, no contenido). Como la retención es de 7 días y el dump sobrevivió 5 meses, el cron documentado en `backups/README.md` no parece estar ejecutándose. Se recomienda restaurar el cron **antes** de implementar cualquier mejora. [CONFIRMADO por fechas de ficheros + script; el contenido del dump no fue leído]

---

## 1. Resumen ejecutivo

Economy ya tiene un motor de importación real y bien encaminado: parseo XLSX en el navegador con perfiles de columnas por entidad ([CONFIRMADO] `client/src/app/services/import/excel-parser.service.ts:69-133`, `ExcelParserService.parse`), deduplicación por huella determinista ([CONFIRMADO] `api/services/core/dedup_service.py:29-46`, `generate_dedup_hash`), importación atómica all-or-nothing ([CONFIRMADO] `api/services/imports/import_service.py:35`, `import_transactions_atomic`), clasificación por reglas regex con prioridad ([CONFIRMADO] `api/services/rules/categorization_service.py:116-158`, `categorize_transaction`), y un pipeline de IA local que existe pero está **desconectado** del flujo ([CONFIRMADO] bloque comentado en `client/src/app/features/import/excel/excel-import.component.ts:342-373`; `api/services/imports/import_service.py:33` instancia `CategorizationService(db)` sin servicio de IA).

Sin embargo, hoy **el flujo completo pierde movimientos en silencio y no deja revisar lo importado**, que es justo el trabajo que Excel hace mejor para el usuario:

1. **Se descartan filas sin categoría en silencio.** Al confirmar la importación, las filas marcadas que no tienen categoría se eliminan del payload sin aviso: solo se envían las que tienen `suggestedCategoryId` ([CONFIRMADO] `client/src/app/features/import/excel/excel-import.component.ts:508-513`, `confirmImport`). El toast de éxito solo informa de insertadas/duplicadas. El usuario cree que importó 200 filas y se importaron menos. [CONFIRMADO]
2. **Las listas solo muestran 50 movimientos, sin orden estable.** `GET /expenses` usa el default de `BaseService.get_all(page=1, per_page=50)` ([CONFIRMADO] `api/services/core/base_service.py:46`; router sin parámetros en `api/routers/expenses/expense_router.py:66-77`; frontend sin paginación en `client/src/app/services/core/base-crud.service.ts:41`, `getAll`), y `BaseRepository.get_all` no tiene `ORDER BY` ([CONFIRMADO] `api/repositories/core/base_repository.py:34-36`). Tras unas semanas de importaciones, la revisión post-importación en listas es imposible. [CONFIRMADO]
3. **Las transferencias propias no existen como concepto y distorsionan los totales.** No hay tabla, modelo, endpoint ni UI de transferencias entre cuentas propias (NO ENCONTRADO: revisadas las 22 tablas de `docs/003-database/er.sql`; grep "transfer" en `api/**.py` → solo `ActionEnum.TRANSFER` en `api/models/core/enums.py:40`, usado por `investments_logs`). La salida cuenta como gasto y la entrada como ingreso en los resúmenes. Además, el flag `ignore_in_analysis` — diseñado justamente para esto — **no se aplica en ninguna consulta de resumen** ([CONFIRMADO] `api/repositories/summaries/summary_repository.py`: ninguna de sus 6 consultas filtra `ignore_in_analysis`; p. ej. `get_totals_by_category` en líneas 35-47 y `get_income_vs_expense` en 186-205). [CONFIRMADO]
4. **Reversión y conciliación: imposibles hoy.** No hay tabla de lotes ni vínculo movimiento→lote (NO ENCONTRADO: grep `import_batch|batch_id|ImportBatch` en `api/**.py` → 0 resultados; er.sql completo sin tabla de lotes). El `balance` del extracto se lee y se muestra en la preview ([CONFIRMADO] `excel-parser.service.ts:107`, `excel-import.component.html:164-169`) pero **no se envía al backend** (no existe el campo en `api/schemas/imports/import_schema.py:35-41`) y no hay contraste con saldo calculado (NO ENCONTRADO: grep `reconcil|saldo_inicial|opening_balance|closing_balance` → 0 resultados). [CONFIRMADO]

**Por qué Excel gana hoy:** en Excel el usuario edita en celda, filtra, ordena, hace find&replace, deshace y borra filas sobrantes sin límites; en Economy el mismo trabajo requiere 6 selectores de catálogo antes del fichero, revisión fila a fila sin acciones en bloque, y luego los movimientos no aparecen en las listas (límite de 50 sin orden). [CONFIRMADO por código; el comparativo detallado está en las secciones 5.H y 6]

**La buena noticia:** casi todos los P0/P1 se resuelven **sin reescribir nada** (regla CLAUDE.md) y la mayoría **sin tocar el esquema**: orden+paginación en listados, aplicar `ignore_in_analysis` en resúmenes, contar y avisar de las filas excluidas, ampliar formatos de fecha, deduplicación con contador de ocurrencias, incluir filas soft-borradas en el dedup, y cablear la IA ya existente como fallback. Solo la reversión por lotes y el modelo de transferencias requieren migración (una tabla `import_batches` + FK nullable `batch_id`; y en su día un modelo de transferencia o un `movement_type`).

**Criterios de éxito (sección 14):** de los 10 objetivos planteados, 7 son alcanzables a corto plazo con cambios de código sin esquema; "clasificación ≥90% automática" requiere además aprendizaje de correcciones (hoy: 0% — editar una categoría no crea ninguna regla; [CONFIRMADO] `api`/frontend: la actualización va por `ExpenseService.update` → `BaseService.update` sin tocar `category_rules`) y "transferencias ≥95% emparejadas" requiere el modelo de transferencias (hoy: 0%). [CONFIRMADO]

---

## 2. Arquitectura y flujo actual (basada en código real)

### 2.1 Stack y servicios

| Capa | Tecnología | Evidencia |
|---|---|---|
| Backend | FastAPI + SQLAlchemy 2 (select()), PostgreSQL 18, Alembic | [CONFIRMADO] `api/app.py:33` (`FastAPI(title="Economy API")`), `docker-compose.yml:61` (imagen `postgres:18`), `api/alembic/` con 15 versiones |
| Frontend | Angular 21.2.1 + Angular Material, ngx-translate, hot-toast, SheetJS (xlsx), chart.js/ng2-charts | [CONFIRMADO] `client/package.json:13-35` |
| IA local | llama.cpp server con qwen2.5-7b-instruct (Q4_K_M, 2 partes) | [CONFIRMADO] `docker-compose.yml:43-58` |
| Proxy | nginx 1.29.5 con TLS (certs locales) | [CONFIRMADO] `docker-compose.yml:85-99` |
| BD | Bind mount local `./database/postgres:/var/lib/postgresql` | [CONFIRMADO] `docker-compose.yml:74` |

- Frontend llama al backend vía `/api` (proxy nginx) ([CONFIRMADO] `client/src/environments/environment.ts:11` `apiUrl: "/api"`).
- Backend: patrón Router → Service (BaseService) → Repository (BaseRepository) → DB, con `Response.ok_data/error` como sobre común. [CONFIRMADO] `api/services/core/base_service.py:36-69`, `api/repositories/core/base_repository.py:20-132`, `api/services/core/response_service.py` (símbolos `Response.error`/`Response.ok_data` con 108/100 usos según grafo de código; fichero no abierto — ver Limitaciones).

### 2.2 Arranque y estado (importante para operación)

- `app.py` define lifespan que ejecuta `init_db()` **solo si** `INIT_DB_ON_STARTUP` ([CONFIRMADO] `api/app.py:27-31`). Pero `DevelopmentConfig` — **la config por defecto** (`api/config.py:86-88`, `APP_ENV` default "development") — tiene `INIT_DB_ON_STARTUP = True` y `SEED_DB_ON_STARTUP = True` ([CONFIRMADO] `api/config.py:52-53`).
- `init_db()` con la estrategia por defecto `create_all` ejecuta `Base.metadata.create_all(engine)` **sin condición** fuera de SQLite (con un warning en el log) ([CONFIRMADO] `api/db/database.py:89-105`, línea 100), y luego siembra admin si no existe ninguno ([CONFIRMADO] `api/db/database.py:107-109`; `seed_admin` solo crea si no hay ADMIN previo, `api/db/users_seed.py:11-18`).
- Por eso **no se arrancaron contenedores en esta auditoría** (además, Docker quedó bloqueado por permisos de la sesión; ver Limitaciones): el arranque en dev escribe en la BD real (create_all + seed). `create_all` es aditivo (no altera tablas existentes), pero es escritura sobre la BD de producción personal. [CONFIRMADO]
- Alembic está presente y en uso (tabla `alembic_version`, er.sql:38-42), y `ProductionConfig` fuerza `SCHEMA_INIT_STRATEGY="migrations"` ([CONFIRMADO] `api/config.py:62`). El dev usa `create_all` por defecto (`api/config.py:37`) → riesgo de drift esquema-código en dev. [CONFIRMADO]

### 2.3 Autenticación y seguridad actual

- Todos los routers de negocio van protegidos con `Depends(require_access_token)` a nivel de registro ([CONFIRMADO] `api/routers/__init__.py:60-66`, tupla `_protected_routers` incluye `import_router` en línea 50). Solo `auth_router` queda público (línea 67).
- JWT con access+refresh, bcrypt rounds=12, dummy-hash contra timing attacks en login, rate limiting **solo en login** (5 fallos / 5 min, en memoria) ([CONFIRMADO] `api/services/auth/auth_service.py:49-79` (`login`), `api/services/core/security_service.py:5-17` (grep bcrypt), `api/services/auth/rate_limiter.py:44-45`).
- **No hay aislamiento por usuario en resúmenes ni en `GET /expenses`** (sin filtro `user_id`): [CONFIRMADO] `api/repositories/summaries/summary_repository.py` (ninguna query filtra user), `api/routers/expenses/expense_router.py:66-77`. Existe endpoint protegido por identidad `GET /expenses/user/{id}` (expense_router.py:107-128) que verifica identidad, pero el listado general no filtra.
- Privacidad: `database.py:37` registra la `DATABASE_URL` completa —incluye contraseña de la BD— en el log de arranque ([CONFIRMADO] `api/db/database.py:37`, `logger.info(f"Database URL: {DATABASE_URL}")`; logs rotativos en `logs/app.log`, `api/services/logs/logger_service.py:35-40`). Y el frontend vuelca payloads completos de movimientos a la consola del navegador ([CONFIRMADO] `excel-import.component.ts:317, 331, 336, 396, 545-546`, `console.log` de transacciones y payload bulk).

### 2.4 Patrón de sesión/transacciones

- Sesión por request con rollback on exception (`get_db`, [CONFIRMADO] `api/db/database.py:62-71`), helper `atomic()` que compromete o revierte ([CONFIRMADO] `api/db/database.py:9-26`), y savepoints por fila (`begin_nested`) durante la importación ([CONFIRMADO] `api/services/imports/import_service.py:139-144, 181-186`).
- BaseRepository escribe con `flush()` y delega el commit al servicio ([CONFIRMADO] `api/repositories/core/base_repository.py:44-46`, comentario en el código + métodos create/update/delete con flush). Soft-delete por `deleted_at` por defecto ([CONFIRMADO] `base_repository.py:67-78`, `delete`).

---

## 3. Inventario de funcionalidades de importación existentes

**Lo que YA existe (no duplicar, extender):**

| Capacidad | Estado | Evidencia |
|---|---|---|
| Carga de fichero XLS/XLSX y parseo en navegador | ✅ | [CONFIRMADO] `excel-import.component.ts:83` (input `accept=".xls,.xlsx"`), `excel-import.component.ts:289-300` (`XLSX.read` + `sheet_to_json(header:1, raw:false)`) |
| Perfiles de importación por entidad (columnas jsonb con alias por campo: date/description/amount/balance, fila de cabecera configurable) | ✅ | [CONFIRMADO] `er.sql:163-178` (`import_profiles.columns jsonb`), `excel-parser.service.ts:82-85` (keyword match por perfil; los perfiles se consumen en el frontend, no en el backend) |
| Orígenes de importación (entidades) con CRUD | ✅ | [CONFIRMADO] `er.sql:151-161` (`import_origins`), rutas `import_origins`/`import_profiles` en `app.routes.ts:35-36` |
| Detección de columnas por alias de perfil (keyword match normalizado) | ✅ | [CONFIRMADO] `excel-parser.service.ts:57-63` (`findColumnIndex`), `utils.service.ts:80-87` (`normalize`: minúsculas, sin acentos ni símbolos) |
| Normalización de importes (formato europeo 1.501,70 y anglosajón 1,501.70, símbolo €, signo unicode −) | ✅ | [CONFIRMADO] `utils.service.ts:88-108` (`parseAmount`) |
| Normalización de descripciones y fechas para dedup | ✅ | [CONFIRMADO] `dedup_service.py:6-21` (`_normalize_description`, `_normalize_date`) |
| Deduplicación determinista (cuenta+fecha+importe 2 decimales+descripción, sha256) con constraint UNIQUE en BD | ✅ | [CONFIRMADO] `dedup_service.py:29-46`, `expense_model.py:21` (`uq_expenses_account_dedup_hash`), `er.sql:109` |
| Importación atómica gastos+ingresos (all-or-nothing) con savepoints por fila | ✅ | [CONFIRMADO] `import_service.py:54` (`atomic(self.db)`), `import_service.py:139-144` |
| Categorización automática por reglas regex priorizadas (backend y frontend aplican las mismas reglas de BD) | ✅ | [CONFIRMADO] `categorization_service.py:139-158`, `rule-categorizer.service.ts:129-156` (`suggestCategoryAndIgnoreFlag`), reglas CRUD en `client/src/app/services/rules/category-rule.service.ts:39-124` |
| Flag `ignore_in_analysis` ("descartable") en import y reglas | ✅ (a medias) | [CONFIRMADO] `import_schema.py:19`, `category_rule_model.py:41`; **no aplicado en resúmenes** (ver P0-3) |
| Sugerencia de source por descripción (local + endpoint `/sources/suggest`) | ✅ | [CONFIRMADO] `excel-import.component.ts:400-450` (`suggestSourceForTransaction`, `findSourceByDescription`), `api/routers/finance/source_router.py:59-70` |
| Preview editable fila a fila (categoría/source/usuario/descartable/select) antes de guardar | ✅ | [CONFIRMADO] `excel-import.component.html:102-252` (mat-table inline), `excel-import.component.ts:78-89` (`displayedColumns`) |
| Reglas de source independientes en BD (regex, prioridad) | ✅ (esquema) | [CONFIRMADO] `source_rule_model.py:18-51`, migración `source_rules_independent_matching.py:1-8`; **pero ver P2-2** |
| Clasificación IA local (llama.cpp) con reglas keyword de frontend y sugerencia de categorías nuevas | ⚠️ existe, desconectada | [CONFIRMADO] `api/services/ai/transaction_ai_service.py:23-81` (`classify`), endpoint en `api/routers/ai/transactions_ai_router.py` (registrado en `api/routers/__init__.py:48`); llamada frontend **comentada** (`excel-import.component.ts:342-373`) y backend import sin `ai_service` (`import_service.py:33`) |
| Endpoint bulk alternativo `/expenses/bulk` (duplica lógica dedup sin categorización) | ⚠️ | [CONFIRMADO] `api/routers/expenses/expense_router.py:38-51`, `api/services/expenses/expense_service.py:61-110` (`create_batch_atomic`) |
| **Vista previa con informe de filas descartadas/inválidas** | ❌ | El parser descarta filas sin importe **sin informar** ([CONFIRMADO] `excel-parser.service.ts:91-98`: filtro silencioso; solo hay error si falla la detección de columnas, línea 87-89) |
| **Marcado previo de duplicados en la preview** | ❌ | El dedup solo actúa al insertar; la preview no consulta BD ([CONFIRMADO] ausencia en `excel-import.component.ts` completo) |
| **Lotes de importación (batch) y reversión** | ❌ | NO ENCONTRADO (er.sql completo, grep api) |
| **Conciliación de saldos del extracto** | ❌ | NO ENCONTRADO (grep); balance capturado y descartado |
| **Transferencias entre cuentas propias** | ❌ | NO ENCONTRADO |
| **Adaptadores por entidad (ING/TR específicos)** | ⚠️ parcial | Mecanismo genérico por perfil; NO ENCONTRADO código específico ING/TR (grep "ing", "trade", "republic" en api → solo falsos positivos genéricos; busqué también en services/imports: solo `import_service.py`, `import_origin_service.py`, `import_profile_service.py`) |
| **Multi-divisa en importación** | ❌ | EUR hardcodeado ([CONFIRMADO] `excel-import.component.ts:528,541`; `excel-parser.service.ts:115`) |

---

## 4. Mapa del flujo actual: del fichero a la consulta

**Lado frontend (lo que vive el usuario):** [CONFIRMADO]

1. Menú → ruta `excel_import` ([CONFIRMADO] `app.routes.ts:34`).
2. La página dispara **8 llamadas HTTP de catálogos** en `ngOnInit`: bancos, cuentas, sources, categorías de ingreso, de gasto, tarjetas, orígenes, perfiles ([CONFIRMADO] `excel-import.component.ts:110-190`, `ngOnInit`).
3. El usuario selecciona: banco → origen → perfil (requerido para habilitar el botón de fichero, `excel-import.component.ts:270-279`) → cuenta (filtra por banco, líneas 196-210, 462-464) → usuario (auto-default al usuario actual, líneas 245-248) → tarjeta opcional (html:56-72).
4. Botón "Seleccionar Excel" → fichero → parseo en navegador con el perfil (`excel-import.component.ts:269-339`, `onFileChange`).
5. Filas sin importe: descartadas en silencio (`excel-parser.service.ts:91-98`).
6. Categorización local con reglas de BD (`rule-categorizer.service.ts:62-93`, tras `refreshRules` en `excel-import.component.ts:320`); sugerencia de source local por descripción (líneas 400-450) y, si falla, HTTP por fila a `/sources/suggest` (líneas 414-430).
7. Preview: tabla con orden (matSort), **sin paginación, sin filtro de texto, sin búsqueda** ([CONFIRMADO] `excel-import.component.html:102-252`; no hay `mat-paginator` ni filtro en el HTML ni en el componente), con edición inline de categoría/source/usuario/descartable y checkbox por fila + marcar-todo.
8. `confirmImport()`: filtra `selected`, **excluye silenciosamente las filas sin categoría** (líneas 508-513), separa por signo (gasto/ingreso, líneas 515-516), envía importes en absoluto para gastos (línea 521) y `auto_categorize` no se envía (backend default `true`, `import_schema.py:40`).
9. POST `/imports/transactions/bulk` → backend atómico → toast "¡Éxito! N transacciones importadas. M duplicados ignorados." y se limpia la tabla (líneas 553-562). **No hay redirección ni enlace a los movimientos importados.**
10. Para consultar los movimientos: rutas `expenses` / `incomes` ([CONFIRMADO] `app.routes.ts:26-28`) con listas truncadas a 50 sin orden (ver P0-2) y gráficos en `charts` que agregan vía `/summaries` ([CONFIRMADO] `charts-container.component.ts:111,128,145,162,179`).

**Lado backend (por llamada):** [CONFIRMADO]

- `POST /imports/transactions/bulk` (`import_router.py:17-42`): valida pydantic → `ImportService.import_transactions_atomic` ([CONFIRMADO] `import_service.py:35-195`): (1) categoriza los null con reglas regex priorizadas (líneas 56-69); (2) valida FKs por fila (3 SELECTs por fila, `expense_repository.py:67-84`); (3) por fila: hash dedup → salto si ya está en el lote → `exists_by_dedup` (1 SELECT) → INSERT con savepoint; IntegrityError → cuenta "duplicado" (líneas 101-186); (4) devuelve `{inserted, duplicates, total}`.
- Ítems que el backend clasifica (null): solo reglas — la IA no está cableada ([CONFIRMADO] `import_service.py:33`).
- Errores: cualquier `ValueError` (incluida fecha no-ISO) responde como "FK_ERROR" 400 ([CONFIRMADO] `import_router.py:38-39`).

## 5. Medición de los escenarios A–H

Metodología: recuento estático sobre código (componentes, botones, diálogos, llamadas HTTP). Los pasos y clics se derivan de la estructura del código; el tiempo real de cada clic es [NO VERIFICABLE] sin la app arrancada. Donde el recuento depende de datos reales (p. ej. cuántas de 200 filas quedan sin regla), se marca [HIPÓTESIS].

### A. Importar extracto ING nuevo de ~200 filas

| Métrica | Valor | Confianza |
|---|---|---|
| Pasos principales | 4: (1) configurar contexto, (2) elegir fichero, (3) revisar/confirmar, (4) navegar a consultar | [CONFIRMADO] estructura `excel-import.component.ts/html` |
| Interacciones previas al fichero | 4-6: banco + origen + perfil + cuenta (+usuario auto, +tarjeta opcional) | [CONFIRMADO] `excel-import.component.html:1-83` |
| Clics totales mínimos | ~7-9 | [HIPÓTESIS] (recuento de controles activos) |
| Llamadas HTTP de catálogos al abrir la página | 8 | [CONFIRMADO] `excel-import.component.ts:110-190` |
| Correcciones manuales previsibles | Depende del catálogo de reglas: cada descripción sin regla (o sin source) requiere edición inline; ~200 selects si el catálogo es joven | [HIPÓTESIS] (depende del número de reglas activas en la BD real) |
| ¿Duplicados visibles antes de confirmar? | No (el dedup solo actúa al insertar) | [CONFIRMADO] |
| ¿Resultado visible al terminar? | Toast con contadores; **no** hay enlace a lo importado; y en las listas solo se ven 50 filas sin orden | [CONFIRMADO] `excel-import.component.ts:553-562`, P0-2 |

**Veredicto:** funcional pero con alta fricción de contexto (selectores) y sin bucle de retorno ("¿qué se importó de verdad?"). [CONFIRMADO]

### B. Reimportar el mismo fichero (idempotencia)

- El backend detecta duplicados por hash y devuelve `inserted=0, duplicates=N`; test dedicado lo cubre ([CONFIRMADO] `api/tests/test_import_service.py:174-208`, `test_import_transactions_atomic_duplicate_handling`).
- El toast muestra "0 importadas, N duplicados ignorados" ([CONFIRMADO] `excel-import.component.ts:555-560`).
- **Pero:** (1) no distingue "fichero ya importado" de "duplicados parciales"; (2) las filas sin categoría se habrán excluido antes en el cliente (P0-1), así que "duplicados" mezcla conceptos; (3) si el usuario borró un movimiento (soft-delete) y reimporta, esa fila **no** vuelve: choca con la UNIQUE y se cuenta como duplicado (ver P1-4). [CONFIRMADO]

**Veredicto:** idempotencia del núcleo ✅; mensaje mejorable. Nota: **no hay test** de "fichero completo ya importado" a nivel de servicio con 200 filas ni de colisión con filas soft-borradas. [CONFIRMADO]

### C. Importar extracto con periodo solapado

- El dedup es fila a fila por hash (cuenta+fecha+importe+descripción): las filas ya importadas se saltan y las nuevas se insertan ([CONFIRMADO] `import_service.py:101-144`; el filtro por rango de fechas **no existe**, y eso aquí juega a favor). [CONFIRMADO]
- Riesgo confirmado: filas **legítimas** idénticas (misma cuenta+fecha+importe+descripción normalizada) dentro del solape se descartan para siempre (P1-3).
- No hay informe "X nuevas, Y omitidas por duplicado, Z revisadas" más allá del toast. [CONFIRMADO]

### D. Importar extracto de Trade Republic (inversión, dividendos, comisiones)

- No hay adaptador específico TR: el mismo pipeline genérico por perfil (NO ENCONTRADO: grep "trade|republic" en `api/` y `client/src/` → solo falsos positivos). [CONFIRMADO]
- El tipo (gasto/ingreso) se decide **solo por el signo** ([CONFIRMADO] `excel-parser.service.ts:52-54`, `inferTransactionType`; `excel-import.component.ts:515-516`).
- Consecuencias para un extracto TR típico: compra de activo → **gasto**; venta → **ingreso**; dividendo → ingreso; comisión → gasto; aportación de efectivo → ingreso en la cuenta de inversión. Todo entra como `expenses`/`incomes` ordinarios: el modelo `investments`/`investments_logs` **no se alimenta desde la importación** (NO ENCONTRADO: el único endpoint de creación de movimientos de inversión es CRUD manual; el import solo crea Expense/Income, [CONFIRMADO] `import_service.py:123-186`). [CONFIRMADO]
- `investments_logs` sí puede representar buy/sell/deposit/withdraw con cantidad y precio (`ActionEnum`, `enums.py:37-44`; `investment_log_model.py:8-22`) pero es **entrada manual**. Sin ISIN/ticker/activo, sin cost basis, sin valoración: posiciones y rentabilidad no son calculables desde extractos (los extractos TR dan operaciones y dividendos, no valoración diaria). [CONFIRMADO en cuanto al modelo; la cobertura de los extractos reales es [NO VERIFICABLE]]
- Mitigación parcial hoy: marcar `ignore_in_analysis` — pero los resúmenes no lo respetan (P0-3), así que ni con la marca se evita la distorsión en gráficos.

### E. Clasificar 30 movimientos desconocidos y que la clasificación se aplique sola la próxima vez

- **En la preview:** edición inline ~3-4 clics por fila (abrir mat-select, buscar categoría en lista sin buscador, elegir) ≈ **90-120 clics** para 30 filas. No existe "aplicar categoría a la selección" ([CONFIRMADO] `excel-import.component.html:208-241`: solo select por fila). [CONFIRMADO estructura; clics HIPÓTESIS]
- **Tras importar:** modal genérico por movimiento que **refetcha 5 catálogos en cada apertura** ([CONFIRMADO] `expenses.component.ts:141-147`, `openDialog`) ≈ 5-7 clics + espera × 30.
- **Aprendizaje: NO EXISTE.** Guardar la corrección llama a `ExpenseService.update` → `BaseService.update` ([CONFIRMADO] `expenses.component.ts:241-265`; `base_service.py:50-56`) que **no crea ni actualiza ninguna `CategoryRule`**. Para que la próxima importación clasifique sola, el usuario debe ir a `category_rules` y crear una regla regex **a mano** (formulario genérico con campo `pattern` regex libre; [CONFIRMADO] ruta `app.routes.ts:38`, CRUD en `category-rule.service.ts:68-113`). [CONFIRMADO]
- La IA que podría cerrar el hueco está desconectada (P1-5).

### F. Registrar y emparejar una transferencia entre dos cuentas propias

- Registrar "a mano": crear un gasto y un ingreso (2 formularios genéricos, ~12-16 clics) y marcar ambos como descartables para que no distorsionen... y aun así los resúmenes los contarán (P0-3). [CONFIRMADO]
- Emparejamiento automático: **0%** — no existe emparejamiento (NO ENCONTRADO: grep "transfer|pair|match" en api/ y client/; no hay nada a nivel de movimiento). [CONFIRMADO]
- Cuando ambas mitades llegan por importaciones separadas (cuenta A y cuenta B): se importan como gasto y como ingreso independientes, contando doble en las estadísticas de gasto/ingreso totales (el "neto" por casualidad se compensa si ambas mitades entran: `get_income_vs_expense`, `summary_repository.py:186-205`). [CONFIRMADO]

### G. Corregir una importación errónea y revertir un lote completo

- No hay lotes ni historia de importaciones: revertir "un lote" **no es posible como unidad** (NO ENCONTRADO, ver sección 3). [CONFIRMADO]
- Corrección fila a fila: modal genérico (E) o DELETE individual (`expense_router.py:95-104` → soft-delete en `base_repository.py:67-78`).
- Efecto perverso confirmado: tras el soft-delete, la UNIQUE `(account_id, dedup_hash)` sigue ocupada por la fila borrada, así que esa transacción **ya no puede reimportarse jamás** (P1-4). Para "revertir y reimportar corregido" hay que hard-deletear o editar a mano. [CONFIRMADO]
- La edición masiva no existe; con más de 50 filas afectadas, ni siquiera se ven todas (P0-2). [CONFIRMADO]

### H. Comparativa con Excel

Dónde gana Excel hoy (todas [CONFIRMADO] por estructura, salvo tiempos [HIPÓTESIS]):

1. **Sin selectores de contexto**: abrir la hoja exportada y trabajar; Economy exige 4-6 selects de catálogo + 8 peticiones HTTP antes del fichero.
2. **Edición directa y en bloque**: filtro + relleno hacia abajo + find&replace; Economy: un select por fila, sin acciones en bloque.
3. **Verlo todo, siempre**: una hoja muestra las 200 filas ordenadas; Economy muestra 50 arbitrarias sin orden (P0-2).
4. **Borrado/deshacer trivial**: borrar filas de un error de importación = borrar filas; Economy: sin lotes, soft-delete que además bloquea la reimportación (P1-4).
5. **El "aprendizaje" ya está hecho**: la tabla de mapeo concepto→categoría del usuario vive en su hoja y la reutiliza; en Economy hay que crear regex manualmente y no hay aprendizaje de correcciones (E).
6. **Fórmulas de control**: SUMIFS contra el saldo final del extracto; Economy descarta el balance (P1-2).
7. **Multi-entidad en una vista**: hojas por banco + hoja consolidada; Economy no consolida cuentas en una revisión única.

Dónde gana Economy (para no sobre-corregir): deduplicación automática, reglas priorizadas compartidas frontend/backend, atomoicidad, multi-usuario/households, gráficos agregados, y si se cablea, la IA local. El objetivo no es imitar Excel sino que el 95% del trabajo sea automático y las excepciones se revisen en un solo sitio.

## 6. Problemas confirmados

Formato: prioridad · evidencia · impacto · causa · propuesta · complejidad · dependencias/riesgos. Los P2/P3 van en formato tabla compacta al final de la sección.

### P0-1 — Filas sin categoría se descartan en silencio al importar

- **Evidencia:** [CONFIRMADO] `client/src/app/features/import/excel/excel-import.component.ts:502-513` en `confirmImport()`: `validTransactions = importable.filter(t => t.suggestedCategoryId)`; solo se avisa si **todas** carecen de categoría (líneas 510-513); el toast de éxito solo muestra `inserted`/`duplicates` (líneas 553-560). Backend: el esquema permite `category_id null` ([CONFIRMADO] `api/schemas/imports/import_schema.py:16,30`) y el servicio intenta auto-categorizar los null (import_service.py:56-69), pero el cliente ya los filtró.
- **Impacto:** el usuario confirma "importar 200" y se importan menos, sin constancia; cree que la app se los comió o que el banco los cambió. Pérdida silenciosa de datos desde el punto de vista del usuario. Es la causa nº1 del "no me fío de la importación".
- **Causa técnica:** el flujo fue diseñado para "no enviar nada sin categoría" y se quedó sin el informe de excepciones.
- **Propuesta:** incluir **todas** las filas seleccionadas en el payload y: (a) mostrar en la preview un filtro/badge "sin categoría (N)" y bloquear la confirmación solo con confirmación explícita; (b) que el backend devuelva también `uncategorized` y `skipped_by_category`; (c) toast final: "importadas X, duplicadas Y, sin categoría Z (verlas)". Alternativa mínima sin tocar backend: contador de excluidas en el cliente antes del POST.
- **Complejidad:** baja.
- **Dependencias/riesgos:** si se envían filas sin categoría al backend con `auto_categorize=true`, chocarán con `expenses.category_id NOT NULL` (er.sql:100) y el IntegrityError se contará como "duplicado" (import_service.py:143-144) — ver P2-6b. Hay que corregir ambos o solo (a)/(c).

### P0-2 — Listados de movimientos truncados a 50 filas, sin orden estable

- **Evidencia:** [CONFIRMADO] `api/services/core/base_service.py:46` (`get_all(page=1, per_page=50)`), `api/routers/expenses/expense_router.py:66-77` (`list_expenses` sin parámetros), `api/repositories/core/base_repository.py:34-36` (`get_all` sin `ORDER BY`), frontend sin paginación ([CONFIRMADO] `client/src/app/services/core/base-crud.service.ts:41`, `getAll` sin params; mismo patrón verificado por grep en `api/routers/incomes/income_router.py` — grep `per_page|page` → 0 resultados). Paginación client-side del generic-table sobre esos 50 ([CONFIRMADO] `generic-table.component.ts:73-77`).
- **Impacto:** tras unas semanas importando, los movimientos nuevos **no aparecen** en `expenses`/`incomes` (orden arbitrario de Postgres sin ORDER BY): el usuario no puede revisar lo que acaba de importar. Destruye la confianza en la app justo después de importar.
- **Causa técnica:** default de conveniencia heredado de BaseService nunca sobrescrito ni expuesto al router/frontend.
- **Propuesta:** (1) añadir `ORDER BY date DESC, id DESC` en `BaseRepository.get_all`; (2) exponer `page/per_page` (+filtros `date_from/date_to`, `account_id`, `q`) en los routers de expenses/incomes; (3) paginación server-side en generic-table o en las pantallas de movimientos. Compatible con la arquitectura actual (el repositorio ya firma paginación).
- **Complejidad:** baja-media (backend baja; frontend media por tocar varias pantallas).
- **Dependencias/riesgos:** respetar soft-delete en el conteo; no romper el contrato de respuesta (añadir campos opcionales, no cambiar existentes — regla API contract de CLAUDE.md).

### P0-3 — Transferencias propias: no existen y además distorsionan todos los totales

- **Evidencia:** [CONFIRMADO] sin modelo de transferencia (er.sql completo, 22 tablas revisadas; grep "transfer" en `api/**.py` → solo `ActionEnum.TRANSFER` en `api/models/core/enums.py:40` para `investments_logs`). El flag `ignore_in_analysis` existe en `expenses`/`incomes` (er.sql:106, `income_model.py:19`) pero **ninguna** consulta de `summary_repository.py` lo filtra ([CONFIRMADO] `get_totals_by_category` 35-47, `get_totals_over_time` 117-145, `get_income_vs_expense` 186-205, `get_totals_by_source` 254-265, `get_totals_by_user` 304-317 — ninguna tiene la condición). Tampoco el import backend lo asigna desde reglas de source (solo la regla de categoría lo hace, `categorization_service.py:202-206`, y solo por `categorize_transaction_with_flags`, que el import **no usa** — usa `categorize_transaction`, import_service.py:59-69).
- **Impacto:** cada transferencia entre cuentas propias suma gasto en el dashboard de gastos y ingreso en el de ingresos; el objetivo "que las transferencias no cuenten como gasto/ingreso" está hoy a **0%**. Con el flujo real del usuario (varias cuentas propias + tarjetas), los totales de gasto/ingreso/ahorro de los gráficos están sobredimensionados de forma sistemática.
- **Causa técnica:** el concepto "movimiento no analizable" llegó a la capa de datos y de import, pero no a la de análisis; y la de análisis nunca tuvo concepto de transferencia.
- **Propuesta (sin tocar esquema, 2 pasos):**
  1. Añadir `Expense.ignore_in_analysis == False` / `Income.ignore_in_analysis == False` a todas las consultas de `SummaryRepository` (y a las métricas de frontend si calcula algo en cliente).
  2. En el import, usar `categorize_transaction_with_flags` en lugar de `categorize_transaction` para que las reglas asignen `ignore_in_analysis` y source automáticamente.
  3. (Con esquema, después) Modelo de transferencias: par emparejado con ventana de fechas ±3 días e importe igual — ver sección 11.
- **Complejidad:** paso 1-2 baja; paso 3 media-alta.
- **Dependencias/riesgos:** el paso 1 cambia cifras históricas mostradas (esperado y deseable, pero comunicarlo); revisar también si los charts de frontend filtran algo por su cuenta (charts-container no filtra ignore_in_analysis [CONFIRMADO] en las llamadas revisadas: pasa fechas solamente).

### P1-1 — Sin lotes de importación: ni auditoría ni reversión controlada

- **Evidencia:** [CONFIRMADO] NO ENCONTRADO: grep `import_batch|batch_id|ImportBatch` en `api/**.py` → 0; er.sql completo sin tabla de lotes; `api/routers/imports/` solo contiene `import_router`, `import_origin_router`, `import_profile_router` (listado de directorio). `dedup_hash` es el único vestigio del origen.
- **Impacto:** "¿qué importé ayer?" y "revierte esa importación" son imposibles como unidad; la corrección de errores va fila a fila en listas truncadas (P0-2) y con el riesgo P1-4.
- **Causa técnica:** el pipeline se diseñó fila-céntrico (hash) sin entidad de sesión de importación.
- **Propuesta:** tabla `import_batches` (id, user_id, account_id, origin_id, profile_id, file_name, file_hash, imported_at, inserted/duplicates/total, saldo inicial/final declarado) + FK nullable `batch_id` en `expenses`/`incomes`/`investments` + endpoint `DELETE /imports/batches/{id}` que haga **soft-delete de los movimientos del lote** que sigan sin alteraciones posteriores (guardar en el lote si sus filas fueron tocadas). Con `file_hash` del fichero completo se habilita además el mensaje exacto "este fichero ya se importó el X".
- **Complejidad:** media.
- **Dependencias/riesgos:** requiere migración (la única pieza P0/P1 que la necesita junto a transferencias); respetar regla Alembic (nueva migración, nunca modificar las viejas).

### P1-2 — Sin conciliación: el saldo del extracto se captura y se tira

- **Evidencia:** [CONFIRMADO] `excel-parser.service.ts:107` mapea la columna `balance` al modelo `ImportTransaction.balance` (`import-transaction.model.ts:5`), la preview la muestra (`excel-import.component.html:164-169`) y el payload no la incluye (no hay campo en `import_schema.py:7-41`; `excel-import.component.ts:518-543` no la envía). Sin concepto de saldo inicial/final en BD ni en UI (NO ENCONTRADO: grep `reconcil|opening_balance|closing_balance` → 0).
- **Impacto:** errores de signo, fechas desplazadas, filas ausentes o duplicadas legítimas (P1-3) pasan inadvertidos: nada dice "el saldo calculado no cuadra con el extracto". Es el control de calidad que Excel sí ofrece visualmente.
- **Causa técnica:** el campo se usó para el negativo-de-tarjeta (líneas 100-102: negativo+tarjeta → `ignore_in_analysis=true`) y para mostrarlo, pero no se modeló.
- **Propuesta:** en la **preview** (sin backend): validar la cadena de saldos: `balance[i] - balance[i-1] == amount[i]` fila a fila y marcar las inconsistencias; mostrar "saldo inicial" y "saldo final" calculados y pedirlós al usuario si el extracto no los trae (dos inputs opcionales). Con P1-1: persistir saldos declarados en el lote y calcular diferencia al terminar → criterio de aceptación de conciliación.
- **Complejidad:** baja (validación en preview), media (persistida en lotes).
- **Dependencias/riesgos:** extractos donde el balance no es saldo acumulado (algunos TR) — la validación debe ser informativa ("no puedo conciliar: la columna no es acumulada"), no bloqueante.

### P1-3 — La deduplicación descarta compras legítimas idénticas

- **Evidencia:** [CONFIRMADO] `api/services/core/dedup_service.py:29-46`: hash de `account|fecha|importe(2dec)|descripción normalizada`; `import_service.py:113-121`: si la clave `(account_id, hash)` ya existe en BD o en el lote → `duplicates += 1` y no se inserta. Sin contador de ocurrencias (grep `occurrence|contador` → no hay).
- **Impacto:** dos cafés del mismo importe el mismo día, dos suscripciones idénticas, o el solape C: la segunda ocurrencia **se pierde para siempre** y además suma en "duplicados" del toast, degradando la fiabilidad percibida.
- **Causa técnica:** la huella no incluye ordinal de ocurrencia.
- **Propuesta (sin esquema):** en `import_transactions_atomic`, para cada fila contar cuántas filas ya existen en BD con ese mismo hash base y añadir la posición de ocurrencia al payload del hash (`hash = sha256(base + "|" + n)`), empezando en `n = existentes + 1`. Requiere una query de conteo por hash distinto (agrupada, no N+1: `SELECT dedup_hash, count(*) ... GROUP BY`). Alternativa con esquema: quitar la UNIQUE y gestionar dedup solo en servicio con `occurrence` numérica; menos recomendable (pierde el candado de BD).
- **Complejidad:** media.
- **Dependencias/riesgos:** migración de datos: los hashes existentes en BD no llevan ordinal → mantener el hash base para n=1 (compatibilidad con filas ya importadas) y solo ordinal ≥2 para las nuevas. Test específico: dos compras idénticas mismo día → se insertan 2.

### P1-4 — Soft-delete + UNIQUE bloquean la reimportación para siempre

- **Evidencia:** [CONFIRMADO] `BaseRepository.delete` hace soft-delete (`base_repository.py:67-78`); `exists_by_dedup` consulta vía `_base_query()` que filtra `deleted_at IS NULL` (`expense_repository.py:59-65` + `base_repository.py:20-24`); la constraint es `uq_expenses_account_dedup_hash` sobre `(account_id, dedup_hash)` **sin** `deleted_at` (`expense_model.py:20-22`, `er.sql:109`). En `import_service.py:138-144`, el IntegrityError resultante se cuenta como "duplicado".
- **Impacto:** si el usuario borra un movimiento (error) y reimporta el extracto para traerlo corregido, la fila nunca vuelve: "duplicado" fantasma. Escenario G roto también por aquí.
- **Causa técnica:** dos mecanismos (soft-delete y unique) pensados por separado.
- **Propuesta (sin esquema):** que `exists_by_dedup` incluya las filas borradas y, si el match es con una borrada, **revivirla** (limpiar `deleted_at` + actualizar campos) en vez de insertar. Alternativa con esquema: partial unique index `WHERE deleted_at IS NULL` (Postgres) o quitar la UNIQUE confando en el candado de servicio.
- **Complejidad:** baja (revivir) / media (índice parcial con migración).
- **Dependencias/riesgos:** revivir debe actualizar amount/date si el usuario editó el borrado antes... decidir política (revivir con datos del fichero es lo esperado).

### P1-5 — La IA local está desconectada del flujo de importación

- **Evidencia:** [CONFIRMADO] (1) backend: `import_service.py:33` construye `CategorizationService(db)` sin `ai_service`, y `categorize_transaction` solo lo usa si está presente (categorization_service.py:148-155); (2) frontend: el bloque que llamaba al clasificador IA está **comentado** (`excel-import.component.ts:342-373`) y `TransactionAiService` no se usa en ningún otro componente (grep referencias → solo el propio servicio y este componente); (3) el contenedor llama.cpp sigue levantado con 4096 de contexto (docker-compose.yml:43-58).
- **Impacto:** los movimientos sin regla quedan sin categoría (y por P0-1, sin importarse). El 90% de clasificación automática es inalcanzable sin esto o sin aprendizaje (P1-6).
- **Causa técnica:** transición a "reglas backend" dejó la IA a medias (el flujo rules → AI → null de CLAUDE.md §7 está a medias).
- **Propuesta (sin esquema):** inyectar `TransactionAIService(db)` en `ImportService` bajo un flag (`auto_categorize_ai: bool = False` en el request), aplicarlo **solo a los null** tras reglas, con timeout corto y fallback a null (el servicio ya maneja errores: transaction_ai_service.py:191-216). Mantener el flujo de sugerencias del preview para no duplicar; degradar con gracia si el contenedor no está (ya lo hace, `logger.warning`).
- **Complejidad:** baja-media.
- **Dependencias/riesgos:** latencia (45s timeout por lote, transaction_ai_service.py:192); mover el `print()` a logger (P3-2); no enviar datos a servicios externos (el endpoint es local, docker-compose `ai:8180` interno — cumple la política de privacidad).

### P1-6 — Las correcciones del usuario no aprenden (reglas 100% manuales)

- **Evidencia:** [CONFIRMADO] `expenses.component.ts:241-265` (`update` → `expenseService.update`) y `base_service.py:50-56`: la actualización no toca `category_rules`. La creación de reglas es un CRUD manual aparte (ruta `category_rules`, `app.routes.ts:38`; servicio `category-rule.service.ts:68-113`). Grep de llamadas a `createRule` desde flujos de corrección → no hay.
- **Impacto:** el objetivo "90% clasificación automática tras 2 meses de uso" es imposible: cada mes se repite el mismo trabajo manual sobre los mismos conceptos. Este es, junto a P0-1, el mayor coste frente a Excel (donde la tabla de mapeo del usuario vive y se reutiliza).
- **Causa técnica:** nunca se implementó el lazo de aprendizaje.
- **Propuesta (sin esquema):** al actualizar la categoría de un movimiento **sin regla previa que lo cubra**, ofrecer (checkbox "recordar") crear `CategoryRule` con `pattern = re.escape(descripción normalizada)` (o palabra clave más larga de la descripción), `type` según el movimiento, `priority` por debajo de las manuales (p. ej. 10), `is_active=true`. Igual desde la preview de importación ("aplicar a este y a futuros"). Vista de gestión para revisar reglas aprendidas (ya existe la pantalla).
- **Complejidad:** baja-media.
- **Dependencias/riesgos:** reglas globales sin `user_id` (er.sql:75-89) — en un household, aprender de todos afecta a todos (decidir si aceptable); validar regex antes de guardar (la modelo ya tolera regex inválidas con warning, `category_rule_model.py:52-66`).

### P1-7 — Fechas: un solo formato aceptado y errores con mensaje engañoso

- **Evidencia:** [CONFIRMADO] `utils.service.ts:70-73` (`toIsoDate` solo parsea `dd/MM/yyyy`; si no, **devuelve el string sin convertir**); `import_service.py:102-104` (`datetime.fromisoformat` lanza `ValueError`); `import_router.py:38-39`: cualquier `ValueError` del servicio responde `FK_ERROR` 400. Y la importación es all-or-nothing: una fila mal fecha aborta las 200. [CONFIRMADO]
- **Impacto:** extractos con `dd-MM-yyyy`, `yyyy-MM-dd` o celdas fecha real de Excel (según perfil/locale) → importación entera rechazada con un mensaje que además apunta a claves ajenas ("FK_ERROR"). Escenario A falla estrepitosamente según el formato del banco.
- **Causa técnica:** un solo formato hardcoded + catch genérico.
- **Propuesta:** (1) ampliar `toIsoDate` a una lista de formatos (`dd/MM/yyyy`, `dd-MM-yyyy`, `yyyy-MM-dd`, ISO con hora) y, si nada encaja, marcar la fila como inválida **con la fila visible en preview** (no descartarla); (2) mensajes de error diferenciados (`INVALID_DATE`, `INVALID_AMOUNT`, `FK_ERROR`) desde el servicio (excepciones tipadas); (3) validar todas las fechas antes de insertar y devolver el listado de filas inválidas con su número de fila.
- **Complejidad:** baja.
- **Dependencias/riesgos:** fechas reales de los extractos del usuario = [NO VERIFICABLE] sin muestras (pregunta en sección 15).

### P1-8 — Moneda fija EUR y sin validación de coherencia de signos/tipos

- **Evidencia:** [CONFIRMADO] `excel-import.component.ts:528,541` (`currency: CurrencyEnum.EUR` fijo en el payload), `excel-parser.service.ts:115` (idem en la transacción). `import_schema.py:11,26` exige `amount > 0`; el cliente hace `Math.abs` para gastos (línea 521). La `CurrencyEnum` ya tiene USD/JPY/cripto (enums.py:4-19) pero la importación nunca la usa. Cuenta tiene moneda (er.sql:31) que se ignora.
- **Impacto:** extractos en otra divisa (TR con acciones en USD, cuenta en otra moneda) se contabilizan como EUR sin conversión ni aviso; y al forzar positivos, un extracto con columnas separadas cargo/abono o signos invertidos se clasificaría al revés sin control.
- **Causa técnica:** caso de uso único EUR positivo-absoluto consolidado.
- **Propuesta:** (1) moneda por defecto = moneda de la cuenta seleccionada (campo existente `accounts.currency`); (2) permitir override en la pantalla; (3) validación de coherencia: si el perfil define columna "sign" o "cargo/abono", respetarla y verificar contra el tipo inferido; avisar si una fila queda con tipo ambiguo.
- **Complejidad:** baja (1-2), media (3).
- **Dependencias/riesgos:** no hay tabla de tipos de cambio: la multi-divisa real (saldo consolidado multi-divisa) es otro proyecto; este P1 solo evita **etiquetar mal**.

### P1-9 — La preview no permite revisar por excepciones (sin filtro, sin bloque, sin paginación)

- **Evidencia:** [CONFIRMADO] `excel-import.component.html:102-252`: mat-table con `matSort` solamente; sin `mat-paginator`, sin filtro de texto, sin agrupación por estado, sin "asignar categoría a seleccionados" (solo checkbox por fila + `toggleAll` de importar, `excel-import.component.ts:479-490`).
- **Impacto:** revisar 200 filas = scroll infinito + selects fila a fila; el objetivo "solo revisar excepciones" no es operativo. Este es el gap de productividad más directo frente a Excel (filtro + relleno en bloque).
- **Causa técnica:** la tabla preview se hizo mínima.
- **Propuesta:** en la preview: (a) chips/filtros por estado (sin categoría / posible duplicado / descartable / OK); (b) acción "asignar categoría/source a las seleccionadas"; (c) paginador o virtual scroll; (d) buscador de descripción. Después de importar: combo con P0-2 (listar lo recién importado por lote).
- **Complejidad:** media (es el cambio de UX más grande pero localizado en un componente).
- **Dependencias/riesgos:** ninguna de esquema; sinergia fuerte con P1-2 y P1-5 (los estados "posible duplicado" y "sugerencia IA" alimentan los mismos chips).

### P1-10 — Copia de seguridad no operativa (operación, no código)

- **Evidencia:** [CONFIRMADO] `backups/backup_postgres.sh:11-16` (dump vía `docker exec`, retención 7 días por `find -mtime +7 -delete`); único dump presente: `economy_2026-06-04_08-51.dump` (nombre/fecha consultados, contenido no leído). Si la retención fuera real, ese dump no existiría → el script no se ejecuta desde ~junio-2026. El cron documentado en `backups/README.md` no está activo [HIPÓTESIS fuerte: verificar `crontab -l` del host — no pude].
- **Impacto:** cualquier migración/optimización posterior (P1-1, transferencias, índices) sobre una BD sin backup reciente es un riesgo inaceptable.
- **Propuesta:** restaurar el cron (host o contenedor con acceso al socket) + prueba de restauración real (`restore_postgres.sh` contra un volcado de prueba) antes del primer cambio de esquema. [NO VERIFICABLE] desde esta sesión (Docker bloqueado).
- **Complejidad:** baja.

### P2 y P3 (tabla compacta)

| ID | Prioridad | Problema | Evidencia clave | Impacto | Propuesta | Complejidad |
|---|---|---|---|---|---|---|
| P2-1 | P2 | Contraseña de BD en el log de arranque | `api/db/database.py:37` (`logger.info(f"Database URL: {DATABASE_URL}")`) | Credencial en `logs/app.log` (rotativo 7 días, logger_service.py:35-40) | Loguear URL con password enmascarada (o solo engine/host/db) | Baja |
| P2-2 | P2 | Source rules: la migración las declara independientes pero el código no las aplica así | `source_rules_independent_matching.py:1-8` vs `categorization_service.py:193-201` (el matching de source solo corre si hubo match de categoría) y `import_service.py:59-69` (usa `categorize_transaction`, que ignora source rules) | Source mal asignada o fija por fallback (`applySourceFallback`, excel-import.component.ts:452-460) | Usar `categorize_transaction_with_flags` en el import (tapa P0-3.2) y desacoplar el bloque de source del `if matched_rule` | Baja |
| P2-3 | P2 | N+1 en importación y preview | `import_service.py:119,164` (`exists_by_dedup` por fila), `expense_repository.py:67-84` (3 SELECTs FK por fila), `categorization_service.py:140,184` (reglas por fila), `excel-import.component.ts:416` (HTTP `/sources/suggest` por fila) | ~1.000+ queries por import de 200 filas; hasta 200 HTTP en la preview | Cargar reglas/categorías/accounts una vez por lote; `SELECT ... WHERE (account_id, dedup_hash) IN (...)`; sugerencias de source en bloque | Media |
| P2-4 | P2 | Datos financieros en consola del navegador | `excel-import.component.ts:317,331,336,396,545-546` | Exposición local de conceptos/importes en devtools | Eliminar o tras `if (!environment.production)` | Baja |
| P2-5 | P2 | Crear/editar perfil de importación exige JSON manual | `import-profiles.component.ts:70-74` (campo `columns` forzado a texto), `148-153` (`JSON.parse` manual), `275` (toast de error de JSON) | Dar de alta una entidad nueva es tarea de programador; ColumnMapper visual existe pero es código muerto (sin referencias, verificación grep) | Reactivar/terminar `ColumnMapperComponent` o un asistente "elige columna para fecha/desc/importe" desde la preview | Media |
| P2-6 | P2 | er.sql desactualizado frente a modelos/migraciones | er.sql `expenses` sin `user_id` (er.sql:91-110) vs `expense_model.py:33` y migración `add_expense_user_tracking.py`; `accounts.balance numeric(12,2)` (er.sql:24) vs migración `a80dc79a6368_account_balance_numeric_20_10_for_crypto.py` | Fuente de verdad ambigua (CLAUDE.md §1 dice er.sql); riesgo de decisiones sobre esquema erróneo | Regenerar er.sql desde la BD real (pgAdmin export de nuevo) tras aplicar migraciones | Baja |
| P2-6b | P2 | IntegrityError genérico contado como "duplicado" | `import_service.py:138-144,180-186` (`except IntegrityError: duplicates += 1`): un NOT NULL de `category_id` (er.sql:100, `expense_model.py:37`) o cualquier violación cae ahí | Filas perdidas contadas como duplicados; estadística del toast miente | Excepción tipada por tipo de violación; si es NOT NULL/FK → error por fila, no "duplicado" | Baja |
| P2-7 | P2 | Cobertura de tests insuficiente + sin CI + 0 tests frontend | `api/tests/` (6 ficheros); grep `*.spec.ts` en client → 0; `.github/` sin workflows (solo `copilot-instructions.md`) | Zona crítica (import/dedup) sin red para cambios propuestos | Tests: duplicados legítimos, soft-delete+reimport, fechas no-ISO, `ignore_in_analysis` en summaries, lote; CI en GitHub Actions con pytest + build | Media |
| P2-8 | P2 | Dos pipelines bulk paralelos | `import_router.py:17` (`/imports/transactions/bulk`) y `expense_router.py:38` (`/expenses/bulk` con `create_batch_atomic`, expense_service.py:61-110, sin categorización ni informe de duplicados en respuesta) | Lógica dedup duplicada y comportamientos divergentes; el frontend solo usa el primero (grep `expenses/bulk` en client → sin uso) | Deprecar/absorber `/expenses/bulk` hacia ImportService (o documentar su nicho) | Baja |
| P2-9 | P2 | Config dev por defecto escribe en la BD real al arrancar | `config.py:52-53` (`INIT_DB_ON_STARTUP/SEED_DB_ON_STARTUP = True` en DevelopmentConfig, default en config.py:86-88) + `database.py:100` (create_all fuera de SQLite) | create_all aditivo + seed en cada arranque dev sobre la BD personal; drift con Alembic | En dev: `SCHEMA_INIT_STRATEGY=migrations` por defecto o `INIT_DB_ON_STARTUP=False` (usar comando explícito) | Baja |
| P2-10 | P2 | Sin aislamiento por usuario en resúmenes y listado general | `summary_repository.py` (ninguna query filtra user), `expense_router.py:66-77` | En households, todos ven totales globales; `GET /expenses` devuelve de todos | Filtrar por usuario/scope del token (o por household con decisión de producto) | Media |
| P3-1 | P3 | Sin índice en `date` de movimientos | er.sql:91-110, 180-196, 211-226 (sin `ix_*_date`) | Con volúmenes crecientes, los rangos de fechas de summaries hacen seq scan | `CREATE INDEX ix_expenses_date` (etc.) — barato y sin riesgo | Baja |
| P3-2 | P3 | `print()` en lugar de logger en clasificación | `categorization_service.py:155,216` | Errores IA sin traza en logs | Sustituir por `logger.warning` | Baja |
| P3-3 | P3 | Esquema de import exige `name` en incomes que el modelo no tiene | `import_schema.py:24` vs `income_model.py:8-31` (sin columna `name`); `import_service.py:168-178` lo descarta | Dato requerido innecesario en el API | Quitar `name` de `IncomeImportCreate` (o hacerlo opcional) | Baja |
| P3-4 | P3 | Código muerto en import | Sin referencias (grep): `import-preview/import-preview.component.ts`, `column/column-mapper/column-mapper.component.ts`, `services/import/bank-format.service.ts`, `services/import/import-transform.service.ts` | Ruido y confusión sobre el flujo real | Eliminar o documentar como experimental | Baja |

## 7. Hipótesis que requieren validación (separadas de los problemas confirmados)

1. **[HIPÓTESIS]** El catálogo real de reglas activas en la BD es pequeño/joven y por eso gran parte de cada extracto queda sin categoría → la fricción real de la revisión sería mayor que la estimada. *Validar:* `SELECT count(*), type, is_active FROM category_rules GROUP BY ...` en sesión de solo lectura; y medir en una importación real cuántas filas quedan sin categoría.
2. **[HIPÓTESIS]** Los extractos ING del usuario usan fechas `dd/MM/yyyy` con importe formato español (por eso el pipeline actual "funciona" a veces); los de Trade Republic usan otro formato (posiblemente `dd/MM/yyyy` con cabeceras distintas o celdas fecha nativas). *Validar:* 2 extractos anonimizados (estructura y cabeceras, sin datos).
3. **[HIPÓTESIS]** En la práctica el usuario importa cada extracto de cuenta una sola vez por mes y usa `ignore_in_analysis` manual para transferencias/tarjetas, lo que explica que la distorsión P0-3 no se haya notado aún como bug explícito. *Validar:* preguntar al usuario su rutina exacta.
4. **[HIPÓTESIS]** Con ~200 filas/mes y varios meses de historia, las listas de gastos superan ya las 50 filas y el usuario ve listas incompletas **hoy**. *Validar:* `SELECT count(*) FROM expenses` (solo lectura) o simplemente abrir la pantalla con la app arrancada.
5. **[HIPÓTESIS]** El volumen de datos actual es pequeño (el dump de junio ocupa ~89 KB comprimido), así que los problemas de rendimiento (P2-3, P3-1) no se sienten aún y el orden de trabajo no cambia: primero correcciones de exactitud (P0/P1) que de rendimiento. *Validar:* row counts en solo-lectura.
6. **[HIPÓTESIS]** La columna `balance` de los extractos ING es saldo acumulado tras el movimiento; en TR puede no serlo. *Validar:* muestras anonimizadas de la sección de saldos.
7. **[HIPÓTESIS]** El usuario quiere reglas **por usuario** o le sirve lo global (las reglas actuales no tienen `user_id`). *Validar:* pregunta directa (sección 15).
8. **[NO VERIFICABLE]** Si el qwen2.5-7b clasifica con calidad aceptable las descripciones de ING/TR (temperatura 0, categorías del sistema): solo probarlo en runtime con descripciones sintéticas. *Validar:* prueba local del endpoint `ai:8180` con 20 descripciones ficticias.
9. **[NO VERIFICABLE]** Comportamiento en producción/nginx (headers, TLS, caching): no revisado (ver Limitaciones).
10. **[HIPÓTESIS]** Que el frontend envíe `auto_categorize` implícito (default true) y categorías ya resueltas significa que el backend re-categoriza solo nulls que no existen → el pipeline backend de categorización casi no se ejercita hoy. *Validar:* log/temporizar en una importación real.

## 8. Flujo ideal de importación (propuesta, paso a paso)

Objetivo: **3 pasos principales + revisión de excepciones** (criterio de la sección 14), sin reescribir arquitectura:

1. **Paso 1 — "Suelta el fichero".** Una pantalla de importación que recuerda el último perfil usado por cuenta (campo `accounts.import_profile_id` ya existe, er.sql:32-33) y autoselecciona banco/cuenta/perfil; drag&drop del fichero. Con P1-1, si el `file_hash` del fichero coincide con un lote previo → mensaje inmediato "ya importado el X" y fin. [Los campos de cuenta ya existen; el recordatorio de "último perfil por cuenta" puede derivarse de ellos]
2. **Paso 2 — "Revisa excepciones, no filas".** La preview muestra: filas OK agrupadas y colapsadas por defecto; chips por estado: *sin categoría (N)*, *posible duplicado (N)*, *fecha rara (N)*, *descartable (N)*; sugerencia IA inline para los sin categoría (P1-5); acción "aplicar categoría a las seleccionadas" (P1-9); validación de cadena de saldos con el balance ya capturado (P1-2); marcar de una vez "todo OK → importar".
3. **Paso 3 — "Confirma y sabes qué pasó".** Botón confirmar → lote registrado (P1-1) → resumen final: insertadas X, duplicadas Y, sin categoría Z (visibles), **conciliación: saldo calculado vs extracto = 0,00 ✓ o diferencia explicada** → botón directo "ver este lote" (lista filtrada por batch_id con paginación real de P0-2).
4. **Continuo — "cada vez menos trabajo".** Al corregir una categoría, propuesta de regla aprendida (P1-6); las siguientes importaciones auto-clasifican más; la IA solo ve lo nuevo/ambiguo.

Cada paso marcado es implementable por piezas independientes; ninguna requiere reescribir el pipeline existente.

## 9. Arquitectura de importadores/adaptadores por entidad (propuesta, respetando la arquitectura actual)

Hoy el "adaptador" es un perfil de columnas genérico (jsonb) aplicado en el navegador. La extensión natural, sin cambiar de arquitectura:

- **Capa 1 — Perfiles (existente, ampliar):** `import_profiles.columns` sigue siendo la primera línea; para cada entidad se versiona (`import_profiles.version`, ya existe en er.sql:175) y se asocia a cuenta (`accounts.import_profile_id`). No tocar el parser genérico.
- **Capa 2 — Normalizadores por entidad (nuevo, backend):** si una entidad necesita más que un mapeo de columnas (p. ej. Trade Republic: tipos de operación "Buy/Sell/Dividend/Interest" en una columna de tipo, signos propios, fechas con hora), añadir en `api/services/imports/` una clase por entidad con la misma interfaz: `normalize(rows: list[dict]) -> list[NormalizedTransaction]`. Registro simple por `import_origins.code` (diccionario en un módulo, p. ej. `adapters/__init__.py` con `{"ing": IngNormalizer, "trade_republic": TradeRepublicNormalizer}`), con fallback al pipeline genérico actual si no hay adaptador. El frontend solo sube filas crudas+perfil; el backend normaliza y clasifica — mueve inteligencia al backend, que es la dirección que ya toma el proyecto (CLAUDE.md §7: "move logic to backend").
- **Capa 3 — Pipeline común (existente):** `ImportService.import_transactions_atomic` recibe la lista normalizada; dedup (sección 12), clasificación (sección 10), inserción, lote (P1-1), conciliación (P1-2) e informe.
- **Regla de oro:** ningún parser de Excel en el backend (el frontend ya lo hace bien con SheetJS y el perfil); los adaptadores solo interpretan **semántica** (tipos de operación, signos, divisa), no formato de fichero. Así el alta de una entidad nueva = crear perfil (asistente visual, P2-5) + opcionalmente un normalizador si tiene semántica propia.

## 10. Propuesta de clasificación automática y gestión de excepciones

Orden de resolución por movimiento (todo transparente, editable y auditable, antes de IA):

1. **Reglas de categoría activas** por prioridad DESC (existente, `categorization_service.py:139-145`) — ampliables con: patrón aprendido (P1-6) vs patrón manual con prioridad alta.
2. **Reglas de source independientes** (existente en BD; aplicarlas de verdad en import y desacoplarlas del match de categoría — P2-2).
3. **Memoria de correcciones del usuario** (nuevo): si el usuario corrigió esa misma descripción normalizada antes y no hay regla, sugerir la última categoría usada para esa descripción — implícito en P1-6 si la regla aprendida usa la descripción como patrón.
4. **IA local** solo para lo restante (P1-5): respuesta con categoría existente o `suggested_new_category`; nunca crea categorías sola — la sugiere en la preview.
5. **Null = excepción visible**: chip "sin categoría" en preview y lista post-import; filtro dedicado "revisar" en la pantalla de movimientos (requiere P0-2 para ser útil con >50 filas).

Reglas de convivencia (transición frontend→backend ya en curso): mantener `RuleCategorizerService` solo como *previsualización* de lo que el backend hará (hoy duplica la lógica con la misma BD de reglas — riesgo de divergencia documentado en P2-2); a medio plazo la preview debe pedir clasificación al backend (un endpoint de "dry-run" que devuelva hashes de duplicados + categorías propuestas sin insertar), eliminando el doble motor.

## 11. Tratamiento de transferencias propias e inversiones

**Transferencias (propuesta en 3 niveles):**

1. **Sin esquema (ya):** aplicar `ignore_in_analysis` en summaries (P0-3) + que las reglas asignen el flag (P2-2) + regla específica por descripción patrón ("TRASPASO", "TRANSFERENCIA ENTRE CUENTAS", IBAN propio en descripción si el extracto lo trae). Esto ya saca la mayoría del ruido de gasto/ingreso. El emparejamiento lógico puede hacerse **en la lista**: vista "posibles transferencias" que agrupa gasto+ingreso con mismo importe y fechas ≤3 días y cuentas distintas, con acción "marcar par como transferencia" (aplica ignore a ambos). [La ventana e importe exactos son configurables]
2. **Con esquema (después):** modelo `transfers` (id, expense_id, income_id, status, created_at) o `movement_type` en gastos/ingresos + `transfer_group_id`; emparejamiento automático al importar (importe igual, fechas ≤3 días, cuentas distintas, moneda igual) con revisión manual de candidatos; criterio de éxito 95% (sección 14) medible.
3. **Diferenciación de tipos:** transferencia propia ≠ ingreso/gasto real ≠ movimiento de inversión: con nivel 2, el import podría preguntar por clasificación cuando ambas mitades llegan en el mismo lote.

**Inversiones (realista con los datos que un extracto da):**

- Separar SIEMPRE **flujo de efectivo** (aportación, retirada, comisiones de custodia, dividendos en efectivo: encaja en `expenses`/`incomes` con `ignore_in_analysis` y cuenta de inversión) de **operación de activo** (compra/venta: necesita `investments_logs` con cantidad y precio). El extracto TR da las dos mezcladas; el normalizador (sección 9) las separa por la columna de tipo de operación.
- Con los datos de extracto **NO se puede** calcular: posiciones acumuladas fiables si hay transferencias de custodia, valoración de mercado (no viene), plusvalías no realizadas (requiere precio actual), TWR/rentabilidad temporal (requiere valoraciones). **Fuente necesaria:** importación de posiciones/valoración (CSV de posiciones de TR que existe como export aparte) o API/actualización manual de precio. [La disponibilidad concreta de esos ficheros para el usuario es [NO VERIFICABLE] — pregunta en sección 15]
- Hoy el modelo ya tiene donde guardar operaciones (`investments_logs`: cantidad, precio, acción) pero ni el import lo alimenta ni hay vista de posición/rentabilidad (revisados `investment_model.py`, `investment_log_model.py`; front `investments-log.component` existe como CRUD — no revisado a fondo, ver Limitaciones). Ampliar = nuevo trabajo, no reescritura.

## 12. Estrategia de deduplicación, idempotencia y conciliación

**Dedup fila (evitar duplicados sin perder legítimos):**

- Base: huella determinista existente `cuenta|fecha|importe|descripción normalizada` (`dedup_service.py:29-46`) + UNIQUE en BD (candado de concurrencia, mantener).
- Corrección de ocurrencias (P1-3): `hash_final = sha256(base|n)` con `n = 1 + nº de filas existentes con ese hash base`, calculado por lotes (`GROUP BY dedup_hash`) para evitar N+1. Las filas viejas (n implícito = 1) siguen encajando.
- Soft-delete (P1-4): el conteo de existentes debe contar también filas borradas (o revivirlas).
- Identificadores bancarios estables (operationId/valoración TR, id de apunte ING si el extracto lo trae): cuando el perfil/adaptador los tenga, añadir columna `external_id` + UNIQUE parcial — **con esquema**, y solo si los extractos reales los traen ([NO VERIFICABLE] sin muestras).

**Idempotencia de fichero:**

- Nivel 1 (sin esquema): header hash — el frontend calcula sha256 del fichero y lo envía; si un lote con ese hash existe (P1-1) → "ya importado el X" antes de parsear nada.
- Nivel 2: el mensaje de resultado ya distingue: `duplicates == total → "Este fichero ya estaba importado (N movimientos)"`; caso parcial: "añadidas X, omitidas Y como duplicadas".

**Conciliación (control de calidad por importación):**

1. Preview: validación de la cadena `balance[i] - balance[i-1] == amount[i]` (el dato ya llega del parser); filas sospechosas marcadas.
2. El usuario puede declarar saldo inicial/final (dos inputs opcionales; por defecto, inferidos del propio extracto).
3. Post-import (con lote): `saldo calculado = saldo inicial + Σ movimientos del lote`; diferencia vs saldo final declarado → 0,00 ✓ o mensaje concreto: "diferencia de X: revisa N movimientos marcados" (los que fallaron la cadena o quedaron sin importar/descartados).
4. Fechas/monedas raras ya cubiertas por P1-7/P1-8 como estados de excepción en preview.

## 13. Plan de mejoras incremental (ordenado por valor y riesgo)

**Ola 1 — sin esquema, alto valor/bajo riesgo (semáforo de exactitud):** antes de nada: restaurar el backup (P1-10). Después, en orden:

| # | Prioridad | Problema | Solución | Complejidad | Esquema |
|---|---|---|---|---|---|
| 1 | P1-10 | Backup parado | Restaurar cron + prueba de restauración | Baja | No |
| 2 | P0-1 / P2-6b | Filas sin categoría perdidas en silencio | Contar y avisar de excluidas en preview + excepciones tipadas en backend (no contar NOT NULL como "duplicado") | Baja | No |
| 3 | P0-2 | Listas de 50 sin orden | `ORDER BY date DESC, id DESC` + paginación server-side expuesta en routers + frontend | Baja-media | No |
| 4 | P0-3.1 | `ignore_in_analysis` ignorado en summaries | Filtrar en las 6 consultas de `SummaryRepository` | Baja | No |
| 5 | P0-3.2 / P2-2 | Source rules y flag no aplicados en import | Usar `categorize_transaction_with_flags` en `ImportService`; desacoplar source del match de categoría | Baja | No |
| 6 | P1-7 | Fechas un solo formato + error engañoso | Multi-formato en `toIsoDate` + errores tipados (`INVALID_DATE`...) | Baja | No |
| 7 | P1-4 | Soft-delete bloquea reimportación | Contar borradas en dedup + revivir | Baja | No |
| 8 | P2-1/P2-4/P3-2/P3-3 | Higiene: password en log, console.log, print(), `name` en incomes | Limpieza directa | Baja | No |

**Ola 2 — sin esquema, productividad (que sea más rápido que Excel en excepciones):**

| # | Prioridad | Problema | Solución | Complejidad | Esquema |
|---|---|---|---|---|---|
| 9 | P1-3 | Duplicados legítimos perdidos | Dedup con ordinal de ocurrencia (compatibilidad n=1) | Media | No |
| 10 | P1-6 | Sin aprendizaje de correcciones | Propuesta de regla al corregir ("recordar") + gestión | Baja-media | No |
| 11 | P1-5 | IA desconectada | Inyectar `TransactionAIService` en import bajo flag, solo nulls | Baja-media | No |
| 12 | P1-9 | Preview sin filtro/bloque | Chips por estado, "aplicar a seleccionadas", buscador, paginador | Media | No |
| 13 | P1-2 | Sin conciliación | Validación de cadena de saldos en preview + saldos declarados | Baja | No |
| 14 | P2-3/P2-8/P2-5 | N+1, endpoints bulk duplicados, perfiles JSON a mano | Batch queries; absorber `/expenses/bulk`; asistente de mapeo de columnas (reactivar ColumnMapper) | Media | No |

**Ola 3 — con esquema (migraciones nuevas, nunca tocar las viejas):**

| # | Prioridad | Problema | Solución | Complejidad | Esquema |
|---|---|---|---|---|---|
| 15 | P1-1 | Sin lotes/reversión | `import_batches` + `batch_id` nullable + endpoint de reversión soft + "ya importado" por file_hash | Media | **Sí** |
| 16 | P0-3.3 | Transferencias | Modelo/emparejamiento (nivel 2, sección 11) | Media-alta | **Sí** |
| 17 | P1-8 | Multi-divisa mal etiquetada | Moneda por defecto de la cuenta + override (etiquetado, no conversión) | Baja | No |
| 18 | P3-1/P2-10 | Índices date; aislamiento por usuario | Índices + scope en queries | Baja/media | Sí (índices) |
| 19 | P2-7 | Tests/CI | CI con pytest; tests de los criterios de sección 14 | Media | No |
| 20 | P2-6/P2-9 | er.sql obsoleto; dev escribe en BD real | Regenerar er.sql; `SCHEMA_INIT_STRATEGY=migrations` en dev | Baja | No |

Dependencias críticas: 15 depende de 1 (backup); 16 depende de 15 (lote para revisión); 3 depende de nada y destraba 12; el criterio "90% clasificación" (14) depende de 10+11 con ~2 meses de uso.

## 14. Criterios de aceptación verificables (sobre los objetivos propuestos)

Con ajustes razonados donde el objetivo original no es realista con lo encontrado:

1. **Idempotencia:** reimportar el mismo fichero sin ediciones intermedias → `inserted=0`, `duplicates=N`, mensaje que contenga "ya importado" o "N duplicados". *Verificación:* test de servicio con payload de 200 + reimportación manual. (Alcanzable en Ola 1-2; el mensaje exacto "ya importado" con file_hash llega con #15.)
2. **Solapes:** importar extracto con solape → 0 duplicados y **0 legítimas descartadas**. *Verificación:* test específico con dos compras idénticas mismo día mismo comercio → se insertan 2 (requiere #9).
3. **Clasificación ≥90% tras 2 meses:** medible como `1 - sin_categoría/total` al importar. *Ajuste razonado:* requiere #10 (aprendizaje) + #11 (IA) y datos de uso; **hito intermedio 70%** al cerrar Ola 2 solo con aprendizaje. Si el usuario rechaza reglas globales (household), recalcular.
4. **Revisión solo de excepciones:** la preview tiene filtro/chip "sin categoría" y "posible duplicado", y las filas OK se aceptan en bloque con **una** acción ("Importar todo lo OK"). *Verificación:* recorrido manual de escenario A.
5. **Esfuerzo ≤3 pasos:** paso 1 = soltar fichero (contexto banco/cuenta/perfil autocompletado del último uso), paso 2 = revisión de excepciones, paso 3 = confirmación; sin recuento de selectores obligatorios >0 antes del fichero salvo primera vez. *Verificación:* cronometraje del escenario A tras Ola 2-3.
6. **Transferencias ≥95% emparejadas** (importe igual, fechas ≤3 días) y contadas como gasto/ingreso 0 veces. *Ajuste razonado:* el 95% requiere el modelo de transferencias (#16); **criterio intermedio (Ola 1): 100% de las transferencias clasificadas como `ignore_in_analysis` por regla no aparecen en totales** (verificación: test en summaries).
7. **Conciliación:** tras cada importación, `saldo calculado - saldo extracto = 0,00` o explicación concreta con las filas sospechosas. *Verificación:* importación con extracto real + una fila manipulada → la preview la marca.
8. **Reversión:** `DELETE /imports/batches/{id}` revierte el lote completo (soft) sin afectar a otros lotes ni histórico previo; los movimientos editados después del lote quedan excluidos de la reversión con aviso. *Verificación:* test con 3 lotes entrelazados (requiere #15).
9. **Inversiones:** ninguna operación de trading cuenta como gasto/ingreso ordinario sin la marca `ignore_in_analysis` o tipo inversión; la UI muestra el aviso "posiciones/valoración/rentabilidad requieren ficheros de posiciones (no incluidos en extractos)". *Verificación:* escenario D con extracto TR sintético.
10. **Seguridad/privacidad en logs:** `grep -R "Database URL" logs/` no muestra credenciales (parche #8-ola-1); ninguna línea de log de import contiene descripciones/importes (hoy ya cumple: `import_service.py:189` solo contadores [CONFIRMADO]); sin `console.log` de payloads en build de producción. *Verificación:* auditoría de `logs/app.log` tras una importación real.

## 15. Información que necesito para completar el análisis

1. **Dos extractos anonimizados** (cabeceras + 3-5 filas con datos ficticios, o estructura/tipos de celda): ING y Trade Republic. Crítico: formato real de fechas, columna(s) de importe (¿firmada única o cargo/abono?), presencia de id de operación estable y columna de saldo.
2. **Extracto de posiciones/valoración de TR** (si existe como export): para decidir el alcance de posiciones/rentabilidad.
3. **Rutina actual exacta:** ¿importas cada extracto una vez? ¿qué haces hoy con las transferencias entre cuentas (marcas descartable a mano?)? ¿cuántas reglas tienes creadas y te valen las reglas globales (compartidas en el hogar)?
4. **Conflicto de números:** ¿ya has notado que las listas de gastos/ingresos muestran ~50 filas y/o que faltan movimientos tras importar? (confirmaría P0-2 en producción).
5. **Preferencias de producto:** ¿reversión por lote o basta borrar por rango de fechas+cuenta? ¿Quieres multi-divisa real (con conversión) o solo etiquetado correcto?
6. **Operación:** acceso a `crontab -l` del host para confirmar el estado del backup; permiso para, en una siguiente sesión, arrancar la app con `APP_ENV=testing` y una BD de prueba (nunca la real) para las verificaciones de runtime.
7. **IA:** ¿quieres la IA local en el flujo (flag activable) o prefieres solo reglas aprendidas?

## 16. Limitaciones de esta auditoría

1. **Sin ejecución runtime.** El modo de permisos de la sesión bloqueó Docker, la ejecución de Python y las herramientas multiagente (Workflow/Agent; error "Auto mode is unavailable"). No se arrancó ningún contenedor ni se consultó la BD real (no hay cliente `psql` en el host y Python estaba bloqueado). Toda conclusión sobre datos (volúmenes, rangos de fechas, distribución de nulos) y EXPLAIN quedó sin hacer; los hallazgos se apoyan en esquema (er.sql), modelos, migraciones y código.
2. **Verificación adversarial reducida.** El plan original (workflow con verificadores independientes por hallazgo) no pudo ejecutarse; en su lugar se hizo una segunda pasada de re-lectura directa de cada fuente citada en P0/P1. Las evidencias corresponden a lecturas directas de los ficheros.
3. **Recuentos de clics/tiempos:** derivados de la estructura del código, no de sesiones reales; marcados [HIPÓTESIS] donde aplica. El coste temporal real de cada acción es [NO VERIFICABLE].
4. **Ficheros no abiertos** (por alcance o política): `.env`, `.env.prod`, `backups/*.dump`, `database/postgres/**`, `database/economy.db`, `api/logs/**`, `logs/**`, `nginx/nginx.conf`, `client/Dockerfile`, `backups/restore_postgres.sh` (contenido), `api/templates/**`, `api/scripts/auto_generate_crud.py`, `api/FASTAPI_GUIDE.md`, `api/REFACTOR_REPORT.md`, `docs/001-backend/**`, `docs/002-frontend/**`, `docs/old_to_delete/**`, contenido de `api/i18n/**`, y los ficheros backend/frontend listados a continuación. Consecuencias concretas de esto: (a) el orden "prioridad DESC" de las reglas se apoya en el docstring del servicio (`categorization_service.py:96`) y en el ordenado equivalente del frontend (`rule-categorizer.service.ts:137-139`), **no** en el SQL de `CategoryRuleRepository.get_active_by_type` (no abierto); (b) nginx (rutas TLS/headers) y el Dockerfile del frontend sin revisar; (c) routers/servicios de inversión, savings, households, users, auth_dependencies, jwt_service, response_service (solo vistos por grafo/uso), `transactions_ai_router.py` (solo registro), `summary_router.py`, repositorios de reglas e incomes: revisados por llamadas y grafo, no línea a línea.
5. **Datos personales:** no se abrieron extractos, dumps ni envs; ningún dato financiero personal aparece en este documento; los nombres de ficheros de backup se citan solo como evidencia de antigüedad.
6. **er.sql vs BD real:** er.sql (export pgAdmin, con sección declarada obsoleta en P2-6) y las migraciones no siempre coinciden con los modelos; el estado real de la BD (qué columna tiene NOT NULL `category_id` aplicado, si `expenses.user_id` existe ya en la BD física) es [NO VERIFICABLE] sin conexión de solo lectura.
7. **Crontab del host:** [NO VERIFICABLE] (no accesible desde la sesión).

---

## Cierre de la auditoría

**Resumen de hallazgos (los P0/P1):** el motor de importación existe y es sólido (parseo por perfil, dedup determinista, atomicidad, reglas priorizadas), pero el flujo end-to-end pierde filas sin categoría en silencio (P0-1), no permite revisar lo importado (listas de 50 sin orden, P0-2), y las transferencias propias distorsionan todos los totales porque el flag "descartable" no se aplica en los resúmenes (P0-3). Encima: sin lotes ni reversión (P1-1), sin conciliación aunque el saldo del extracto se captura y se tira (P1-2), dedup que come compras legítimas idénticas (P1-3), soft-delete que bloquea reimportaciones (P1-4), IA pagada y desconectada (P1-5), cero aprendizaje de correcciones (P1-6), un solo formato de fecha con error engañoso (P1-7), EUR fijo (P1-8), preview sin filtros ni acciones en bloque (P1-9) y backup parado desde junio (P1-10). ~70% del plan de mejora es código sin tocar esquema.

**Confirmación:** NO se ha modificado ningún código, dato, esquema, dependencia ni configuración del repositorio. La única escritura realizada es este documento (`docs/audits/UX_PRODUCTIVITY_IMPORT_AUDIT.md`) y la creación de su directorio.

**Comandos/herramientas ejecutados (todos de lectura salvo la creación del directorio/documento):**
- Listado y búsqueda de estructura: `ls -la`, `find` (varios), `grep` (varios, sobre código fuente).
- Lectura de ficheros con Read: docker-compose.yml, README.md, Makefile, .env.example (NO .env ni .env.prod), api/app.py, api/config.py, api/db/database.py, api/Dockerfile, er.sql completo, modelos/repositories/routers/services/schemas citados en evidencias, tests, backups/*.sh + backups/README.md (solo el script, no los dumps), client/package.json, componentes/servicios frontend citados, docs/Economy.md.
- Grafo de código (solo lectura): `get_architecture` (routes/entry_points/hotspots) vía codebase-memory MCP.
- Intentos DENEGADOS por el modo de permisos de la sesión (no ejecutados): `docker ps -a`, `docker volume ls`, `python3 -c` (intento de driver PostgreSQL), herramienta Workflow (orquestación multiagente), herramienta Agent.
- **Comandos de base de datos ejecutados: ninguno.** No hubo ninguna conexión a PostgreSQL. **Contenedores arrancados: ninguno.**

