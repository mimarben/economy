# Ola 1 — Implementación (2026-11-13)

Cambios aplicados sobre el plan de `UX_PRODUCTIVITY_IMPORT_AUDIT.md` §13 (Ola 1 + aprendizaje de reglas). **Sin migraciones, sin cambios de esquema, sin breaking changes de API** (solo extensiones opcionales).

## Cambios backend

| Ítem | Fichero | Qué hace |
|---|---|---|
| P0-2 | `api/repositories/core/base_repository.py` | `get_all` ordena `date DESC, id DESC` (fallback `id DESC`) |
| P0-2 | `api/routers/expenses/expense_router.py`, `api/routers/incomes/income_router.py` | `GET /expenses` y `GET /incomes` aceptan `?page=&per_page=` (default per_page=1000 → el frontend existente ya ve todo, newest-first) |
| P0-3.1 | `api/repositories/summaries/summary_repository.py` | Las 8 consultas de gastos/ingresos excluyen `ignore_in_analysis=true` → transferencias/tarjeta dejo de inflar totales |
| P0-3.2 / P2-2 | `api/services/rules/categorization_service.py` | Source rules se evalúan SIEMPRE (no solo si hay match de categoría); `print`→logger |
| P0-3.2 | `api/services/imports/import_service.py` | El import usa `categorize_transaction_with_flags` → reglas pueden marcar `ignore_in_analysis` y source |
| P1-4 | `api/services/imports/import_service.py` + repos de expenses/incomes (`get_by_dedup_including_deleted`) | Reimportar tras soft-delete **revive** la fila en vez de "duplicado" fantasma |
| P2-6b | `api/services/imports/import_service.py` | `IntegrityError` solo cuenta como duplicado si es la constraint de dedup; cualquier otra violación → error claro (no más filas perdidas contadas como duplicadas) |
| P1-6 | `api/services/expenses/expense_service.py`, `api/services/incomes/income_service.py` | **Aprendizaje**: al corregir la categoría de un movimiento, si ninguna regla cubre su descripción se crea automáticamente una regla exacta (prioridad 10, activa). La próxima importación se clasifica sola |
| P3-3 | `api/schemas/imports/import_schema.py` | `name` opcional en `IncomeImportCreate` (el modelo Income no tiene `name`) |
| P2-1 | `api/db/database.py` | La URL de BD se loguea con la contraseña enmascarada |
| Bug nuevo | `api/routers/incomes/income_router.py:102` | Typo `esponse` → `Response` (borrar un ingreso petaba con NameError) |

## Cambios frontend

| Ítem | Fichero | Qué hace |
|---|---|---|
| P1-7 | `client/src/app/utils/utils.service.ts` | `toIsoDate` acepta dd/MM/yyyy, dd-MM-yyyy, dd.MM.yyyy, yyyy-MM-dd, yyyy/MM/dd, dd/MM/yy, ISO con hora |
| P0-1 | `client/src/app/features/import/excel/excel-import.component.ts` | Avisos con conteos: filas descartadas sin importe, transacciones sin categoría antes de importar, y tras importar cuántas quedaron fuera por falta de categoría |
| P2-4 | idem | Eliminados los `console.log` que volcaban datos financieros |

## Tests añadidos (EJECUTAR — no pude por permisos de la sesión)

```bash
cd api && python -m pytest tests/ -q   # (o tu runner habitual: uv run pytest)
```

- `tests/test_import_service.py::test_import_revives_soft_deleted_transaction` — revive tras soft-delete.
- `tests/test_rule_learning.py` (3 tests) — aprendizaje de reglas: crea regla al corregir, no crea si la categoría no cambia, no duplica reglas.

## Verificación manual recomendada

1. Reiniciar backend (los cambios son código puro, sin migraciones): `docker compose restart backend` (o `up -d --build`).
2. Abrir `/expenses`: deben salir TODOS los movimientos, los más nuevos arriba.
3. Comprobar gráficos/resumen: si tienes movimientos marcados "descartable", los totales deben bajar acorde.
4. Editar la categoría de un gasto → aparece una regla `auto: ...` en `category_rules` → reimportar un extracto con esa descripción → se clasifica sola.
5. Probar reimportar un extracto tras borrar un movimiento: debe revivir.

## Nuevo hallazgo registrado (de tus respuestas) — Carrefour Pass

Gastos con tarjeta Pass: el extracto de Pass tiene el **detalle** y en ING aparece **un cargo diario agregado** ("CARREFOUR PASS" un importe al día, no lineal). Esto es un problema de **conciliación agregada** (N detallados ↔ 1 agregado por día): el dedup actual no lo cubre y exige emparejamiento por suma diaria. Propuesto para Ola 2/3 (requiere la vista de conciliación y posiblemente lotes). Anotado como **P1-11** pendiente de diseño.

## Pendiente de tus respuestas / siguiente sesión

- [ ] **Ejecutar pytest** (bloqueado en esta sesión).
- [ ] **crontab -l** del host: confirmar backup (yo no pude).
- [ ] Convertir `docs/movements/*.xls` a **CSV** para que analice cabeceras/formatos/fechas (el .xls binario no lo puedo parsear sin Python).
- [ ] Ola 2: preview con filtros por estado + "aplicar categoría a seleccionadas" (P1-9), conciliación de saldos en preview (P1-2), dedup con ordinal para compras legítimas idénticas (P1-3).
- [ ] IA local: dejada **fuera** del flujo (tu indicación: lenta; con aprendizaje de reglas cubre el 90%). El flag queda diseñado en el informe (P1-5) por si cambias de modelo (efectivamente hay alternativas más rápidas que qwen2.5-7b en llama.cpp).
