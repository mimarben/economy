# Ola 2 — Implementación (2026-11-14)

Continuación de `OLA1_IMPLEMENTATION.md` (plan del informe §13, Ola 2). **Sin migraciones ni cambios de esquema.**

## Cambios backend

### P1-3 — Dedup con ordinal: las compras legítimas idénticas ya no se pierden

`api/services/imports/import_service.py` (Step 4) + tests.

Esquema: cada fila recibe un ordinal = su **posición dentro de su familia** (misma cuenta+fecha+importe+descripción) **en el fichero**. La ocurrencia 0 conserva el hash base (compatibilidad total con tus filas actuales); la ocurrencia N se guarda como `<base>|<N>`.

Por qué la posición del fichero y no un contador de BD: los extractos listan días completos, así que cualquier export que cubra un día contiene TODAS las transacciones de ese día → la posición de una ocurrencia dentro de su familia es estable entre exportaciones. Esto garantiza:

- **Idempotencia**: reimportar el mismo fichero reproduce los mismos ordinales → todo son duplicados, 0 insertados. (Un contador contra BD lo habría roto: habría creado `|N` nuevas.)
- **Dos cafés idénticos el mismo día**: primera importación → base + `|1`, ambas se insertan.
- **Solape de periodos**: filas ya importadas → duplicadas; hermanas nuevas → insertadas.
- **Filas legacy**: todas tienen hash base = ordinal 0 → siguen cuadrando.

### Test añadido

`tests/test_import_service.py::test_import_identical_legitimate_transactions_both_inserted` — cubre inserción de 2 idénticas + reimportación idempotente del mismo fichero.

## Cambios frontend (`excel-import`)

### P1-9 — Revisión por excepciones

- **Barra de filtros por estado** con conteos: *Todas / Sin categoría (N) / Saldo ✗ (N) / Descartables (N)* (`excel-import.component.html`, toolbar `review-toolbar`).
- **Buscador** de descripción (normalizado, sin acentos) sobre la preview.
- **Categoría en bloque**: seleccionas filas → eliges tipo (gasto/ingreso) + categoría → "Aplicar en bloque" (respeta el tipo: no aplica una categoría de gasto a un ingreso) (`applyBulkCategory()` en el componente).
- **Paginador** (25/50/100/200) en la tabla de preview.

### P1-2 — Conciliación del saldo del extracto en la preview

- `validateBalanceChain()` comprueba fila a fila `saldo[i] == saldo[i-1] + importe[i]`; las filas que no cuadran quedan marcadas con ⚠ en la columna Balance (tooltip explicativo) y contabilizadas en el filtro "Saldo ✗".
- Toast al terminar el parseo si hay descuadres: posibles filas ausentes, descartadas o mal parseadas.
- Si el extracto no trae saldo utilizable, la validación se desactiva sola (no bloquea).

## Verificación manual recomendada

1. Reiniciar backend y recargar frontend (sin migraciones).
2. `cd api && python -m pytest tests/ -q` — ejecutar TODA la suite (añadidos 2 tests nuevos en Ola 1 + 1 en Ola 2; los 3 de aprendizaje + revive + idénticas).
3. Importar un extracto real de ING con dos movimientos idénticos el mismo día → deben entrar los dos.
4. Reimportar el mismo fichero → "0 importadas, N duplicados".
5. En la preview: probar los filtros "Sin categoría" y "Saldo ✗", el buscador, seleccionar varias y aplicar categoría en bloque.

## Pendiente

- [ ] Ejecutar pytest (bloqueado por permisos en esta sesión).
- [ ] `docs/movements/*.xls` → CSV para análisis de formatos (fechas/ids de operación).
- [ ] crontab del host (backup).
- [ ] Ola 3 (con esquema): lotes de importación + reversión (P1-1), transferencias propias (P0-3.3), y el problema Pass↔ING (P1-11: cargo diario agregado vs detalle — necesita la vista de conciliación por lotes).
