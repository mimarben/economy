# Excel Import: arquitectura simple (paso a paso)

Este módulo ahora está pensado para aprender y mantenerlo profesional sin magia oculta.

## Flujo recomendado

1. **Seleccionar banco/formato** en UI.
2. **Cargar Excel** y validar cabeceras solo contra ese formato.
3. **Parsear filas** y generar `pendingTransactions`.
4. **(Opcional) Clasificar con IA** si el checkbox está activo.
5. **Revisión manual** en tabla.
6. **Guardar** gastos/ingresos seleccionados.

## Por qué así

- Evita ambigüedad al detectar formatos bancarios.
- Te permite importar sin bloquearte por la IA.
- Facilita depurar: primero parser, luego clasificación.

## Próximos pasos profesionales

- Extraer `COLUMN_MAPS` a un fichero `bank-format.registry.ts`.
- Añadir tests con ejemplos reales por banco (1 Excel mínimo por banco).
- Guardar trazas de clasificación (descripción + categoría sugerida + confianza).
- Introducir una regla de fallback: si IA falla, mantener categoría por keywords y marcar para revisión.
