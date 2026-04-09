# Notas rápidas: Import Excel + inversiones (sin refactor grande)

## 1) Guardado del import: transacción atómica

Para un import de Excel conviene guardar en **una sola transacción**:

- ✅ si todo va bien: se guardan todas las filas.
- ❌ si falla una fila: rollback completo (no se guarda ninguna).

En esta base ya existe endpoint:

- `POST /expenses/bulk`
- `POST /incomes/bulk`

Ese endpoint valida y persiste todo en bloque con comportamiento all-or-nothing.

### ¿Y si separo en 2 llamadas (`expenses/bulk` + `incomes/bulk`)?

Con **dos peticiones HTTP distintas** no hay atomicidad global garantizada.

- Puede guardarse `expenses` y fallar `incomes`.
- Para evitar duplicados/parciales, la opción robusta es un endpoint único tipo:
  - `POST /imports/transactions/bulk-atomic`
  - body: `{ expenses: [...], incomes: [...] }`
  - una sola transacción en backend para ambos bloques.

## 2) Reglas + IA para categorizar

Flujo recomendado:

1. Parsear Excel
2. Aplicar reglas deterministas (rápidas y baratas)
3. Mandar solo "uncategorized" a IA
4. El usuario confirma
5. Persistencia atómica con `/expenses/bulk`

## 3) Investments: histórico de saldos e inversiones

El modelo actual con `investments` + `investments_logs` es correcto para histórico:

- `investments`: posición / activo
- `investments_logs`: eventos y snapshots (`current_value`, `price_per_unit`, `units_bought`, `action`, `date`)

Recomendación práctica:

- crear un log por cada operación (buy/sell/dividend/fee).
- opcional: un snapshot diario (EOD) para curvas de patrimonio más limpias.

## 4) API libre para precios (BTC, S&P 500, fondos)

Opciones gratuitas típicas:

- **Bitcoin / crypto**: CoinGecko (simple y sin key para uso básico).
- **S&P 500 y ETFs/acciones**: Stooq (CSV gratuito) o Alpha Vantage (free tier con límites).
- **Fondos**:
  - Yahoo Finance (símbolos de fondos cuando existan).
  - Alpha Vantage / Twelve Data (según cobertura del fondo y límites).

Consejo: empezar con 1 proveedor principal + 1 fallback.

## 5) Librería de gráficos para después

En Angular, recomendación simple:

- **ApexCharts (`ng-apexcharts`)** para arrancar rápido en dashboards financieros.

Alternativas:

- ECharts (muy potente y flexible).
- Chart.js (simple, pero menos cómodo para series complejas financieras).
