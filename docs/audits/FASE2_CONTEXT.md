# Contexto fijo Fase 2 — Economy App (inversiones)

Lee este fichero y docs/audits/fase1.md al empezar. Responde en castellano.

## Decisiones aprobadas (no reabrir)
D1 Posición derivada en servicio, sin tabla `positions`.
D2 investments_logs híbrido: legacy = snapshot (último log); nuevas filas = eventos por tipo de acción.
D3 Eulerpool proveedor primario, Yahoo fallback (cadena ya existente).
D4 Categorías: reutilizar investments_categories + asset_class estricto (ETF|FUND|STOCK|CRYPTO|BOND|MANAGED_PORTFOLIO|OTHER).
D5 Moneda base EUR con tabla fx_rates (BCE). Sin tasa → None + estado, nunca inventar.
D6 Método de coste FIFO.
D7 DELETE de inversiones solo admin y solo sin historial financiero; lo normal es vender → CLOSED.
D8 Filtrar dashboard/investments por cuentas del usuario (salvo admin).
D9 portfolio_valuations pospuesto; sí quoted_at e historia de cotizaciones.
D10 Reconciliación bancaria: solo trazabilidad (source_id, external_ref), sin matching automático.

## Reglas
- Arquitectura: Router → Service → Repository → DB. Reutiliza BaseService/BaseRepository. Sigue CLAUDE.md.
- Cambios aditivos y nullable. No renombrar ni cambiar tipo de campos/contratos de API existentes.
- Nunca modificar migraciones históricas de Alembic; solo crear nuevas, con downgrade().
- Nunca leer, imprimir ni registrar EULERPOOL_API_KEY. No hacer cat de .env.
- ISIN nunca obligatorio ni PK. Una cartera gestionada nunca suma el valor de sus componentes.
- Precios históricos de compra inmutables. Prohibido inventar precios o tasas FX.
- Toda regla financiera nueva lleva tests. Si un test falla: no lo debilites ni borres; arregla el código o para y pregunta.
- No toques nada fuera del alcance del incremento. Si dudas, pregunta antes.
- Un único incremento por sesión.

## Cierre obligatorio de cada incremento
1. Ejecuta pytest completo y pega el resultado real (antes y después).
2. `git diff --stat` y confirma que no se tocó ninguna migración histórica.
3. Informe: ficheros modificados, migraciones creadas, tests añadidos, limitaciones, pendientes.
4. No afirmes que algo funciona si no lo has ejecutado.
