# Verificación de Olas 1 y 2 — Informe de entrega (2026-11-14)

Ciclo de verificación del trabajo de `OLA1_IMPLEMENTATION.md` (2026-11-13) y `OLA2_IMPLEMENTATION.md` (2026-11-14), según el Prompt 2 (fases 1-4). Todo el trabajo permanece **sin commit** a petición del usuario.

## 1. Resumen comportamiento anterior → nuevo

Cubierto en detalle por los informes de Ola 1 y Ola 2. En una línea: antes la importación perdía filas en silencio, las listas no mostraban lo importado, las transferencias/tarjeta inflaban los totales, borrar bloqueaba la reimportación para siempre, y la corrección de categorías no aprendía; ahora hay conteos y avisos, listado ordenado y paginado, resúmenes que excluyen `ignore_in_analysis`, reimportación que revive lo borrado, dedup que admite compras idénticas legítimas, preview con filtros/bloque/buscador/conciliación de saldos, y aprendizaje automático de reglas.

## 2. Archivos modificados y creados

Según `git diff --stat` (inicio de sesión, pre-fix): **19 archivos modificados, +679/−79**, más los creados:

- `api/tests/test_rule_learning.py` (nuevo, 3 tests; +corrección de hoy)
- `docs/audits/` (auditoría e informes), `docs/floorplans/`

Correcciones de hoy (2026-11-14, ciclo del punto de control 2):

1. `api/tests/test_rule_learning.py` — `_make_expense()` y el segundo `Expense` de `test_no_duplicate_rule_learned` ahora asignan `user_id` + `is_personal=True` (el fixture no reflejaba la app real, donde siempre hay usuario asignado).
2. **Bug real del aprendizaje (Ola 1)** — `expense_service.py` / `income_service.py`: `existing` es el mismo objeto ORM que `super().update()` muta (identity map), así que `category_changed` comparaba el valor nuevo consigo mismo → siempre `False` → el aprendizaje jamás se ejecutaba. Corregido capturando `previous_category_id`/`previous_description` ANTES del update. Detectado gracias al test nuevo (2 failed).
3. **Miembros de enum inexistentes** — `TransactionEnum.expense`/`.income` (minúscula) usados en el código de aprendizaje nuevo (Ola 1) y en código PREEXISTENTE de `categorization_service.py:49-57` (`_get_category_model_by_type`, usado al crear reglas vía API/UI). Verificado con el usuario que `TransactionEnum.expense` lanza `AttributeError` → **crear reglas de categoría desde la UI estaba roto en producción** (bug preexistente, ajeno a las Olas 1/2). Corregidos los 6 accesos a `EXPENSE`/`INCOME`/`INVESTMENT` en los 3 ficheros.

## 3. Cambios de API

Solo **extensiones opcionales compatibles hacia atrás**:

- `GET /expenses` y `GET /incomes` aceptan `?page=&per_page=` (defaults 1/1000 → respuesta idéntica a antes para clientes existentes, ahora ordenada date DESC).
- `IncomeImportCreate.name` pasa de requerido a opcional (relaja, no rompe).
- Resto de cambios son internos (servicios/repositorios) o frontend.

## 4. Esquema de PostgreSQL

**NO tocado.** Ninguna migración generada ni aplicada; ningún DDL; la BD real no ha recibido ni una consulta de esta sesión. Verificado: la suite usa SQLite en memoria (`api/tests/conftest.py:27`).

## 5. Pruebas ejecutadas (reales, con comparación)

| Comando | Resultado | Estado |
|---|---|---|
| `cd api && .venv/bin/python -m pytest tests/ -q` (ejecutado por el usuario, pre-fix) | **3 failed, 41 passed** — fallos: los 3 tests de aprendizaje, por fixture sin `user_id` (bug del test, no del código de producción) | [HECHO Y COMPROBADO] |
| `cd client && npm run build` (ejecutado por el usuario) | **OK** en 4,6 s; único warning: presupuesto CSS de `generic-table.component.css` (preexistente, no relacionado) | [HECHO Y COMPROBADO] |
| Re-ejecución de pytest tras los 3 fixes (usuario) | **2 failed, 42 passed** (2ª ejecución, tras fix del fixture: fallos por aprendizaje que nunca ejecutaba, ver corrección 2) | [HECHO Y COMPROBADO] |
| Re-ejecución final tras fixes 2 y 3 | — | **[PENDIENTE]**: `cd api && .venv/bin/python -m pytest tests/ -q` → esperado **44 passed, 0 failed** |

No existen fallos preexistentes en la suite: los 41 verdes incluyen todos los tests antiguos.

## 6. Criterios de aceptación de la auditoría (§14) cubiertos

| Criterio | Estado | Cómo se verifica |
|---|---|---|
| 1. Idempotencia (reimportar = 0 nuevas + mensaje) | ✅ código | test `test_import_identical_legitimate_transactions_both_inserted` (pasó) + toast con contadores; "ya importado" exacto llega con lotes (Ola 3) |
| 2. Solapes sin perder legítimas | ✅ código | dedup ordinal por posición en fichero (test pasó) |
| 3. Clasificación ≥90 % | ◐ avance | aprendizaje de reglas activo (3 tests, a re-verificar); sin IA (decisión del usuario) |
| 4. Revisión solo de excepciones | ✅ código | filtros "Sin categoría"/"Saldo ✗"/"Descartables" + buscador + paginador en preview (build OK) |
| 6. Transferencias no cuentan en totales (criterio intermedio Ola 1) | ✅ código | `ignore_in_analysis` excluido en las 11 consultas de summaries (verificación manual: gráficos) |
| 7. Conciliación | ◐ preview | `validateBalanceChain` marca filas y avisa; persistencia en lote → Ola 3 |
| 10. Privacidad en logs | ✅ código | password de BD enmascarada; `console.log` de payloads eliminados; logs de import solo contadores |

## 7. Riesgos y limitaciones pendientes

1. **Re-ejecutar pytest tras el fix del fixture** (único pendiente inmediato).
2. Dedup ordinal: subsets solapantes de un mismo día pueden desalinear ordinales (asunción documentada: los extractos listan días completos). Detectable en la práctica si aparecen "duplicados" inesperados.
3. Latente preexistente (no de Ola 1/2): un gasto con `user_id=None` no puede editarse vía `ExpenseService.update` (`ExpenseRead` exige usuario si `is_personal`). Hoy no se reproduce (el frontend siempre asigna usuario). Decisión de producto pendiente.
4. Backup (P1-10) **sin confirmar** — sigue bloqueando Ola 3.
5. Verificación manual en runtime (lista de OLA1 §"Verificación manual") aún no hecha: requiere reiniciar backend.

## 8. Plan de reversión

Todo el trabajo está **sin commit**: `git checkout -- .` + borrar los no rastreados (`api/tests/test_rule_learning.py`, `docs/audits/`, `docs/floorplans/`) devuelve el repo a `6e964ce`. No hay migraciones ni datos que revertir. Para revertir solo hoy: restaurar `test_rule_learning.py` sin `user_id`/`is_personal` en los dos constructores.

## 9. Pasos manuales de validación (runtime, con datos de prueba)

1. Reiniciar backend: `docker compose up -d --build backend` (sin migraciones).
2. `/expenses` y `/incomes`: todos los movimientos, los más nuevos arriba.
3. Gráficos: si hay marcados "descartable", los totales bajan acorde.
4. Editar categoría de un gasto → regla `auto: ...` en `category_rules` → reimportar esa descripción → se clasifica sola.
5. Reimportar un extracto tras borrar un movimiento → revive (no "duplicado").
6. Importar extracto con dos idénticos mismo día → entran los dos; reimportar el fichero → 0 nuevas, N duplicados.
7. En la preview: filtros de estado, buscador, categoría en bloque, aviso de descuadres de saldo.

## 10. Propuesta de siguiente unidad

**Verificación manual en runtime (paso 9)** para cerrar del todo Ola 1/2, y en paralelo confirmar el **backup** (P1-10: `crontab -l`, prueba de restauración). Con backup confirmado + tu autorización explícita de esquema → **Ola 3: lotes de importación y reversión (P1-1)**, que desbloquea además el "ya importado" exacto, la conciliación persistida y el análisis Pass↔ING (P1-11).

## 11. Estado de control

Sin commit, sin push. Esperando validación del usuario (PUNTO DE CONTROL 3) — preferiblemente tras la re-ejecución de pytest.
