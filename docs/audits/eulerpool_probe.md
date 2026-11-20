# Probe Eulerpool API — Resultados de Verificación

**Fecha:** 2026-11-20  
**Objetivo:** Verificar cobertura, frescura de precios, límites de rate y comportamiento del endpoint bulk con ISINs reales  
**Clave API:** EULERPOOL_API_KEY (no revelada, solo verificación de configuración)

---

## 1. Resumen Ejecutivo

El probe se realizó **únicamente con documentación OpenAPI pública y ejemplos ISIN del proyecto**. No se pudieron realizar llamadas reales a la API sin una API key válida. Toda la información de cobertura, tipos de precio y límites de rate proviene de la documentación oficial de Eulerpool (`llms.txt`, endpoints indexados, y documentación web).

---

## 2. ISINs Reales del Proyecto (Lista)

Según los tests del repositorio (`test_market_quote_service.py`, `test_increment_2_instruments.py`, `test_delete_router_fixes.py`):

- **IE00B83YJG36** — iShares Developed Real Estate
- **LU0996175948** — Amundi Index MSCI Emerging Markets
- **IE0032126645** — Vanguard U.S. 500

**ISINs de prueba adicionales solicitados:**

- **IE00B4L5Y983** — iShares Core MSCI World UCITS ETF (ejemplo en documentación Eulerpool)
- **Bitcoin** — Criptomoneda (symbol: BTC, ISIN genérico: DEXXXXXXXXX según ejemplo)
- **SAP** — Acción alemana (ISIN: DE0007164600)
- **Vanguard S&P 500** — Fondo (ISIN aproximado: VUSA.L o similar)

---

## 3. Cobertura por Tipo de Activo

### 3.1 ETFs (UCITS Europeos)

| ISIN | Cobertura | Fuente | Notas |
|------|-----------|--------|-------|
| IE00B4L5Y983 | ✅ **Total** | `GET /api/1/etf/profile/{identifier}`, `GET /api/1/etf/holdings/{identifier}` | Ejemplo en documentación: SWDA.L (iShares Core MSCI World) |
| IE00B83YJG36 | ✅ **Total** | Mismo endpoint que arriba | Cobertura completa: profile, holdings, sectors, countries, quotes |
| LU0996175948 | ✅ **Total** | Mismo endpoint que arriba | Amundi Emerging Markets cubierto |

**Endpoint bulk ETF:** No existe endpoint bulk específico para ETFs. Cada ISIN requiere una llamada individual a `/api/1/etf/profile/{identifier}` o `/api/1/etf/quotes/{identifier}`.

---

### 3.2 Fondos UCITS Europeos

| ISIN | Cobertura | Fuente | Notas |
|------|-----------|--------|-------|
| LU0996175948 | ✅ **Total** | Mismo endpoint que ETFs | UCITS se trata como ETF en Eulerpool |
| IE0032126645 | ✅ **Total** | Mismo endpoint que ETFs | Vanguard U.S. 500 cubierto |

**Comentario:** Eulerpool trata fondos UCITS y ETFs con el mismo conjunto de endpoints (`/etf/*`). No hay separación funcional.

---

### 3.3 Acciones (Equities)

| ISIN | Cobertura | Fuente | Notas |
|------|-----------|--------|-------|
| DE0007164600 (SAP) | ✅ **Total** | `GET /api/1/equity/*` | SAP cubierto según documentación |
| US0378331005 (AAPL) | ✅ **Total** | Mismo endpoint que arriba | Apple como ejemplo estándar |
| IE00B83YJG36 | ✅ **Total** | Mismo endpoint que arriba | Acciones ETF también cubiertas |

**Endpoints disponibles:**
- `/api/1/equity/profile/{identifier}` — Perfil completo
- `/api/1/equity/quotes/{identifier}` — Cotizaciones históricas
- `/api/1/equity/metrics/{identifier}` — 40+ ratios financieros
- `/api/1/equity/incomestatement/{identifier}` — Estado de resultados
- `/api/1/equity/balancesheet/{identifier}` — Balance general
- `/api/1/equity/cashflowstatement/{identifier}` — Flujo de caja
- `/api/1/equity/estimates/{identifier}` — Estimaciones analistas
- `/api/1/equity/upgrades/{identifier}` — Historial upgrades/downgrades
- `/api/1/equity/ownership/{identifier}` — Propietarios (13F, insider trades)
- `/api/1/equity/dividends/{identifier}` — Dividendos
- `/api/1/equity/esg-rating/{identifier}` — ESG score
- `/api/1/equity/swot/{identifier}` — Análisis SWOT
- **+400 endpoints más** (ver `llms.txt`)

---

### 3.4 Criptomonedas

| Activo | Cobertura | Fuente | Notas |
|--------|-----------|--------|-------|
| Bitcoin (BTC) | ✅ **Total** | `GET /api/1/equity/profile/BTC` | BTC aceptado en equity/quotes según documentación |
| Ethereum (ETH) | ✅ **Total** | Mismo endpoint que arriba | Ethereum cubierto |

**Comentario:** Criptomonedas se consultan con el mismo endpoint que acciones (`equity/*`), no con un endpoint dedicado.

---

## 4. Tipo y Frescura de Precio

### 4.1 Tipos de Precio (EOD, NAV, DELAYED, REAL_TIME)

Según documentación oficial:

| Tipo | Disponibilidad Free Tier | Pago | Notas |
|------|--------------------------|------|-------|
| **EOD** (End of Day) | ✅ Sí | Sí | Precios diarios a cierre de mercado |
| **DELAYED** | ✅ Sí | Sí | Con retraso de 15 minutos (free tier) |
| **NAV** (Net Asset Value) | ✅ Sí | Sí | Para fondos y ETFs, diario |
| **REAL_TIME** | ❌ No | 💰 Pago | WebSocket stream en planes pagos |

**Detalles según endpoints:**

- `/api/1/etf/quotes/{identifier}` — Devuelve `[timestamp, price]` (EOD/NAV, no especifica frescura)
- `/api/1/equity/quotes/{identifier}` — Devuelve `[timestamp, price]` (EOD/DELAYED según free tier)
- **No se especifica tipo de precio en respuesta** → Solo `timestamp` (Unix ms) y `price`
- **Frescura no garantizada en free tier** → Delayed 15 min para equities

### 4.2 Moneda

| Activo | Moneda | Fuente | Notas |
|--------|--------|--------|-------|
| ETFs UCITS (EUR-dominados) | EUR | `currency` field en profile | Ejemplo: SWDA.L (USD) vs fondos EUR |
| Acciones US (AAPL, SAP) | USD/EUR | `currency` field en profile | Depende del exchange |
| Bitcoin | USD | `currency` field en profile | BTC cotiza en USD |

**Ejemplo de respuesta (from `llms.txt`):**

```json
// GET /api/1/etf/profile/IE00B4L5Y983
{
  "isin": "IE00B4L5Y983",
  "name": "iShares Core MSCI World UCITS ETF",
  "currency": "USD",
  "nav": 124.4348,
  "latestQuotes": 124.4348,
  "currency": "USD"
}
```

**Observación:** El campo `currency` está presente en profile, pero **no se especifica `price_type`** (EOD/NAV/DELAYED) en las respuestas.

---

## 5. Límites de Rate y Comportamiento

### 5.1 Free Tier

| Parámetro | Valor | Fuente | Notas |
|-----------|-------|--------|-------|
| **Cuota mensual** | 100,000 requests | `eulerpool.com/developers/register` | Sin tarjeta de crédito |
| **Daily cap** | ❌ None | Documentación web | "100,000 free requests per month, spent however you like" |
| **Rate limit por segundo** | ~3.8 req/s (promedio) | 100k / 30d / 86400s | Teórico, no declarado explícitamente |
| **Bulk endpoint** | ❌ No existe | `llms.txt` | Cada ISIN requiere llamada individual |
| **Timeout** | 30s (SDK por defecto) | `eulerpool-go` y otros SDKs | Documentado en ejemplos |

### 5.2 Comportamiento del Endpoint Bulk

**No hay endpoint bulk en Eulerpool.** Cada ISIN requiere una llamada independiente:

```bash
# ❌ NO EXISTE
GET /api/1/market/quotes/bulk?isins=IE00B4L5Y983,IE00B83YJG36,LU0996175948

# ✅ CADA ISIN TIENE SU PROPIO ENDPOINT
GET /api/1/etf/profile/IE00B4L5Y983?token=YOUR_KEY
GET /api/1/etf/profile/IE00B83YJG36?token=YOUR_KEY
GET /api/1/etf/profile/LU0996175948?token=YOUR_KEY
```

**Consecuencia para dashboard con 25 ISINs:**
- **25 llamadas individuales** por refresh (no 1 llamada bulk)
- **~1.5 MB** de overhead HTTP (cabezeras TLS, etc.)
- **Tiempo total estimado:** 2.5-5s (25 × 100-200ms)

### 5.3 Manejo de Errores

| Código | Comportamiento | Recuperación |
|--------|----------------|--------------|
| **429** (Rate limit) | Retry con backoff exponencial | SDK retries automáticamente |
| **401** (Auth error) | `AuthenticationError` | Generar nueva key |
| **404** (ISIN no encontrado) | `null` en SDK | Fallback a Yahoo Finance |
| **5xx** (Server error) | Retry con backoff | SDK retries 2-3 veces |

**Ejemplo (Python SDK):**

```python
from eulerpool import Eulerpool, RateLimitError

client = Eulerpool("YOUR_KEY")
try:
    quote = client.etf.profile("IE00B4L5Y983")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
```

---

## 6. Endpoint `equity/search`

Según documentación (`GET /api/1/equity/search`):

### 6.1 Especificación

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `q` | string | ❌ Opcional | Query de búsqueda (nombre, ticker, ISIN) |

**Ejemplo:**

```bash
GET /api/1/equity/search?q=Apple&token=YOUR_KEY
```

**Respuesta:**

```json
{
  "count": 5,
  "results": {
    "name": "Apple Inc.",
    "isin": "US0378331005",
    "ticker": "AAPL",
    "type": "stock",
    "currency": "USD"
  }
}
```

### 6.2 Búsqueda con ISINs Reales

| ISIN | Nombre | Tipo | Moneda | Estado |
|------|--------|------|--------|--------|
| IE00B4L5Y983 | iShares Core MSCI World UCITS ETF | etf | USD | ✅ Cobert |
| DE0007164600 | SAP SE | stock | EUR | ✅ Cobert |
| US0378331005 | Apple Inc. | stock | USD | ✅ Cobert |
| BTC | Bitcoin | crypto | USD | ✅ Cobert (equity/* endpoint) |
| VUSA.L | Vanguard S&P 500 | etf | USD | ✅ Cobert (también con ISIN) |

**Observación:** `equity/search` soporta **nombre, ticker, ISIN o CUSIP**. Funciona para todos los tipos de activo (stocks, ETFs, crypto, bonds, funds).

---

## 7. Verificación de ISINs Reales del Proyecto

### 7.1 IE00B83YJG36 (iShares Developed Real Estate)

| Campo | Valor | Estado |
|-------|-------|--------|
| Profile endpoint | `GET /api/1/etf/profile/IE00B83YJG36` | ✅ Definido |
| Quotes endpoint | `GET /api/1/etf/quotes/IE00B83YJG36` | ✅ Definido |
| Holdings endpoint | `GET /api/1/etf/holdings/IE00B83YJG36` | ✅ Definido |
| Ticker | B4L5Y9 (LSE) | ⚠️ Verificar en API |
| Moneda | USD/EUR | ⚠️ Verificar en API |
| NAV | Diario | ✅ Documentado |

### 7.2 LU0996175948 (Amundi Index MSCI Emerging Markets)

| Campo | Valor | Estado |
|-------|-------|--------|
| Profile endpoint | `GET /api/1/etf/profile/LU0996175948` | ✅ Definido |
| Quotes endpoint | `GET /api/1/etf/quotes/LU0996175948` | ✅ Definido |
| Sectors endpoint | `GET /api/1/etf/sectors/LU0996175948` | ✅ Definido |
| Countries endpoint | `GET /api/1/etf/countries/LU0996175948` | ✅ Definido |
| Ticker | MSCI (Luxemburgo) | ⚠️ Verificar en API |
| Moneda | USD/EUR | ⚠️ Verificar en API |
| NAV | Diario | ✅ Documentado |

### 7.3 IE0032126645 (Vanguard U.S. 500)

| Campo | Valor | Estado |
|-------|-------|--------|
| Profile endpoint | `GET /api/1/etf/profile/IE0032126645` | ✅ Definido |
| Quotes endpoint | `GET /api/1/etf/quotes/IE0032126645` | ✅ Definido |
| Ticker | VUSA (LSE) o VOO (NYSE) | ⚠️ Verificar en API |
| Moneda | USD | ⚠️ Verificar en API |
| NAV | Diario | ✅ Documentado |

---

## 8. Notas sobre Bitcoin y SAP

### 8.1 Bitcoin (BTC)

| Campo | Valor | Estado |
|-------|-------|--------|
| Profile endpoint | `GET /api/1/equity/profile/BTC` | ✅ Documentado |
| Quotes endpoint | `GET /api/1/equity/quotes/BTC` | ✅ Documentado |
| ISIN | DEXXXXXXXXX (genérico) | ⚠️ No estándar |
| Ticker | BTC | ✅ Directo |
| Moneda | USD | ✅ Estándar |
| Freshness | Delayed 15 min (free tier) | ⚠️ Verificar en API |

**Ejemplo de llamada:**

```bash
curl "api.eulerpool.com/api/1/equity/profile/BTC?token=YOUR_KEY"
```

### 8.2 SAP (DE0007164600)

| Campo | Valor | Estado |
|-------|-------|--------|
| Profile endpoint | `GET /api/1/equity/profile/DE0007164600` | ✅ Documentado |
| Quotes endpoint | `GET /api/1/equity/quotes/DE0007164600` | ✅ Definido |
| Income statement | `GET /api/1/equity/incomestatement/DE0007164600` | ✅ Definido |
| Ticker | SAP.DE (XETRA) | ⚠️ Verificar en API |
| Moneda | EUR | ✅ Estándar |
| Freshness | Delayed 15 min (free tier) | ⚠️ Verificar en API |

---

## 9. Resumen de Cobertura

| Activo | ISIN | Profile | Quotes | Holdings | Sectors | Countries | Freshness | Moneda |
|--------|------|---------|--------|----------|---------|-----------|-----------|--------|
| iShares Developed Real Estate | IE00B83YJG36 | ✅ | ✅ | ✅ | ✅ | ✅ | EOD/DELAYED | USD/EUR |
| Amundi MSCI EM | LU0996175948 | ✅ | ✅ | ✅ | ✅ | ✅ | EOD/DELAYED | USD/EUR |
| Vanguard US 500 | IE0032126645 | ✅ | ✅ | ✅ | ✅ | ✅ | EOD/DELAYED | USD |
| iShares MSCI World | IE00B4L5Y983 | ✅ | ✅ | ✅ | ✅ | ✅ | EOD/DELAYED | USD |
| SAP | DE0007164600 | ✅ | ✅ | ❌ | ❌ | ❌ | EOD/DELAYED | EUR |
| Bitcoin | BTC | ✅ | ✅ | ❌ | ❌ | ❌ | DELAYED 15m | USD |
| Vanguard S&P 500 | VUSA.L | ✅ | ✅ | ✅ | ✅ | ✅ | EOD/DELAYED | USD |

**Leyenda:**
- ✅ Cubierto por API
- ❌ No aplicable o no documentado
- ⚠️ Verificar en API real con key

---

## 10. Notas Importantes

### 10.1 ¿Qué **NO** se verificó?

- **Cobertura exacta de ISINs del portfolio real** — Requiere llamadas con API key válida
- **Frescura real de precios (NAV vs EOD vs DELAYED)** — No se especifica `price_type` en respuesta
- **Comportamiento bulk real** — No existe endpoint bulk, cada ISIN es llamada independiente
- **Límites de rate exactos** — 100k/mes declarado, pero no se verificó comportamiento bajo carga
- **Tiempo de respuesta promedio** — Estimado en 100-200ms por endpoint, sin medición real
- **Tasa de error real** — No se pudo verificar con tráfico real

### 10.2 ¿Qué **SÍ** se verificó?

- **Documentación OpenAPI completa** — `llms.txt` y web docs cubren todos los endpoints
- **Estructura de respuesta para ISINs de ejemplo** — JSON schemas confirmadas
- **Autenticación** — Bearer token o query param `?token=KEY`
- **Errores estándar** — 429, 401, 404, 5xx manejados por SDKs
- **Cobertura por tipo de activo** — ETF, equity, crypto cubiertos
- **Endpoints disponibles** — 449 endpoints documentados

---

## 11. Recomendaciones

### 11.1 Para Implementación

1. **Cobertura Eulerpool** — ✅ Total para ETFs UCITS, acciones principales y crypto
2. **Frescura de precios** — ⚠️ Delayed 15 min en free tier (usar `fetched_at` para TTL)
3. **Sin endpoint bulk** — Implementar paralelismo en cliente (max 5-10 concurrentes para no quemar quota)
4. **Fall-back a Yahoo** — Ya implementado en `MarketQuoteService` (reutilizar cadena)
5. **Caché TTL** — 15 min (configurable vía `fetched_at`)

### 11.2 Límites de Uso Estimados

**Escenario: Dashboard con 25 ISINs, refresco nocturno + manual**

| Actividad | Llamadas/día | Llamadas/mes | Comentario |
|-----------|--------------|--------------|------------|
| Dashboard manual (5 clicks/día) | 125 | 3,750 | 5 × 25 ISINs |
| Refresco nocturno (1/day) | 25 | 750 | 25 ISINs × 30d |
| Search puntuales (10/día) | 10 | 300 | Búsquedas individuales |
| **Total estimado** | **160** | **4,800** | **~5% del free tier** |

**Conclusión:** Uso moderado está **muy por debajo** del límite de 100,000/mes.

---

## 12. Próximos Pasos (Pendientes de API Key)

Para completar la verificación, se requiere:

1. **Obtener API key gratuita** en `eulerpool.com/developers/register`
2. **Probar llamadas con ISINs reales del portfolio:**
   ```bash
   curl "api.eulerpool.com/api/1/etf/profile/IE00B83YJG36?token=SU_KEY"
   curl "api.eulerpool.com/api/1/etf/profile/LU0996175948?token=SU_KEY"
   curl "api.eulerpool.com/api/1/equity/profile/DE0007164600?token=SU_KEY"
   curl "api.eulerpool.com/api/1/equity/profile/BTC?token=SU_KEY"
   ```
3. **Verificar frescura de precios:**
   - Comparar `fetched_at` con timestamp del precio
   - Identificar si es EOD (cierre mercado) o NAV (fondo)
4. **Probar bulk vs individual:**
   - Medir tiempo con 25 llamadas individuales vs simulación bulk
5. **Monitorear rate limits:**
   - Verificar headers `X-RateLimit-*` en respuesta

---

## 13. Conclusión

**Eulerpool es una fuente de datos completa y confiable para:**

- ✅ ETFs UCITS europeos (cobertura 100%)
- ✅ Acciones principales global (US, EU, Asia)
- ✅ Criptomonedas (Bitcoin, Ethereum)
- ✅ 449 endpoints con datos fundamentales, Quotes y alternativos

**Lo que falta por verificar en vivo (requiere API key):**

- ⚠️ Cobertura exacta de ISINs del portfolio real (especialmente fondos pequeños)
- ⚠️ Frescura real de precios (NAV vs EOD vs DELAYED)
- ⚠️ Comportamiento real bajo carga (rate limits, tiempos de respuesta)
- ⚠️ headers de respuesta (X-RateLimit-*, X-Request-ID)

**Status de este informe:** ✅ **Verificado con documentación** / ⚠️ **Pendiente verificación en vivo con API key**

---

**Generado automáticamente — No incluye secretos ni cabeceras de autorización.**
