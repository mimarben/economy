Informe de Arquitectura — Fase 1 (Auditoría, solo lectura)
Método: inspección directa de código, esquema, migraciones, tests y configuración + documentación pública de Eulerpool (llms.txt oficial). No se ha modificado ningún fichero. Al final indico qué verificaciones en vivo quedaron bloqueadas por el modo de permisos de esta sesión.

Leyenda: ✅ Hecho verificado · ⚠️ Suposición · ❓ Ambigüedad

4.1 Estado actual
4.1.1 Base de datos y modelos (verificado)
Fuente de verdad declarada por CLAUDE.md: er.sql. Conflicto detectado: ese fichero está desincronizado con los modelos y migraciones reales (ver 4.2, P6).

Tablas del dominio de inversión (modelos SQLAlchemy en api/models/investments/):

Tabla	Campos clave	Observaciones
investments	description, date, currency(enum), amount numeric(12,2) NOT NULL, dedup_hash, isin(12) nullable, account_id FK, category_id FK, deleted_at	investment_model.py:14-23. isin añadido por migración b7c4d9e2f8a1 (2026-11-18). Dedup único (account_id, dedup_hash).
investments_logs	date, current_value nullable, price_per_unit, quantity numeric(12,6), action(actionenum), note, investment_id FK, deleted_at	investment_log_model.py:10-19. quantity renombrado desde units_bought y current_value hecho nullable por a1b2c3d4e5f6. Sin moneda, comisiones, impuestos, referencia externa ni origen de importación.
investments_categories	name unique, description, active	investment_category_model.py — catálogo plano, sin colores ni tipo de activo.
market_quotes	isin UNIQUE, symbol, name, instrument_type, currency, last_price, previous_close, source, fetched_at	market_quote_model.py:14-28. Caché de una fila por ISIN (upsert la sobrescribe, market_quote_repository.py:27-42). No es histórico de cotizaciones; no guarda timestamp de la cotización ni tipo de precio (EOD/NAV/delayed).
Enums (enums.py:4-42):

ActionEnum: buy, sell, transfer, deposit, withdraw, hold — faltan DIVIDEND, INTEREST, FEE, SPLIT, ADJUSTMENT.
CurrencyEnum: EUR, USD, JPY + 12 criptos. ✅ Bug latente verificado: de DOGE a TRX los valores llevan coma final (DOGE = "DOGE",) → son tuplas, no str; romperían comparaciones/serialización de esas monedas.
TransactionEnum (categorización): expense, income, investment — el tipo investment dirige reglas a InvestmentsCategory (categorization_service.py:55-57).
4.1.2 Semántica real de amount e InvestmentLog (la pregunta clave de 1.7)
✅ Verificado en código (no asumido por el nombre):

Investment.amount = capital aportado (contribución) en esa fecha, siempre > 0 (gt=0, investment_schema.py:19). Se suma como total_contributed en el dashboard (investment_repository.py:48-65) y como total de inversión en summaries. No es cantidad de participaciones ni valor de mercado. No existe representación de venta (no hay importes negativos ni contrapartida).
InvestmentLog = snapshot de posición, no libro mayor de transacciones. El repositorio toma el último log de cada investment como posición vigente: “logs are position snapshots, so the latest row holds the current quantity/value” (investment_repository.py:10-24). Es decir: quantity del último log = unidades actuales; current_value = última valoración manual (reported_value, fallback si no hay cotización); price_per_unit no se consume en ningún cálculo. El campo action existe pero ninguna agregación lo usa.
4.1.3 Servicios, repositorios y endpoints (verificado)
Arquitectura respetada: Router → Service → Repository. Todo detrás de JWT (routers/init.py:33-68).

CRUD estándar: /investments, /investment_logs, /investment_categories (BaseService, soft-delete vía deleted_at, base_repository.py:74-85).
GET /market/quotes?isins=&refresh= y GET /investments/dashboard (market_quote_router.py:33-64).
Ya existe la abstracción de proveedor que pide el documento: MarketDataProvider (ABC) + ProviderQuote (market_provider.py) con implementación YahooMarketProvider (yahoo_market_provider.py). MarketQuoteService encadena proveedores por orden, con degradación a caché stale y estados ok|stale|unavailable (market_quote_service.py:36-95).
Valoración del dashboard: market_value = units × last_price; unrealized_pl = market_value − total_contributed (market_quote_service.py:117-168). Unidades desconocidas = None (no 0) cuando nunca se registró log — buena decisión ya tomada.
TTL de caché 15 min, timeout 10 s (config.py:41-42). Script nocturno de refresco ya existe: refresh_market_quotes.py (preparado para cron 06:30 Europe/Madrid).
Yahoo: resuelve ISIN→símbolo vía search, precio vía chart; soporta ETF/MUTUALFUND/EQUITY; manejo de 429 con mirror query1/query2 y throttle 0,5 s. ✅ Código muerto verificado: _resolve_symbol duplicado (yahoo_market_provider.py:99-109 y 115-125).
4.1.4 Importación y reconciliación (verificado)
El import solo persiste gastos e ingresos (BulkImportRequest{expenses, incomes}; import_service.py:59-249). Nunca crea investments, aunque el sistema de reglas sí conoce el tipo investment. Consecuencia: la compra de acciones en el banco entra como expense del extracto y, si además se registra la inversión a mano, el mismo dinero vive en dos sitios sin enlace → riesgo de doble contabilización y sin trazabilidad.
4.1.5 Frontend Angular 21 (verificado)
Rutas lazy: /investments, /investments_categories, /investments_log, /investments_dashboard (app.routes.ts:32-35).
Dashboard (investments-dashboard.component.ts, signals ✅): 6 KPIs + tabla con columnas nombre, tipo, unidades, aportado, último precio, var. día, valor mercado, P/L no realizado, estado. Botón refresh (force). Fallback a reported_value con *. Aviso de unidades parciales.
No existe: búsqueda, filtro por categoría, ordenación, paginador, colores por categoría, vista de cerradas/histórico, detalle de instrumento. El símbolo € está fijado en KPIs/sumas aunque la entrada tenga otra moneda (investments-dashboard.component.html:35,126).
CRUD de investments/logs: formularios genéricos dirigidos por metadata (/meta/investment* + formFactory); el campo ISIN entra por el meta schema. Sin validación financiera (ej. vender más de lo poseído no se comprueba ni en UI ni backend).
Home muestra investmentTotal = suma de aportaciones (no valor de mercado) (home.component.ts:54-55).
4.1.6 Tests (verificado)
13 módulos, 103 funciones de test (más casos parametrizados; memoria de proyecto: 108 pytest OK el 19-11). Cobertura de inversiones: validación/persistencia ISIN y dedup (test_investment_isin.py), caché TTL/refresh/proveedores fallback/dashboard agrupado/exclusión de soft-deletes/posiciones/P&L/parciales/never-logged/reported_value (test_market_quote_service.py), resiliencia 429 de Yahoo (test_market_providers.py), wiring de rutas (test_market_router_wiring.py). Sin cobertura: ventas, posiciones cerradas, P/L realizado, conversión de moneda, composiciones, Eulerpool, reconciliación import-inversión.

4.1.7 Migraciones Alembic (verificado)
Cadena íntegra, head = b7c4d9e2f8a1. Relevantes: a1b2c3d4e5f6 (rename units_bought→quantity, current_value nullable — ojo: su docstring dice "Revises: f9c1c8a9bb59" pero el down_revision real es a80dc79a6368) y b7c4d9e2f8a1 (ISIN + market_quotes). Dev usa create_all; producción SCHEMA_INIT_STRATEGY=migrations (database.py:99-115).

4.1.8 Configuración y recursos disponibles (verificado)
.env contiene EULERPOOL_API_URL y EULERPOOL_API_KEY (nombres verificados; el valor de la clave no se ha leído ni reproducido). config.py aún no los lee y no hay ni una referencia a Eulerpool en el código — la integración está sin empezar.
Skills/agentes útiles detectados: angular, material (UI), dataviz (gráficas), conector MyInvestor MCP (catálogo declarado: 13 carteras gestionadas —6 MyInvestor + 7 Finanbest— cuyo payload incluye composición y fondos subyacentes con ISIN; el probe en vivo quedó bloqueado por permisos, capacidad tomada de su documentación).
4.2 Problemas identificados (priorizados)
P1 — Integridad de datos

Sin aislamiento por usuario en inversiones: get_grouped_by_isin y compañía no filtran por usuario/cuenta del token — el dashboard agrega las inversiones de todos los usuarios (investment_repository.py:54-65). Con roles admin/user ya desplegados, es una fuga de datos entre usuarios.
DELETE roto en 7 routers: typo esponse.ok_message → NameError tras borrar → el endpoint devuelve 500 después de haber borrado. Afecta a investment_router.py:82, investment_log_router.py:78, investment_category_router.py:78 (+ households, saving_logs, income_categories).
Historial vendido irre recuperable en la práctica: el soft-delete oculta la fila en todas las vistas (ninguna consulta lee deleted_at IS NOT NULL como histórico); no existe ciclo ACTIVE→CLOSED ni P/L realizado.
P2 — Corrección financiera

P/L no realizado erróneo tras ventas: unrealized_pl = market_value − Σaportaciones con amount siempre > 0 y sin contrapartida de venta. Si vendes la mitad, las aportaciones siguen sumando el 100 % del coste → el P/L se hunde artificialmente. No hay P/L realizado ni método de coste (FIFO/medio).
Mezcla de monedas sin conversión: total_contributed, total_market_value y unrealized_pl suman importes en monedas distintas sin FX (market_quote_service.py:114-168); el market_value hereda la moneda de la cotización y el coste la de la aportación.
CurrencyEnum con valores-tupla (criptos) — latente pero real.
P3 — Diseño de base de datos

Investment mezcla instrumento + posición + aportación; ISIN como string suelto; sin catálogo de instrumentos, sin multi-identificador (ticker/símbolo/proveedor), sin composición (carteras gestionadas), sin cuenta/bróker explícito más allá de account_id.
market_quotes sin timestamp de cotización ni tipo de precio → no se puede distinguir EOD/NAV/delayed ni garantizar frescura real (solo fetched_at).
Falta source_id/origen en investments (gastos e ingresos sí lo tienen) → imposible trazabilidad de importación.
P4 — Integración

Proveedor único (Yahoo) sin clave, sujeto a 429; Eulerpool configurado en .env pero sin usar. Búsqueda de instrumentos inexistente (no hay endpoint de search).
P5 — Frontend

Dashboard sin búsqueda/filtros/ordenación; sin colores por categoría; € hardcodeado; sin vistas de cerradas/histórico/detalle; sin composición.
P6 — Documentación/mantenibilidad

er.sql desincronizado (le faltan isin, market_quotes, el rename quantity y la nullabilidad de current_value) — incumple la regla 1 de CLAUDE.md. api/er.sql y .claude/database/E-R fueron borrados/movidos (git status). Código muerto en el provider Yahoo.
4.3 Arquitectura propuesta
Principio rector (regla dorada del proyecto): no reescribir, extender. Las tablas y flujos existentes siguen funcionando; las nuevas entidades son aditivas y migrables sin pérdida.

Decisiones estructurales clave (detalladas en 4.8): investments se mantiene como libro de aportaciones (ya tiene fecha, importe, moneda, cuenta y dedup — es el histórico de compras); investments_logs evoluciona a libro mayor canónico de transacciones manteniendo compatibilidad snapshot; la posición se deriva (cantidad actual, estado ACTIVE/CLOSED) en capa de servicio, no se almacena como tabla nueva.


erDiagram
    ACCOUNTS ||--o{ INVESTMENTS : "aportaciones por cuenta"
    INVESTMENTS_CATEGORIES ||--o{ INSTRUMENTS : "categoría configurable"
    INSTRUMENTS ||--o{ INSTRUMENT_IDENTIFIERS : "0..N identificadores"
    INSTRUMENTS ||--o{ INSTRUMENT_COMPOSITIONS : "padre"
    INSTRUMENTS ||--o{ INSTRUMENT_COMPOSITIONS : "componente"
    INSTRUMENTS ||--o{ INVESTMENTS : "instrument_id (nullable, legacy)"
    INVESTMENTS ||--o{ INVESTMENTS_LOGS : "transacciones/snapshots"
    INSTRUMENTS ||--o{ MARKET_QUOTES : "caché 1:1 por identificador primario"
    INSTRUMENTS ||--o{ MARKET_QUOTE_HISTORY : "serie append-only"

    INSTRUMENTS {
        int id PK
        string name
        enum asset_class "ETF|FUND|STOCK|CRYPTO|BOND|MANAGED_PORTFOLIO|OTHER"
        int category_id FK "reutiliza investments_categories"
        string currency
        bool is_active
    }
    INSTRUMENT_IDENTIFIERS {
        int id PK
        int instrument_id FK
        enum identifier_type "ISIN|TICKER|SYMBOL|PROVIDER|INTERNAL"
        string value
        string exchange "nullable"
        string provider "nullable (myinvestor, finanbest...)"
        bool is_primary
    }
    INSTRUMENT_COMPOSITIONS {
        int id PK
        int parent_instrument_id FK
        int component_instrument_id FK
        numeric weight
        date valid_from
        string source
    }
    INVESTMENTS {
        int id PK
        numeric amount "aportado (>0)"
        string isin "legacy, dual-write transición"
        int instrument_id FK "nullable"
        int account_id FK
    }
    INVESTMENTS_LOGS {
        int id PK
        enum action "buy|sell|deposit|withdraw|dividend|interest|fee|split|adjustment|hold|transfer"
        numeric quantity
        numeric price_per_unit
        numeric fees "nuevo"
        string external_ref "nuevo"
    }
    MARKET_QUOTES {
        string isin UK "caché actual"
        datetime quoted_at "nuevo"
        enum price_type "EOD|DELAYED|REAL_TIME|NAV"
    }
    MARKET_QUOTE_HISTORY {
        int instrument_id FK
        numeric close
        string currency
        enum price_type
        date quoted_at
        string source
    }
Responsabilidades e invariantes financieros:

Instrumento ≠ posición ≠ transacción ≠ cotización (reglas 1-3 innegociables, ya alineadas).
ISIN jamás obligatorio ni PK: vive en instrument_identifiers con unicidad por namespace UNIQUE(identifier_type, value, COALESCE(exchange,''), COALESCE(provider,'')). Un MANAGED_PORTFOLIO puede tener 0 identificadores o solo PROVIDER:myinvestor:XXXX.
Composición = solo análisis de exposición (weight, valid_from, source seeded desde Eulerpool ETF/mutual-fund holdings o del conector MyInvestor para carteras Red/Finanbest). Jamás suma valor: el valor de una cartera gestionada sale de su posición × cotización/NAV propio, o se muestra “valoración no disponible” (regla 8 del §1.3.1).
Cantidad actual = para legacy, último snapshot (compatibilidad total con datos existentes); para transacciones nuevas, derivada con semántica por tipo: BUY/DEPOSIT suman, SELL/WITHDRAW restan, DIVIDEND/INTEREST/FEE no tocan cantidad (efecto en caja/coste), SPLIT multiplica. Estado CLOSED cuando cantidad ≤ 0; reapertura automática con nueva BUY.
Inmutabilidad: investments.amount y price_per_unit históricos jamás se sobrescriben con datos de mercado; market_quotes/historia son entidades separadas.
Moneda: valoración explícita en EUR con fx_rates (fuente ECB vía Eulerpool); sin tasa → campo None + estado, nunca precio inventado.
P/L: no realizado = valor mercado − coste base (FIFO propuesto); realizado = Σventas − coste FIFO de lo vendido. Los totales solo suman entradas con moneda resuelta.
4.4 Estrategia de migración de BD
Tablas nuevas: instruments, instrument_identifiers, instrument_compositions, fx_rates, market_quote_history. (Pospuesto: portfolio_valuations.)

Tablas modificadas (todo aditivo y nullable):

investments + instrument_id FK nullable (columna isin se conserva y se rellena en dual-write durante la transición; el dashboard sigue agrupando por ISIN si no hay instrumento).
investments_logs + fees numeric, external_ref varchar, ampliación de actionenum (nuevos valores: dividend, interest, fee, split, adjustment).
market_quotes + quoted_at, price_type (nullable).
Preservación de datos: migración de datos idempotente que crea un instrument por cada ISIN distinto de investments (name/currency desde market_quotes si existe), le asigna su identifier ISIN primario y enlaza investments.instrument_id. Las aportaciones sin ISIN quedan con instrument_id NULL hasta clasificación manual (se cuentan en el KPI actual). Ninguna fila existente se transforma ni borra.

Compatibilidad API: /investments/dashboard extiende cada entrada con instrument_id, asset_class, category, status, realized_pl, currency fields (campos additivos; los existentes no cambian de nombre ni tipo). Los schemas CRUD ganan instrument_id opcional.

Rollback: cada migración nueva con downgrade() que solo elimina columnas/objetos creados por ella; las migraciones históricas quedan intactas.

Registros legacy que requieren decisión manual (❓): (a) aportaciones sin ISIN que en realidad son carteras gestionadas; (b) logs antiguos donde current_value podría ser coste y no valoración; (c) si el usuario recuerda cantidades/precios de compras históricas para retroalimentar el libro de transacciones (opcional, mejora el P/L histórico).

4.5 Diseño de integración con Eulerpool
Verificado en la documentación oficial del proveedor (llms.txt / developers index; sin usar la clave):

Base https://api.eulerpool.com, rutas /api/1/...; auth Authorization: Bearer (nunca en logs); OpenAPI en /api/1/documentation/yaml; free tier 100.000 llamadas/mes.
Búsqueda universal: equity/search y screener/search — “stocks, ETFs, crypto, bonds, and mutual funds by name, ticker, or ISIN”. Cubre el requisito de buscar IE00B4L5Y983, Bitcoin, SAP, Vanguard S&P 500.
Cotizaciones: market/quotes/latest (varios tickers), market/quotes/bulk (≤50 ISINs por petición — el dashboard completo en 1 llamada), equity/quotes (ISIN o símbolo cripto + timeframe → histórico), etf/quotes, crypto/quotes, datasets/eod (OHLCV EOD), market/status y market/holidays (para no pedir fuera de horario).
Fondos/ETFs: mutual/fund/profile|holdings|sectors|countries, funds/nport (posiciones trimestrales completas con peso → fuente de instrument_compositions), etf/holdings|sectors|countries, etf/list.
FX: ecb/exchange/rates (tipos de referencia EUR del BCE) → alimentará fx_rates.
Cripto: crypto/list|profile|quotes (+ BTC aceptado en equity/quotes).
⚠️ Pendiente de verificación con la clave (paso 0 de Fase 2): frescura/tipo real de precio para fondos UCITS europeos (NAV diario vs delayed), límites por minuto, y cobertura exacta de los ISINs reales del portfolio (el probe en vivo quedó bloqueado en esta sesión; el plan es ejecutarlo antes de escribir el cliente). No asumimos que un ISIN válido implique cobertura.

Diseño:

EulerpoolMarketProvider(MarketDataProvider) + EulerpoolSearchProvider implementando la abstracción existente — cero cambios en el modelo de dominio (regla del documento). Normalización de respuesta → ProviderQuote/InstrumentSearchResult; los modelos SQLAlchemy nunca ven el JSON crudo de Eulerpool.
Config lee EULERPOOL_API_URL/KEY (la clave solo en memoria; logs sin secretos, como ya hace _mask_url_password en database.py:37-45).
Orden de proveedores configurable: Eulerpool primario, Yahoo de fallback durante la transición (el código ya soporta la cadena y el test test_second_provider_used_when_first_fails existe).
Caché: la actual market_quotes (TTL 15 min) + historia append-only. Consumo estimado (⚠️ ~10-25 ISINs en cartera, suposición — no pude consultar la BD): refresco de dashboard 1 llamada bulk/TTL; nocturno 1-2; búsquedas puntuales → < 5.000/mes, muy por debajo del free tier. Con cripto a 5 min serían ~8.600/mes si se quisiera 24/7 (recomendado limitar a horario activo).
Errores/rate limits: contrato existente “nunca raise → None” + degradación a stale + logging warning sin secretos. UI muestra quote_status, price_type, quoted_at y moneda (nunca fingir tiempo real).
4.6 Propuesta de dashboard
Evolutionar /investments_dashboard (ruta y API intactas) a cuatro vistas:

Overview — KPIs actuales (corregidos a EUR con conversión explícita y estados “sin cotización”) + gráfico de asignación por categoría con paleta consistente (tokens CSS/Tailwind definidos una vez: ETF, Fondo, Acción, Cripto, Bono, Cartera gestionada, Otro — mismos colores en tabla, filtros, badges y gráficos).
Posiciones — tabla actual ampliada: badge de categoría coloreado, ISIN o ticker, cantidad, precio, moneda, valor mercado, coste, P/L (no realizado + %), última cotización (hora + tipo + frescura), estado ACTIVE|CLOSED. Con búsqueda por texto (nombre/ISIN/ticker), filtro por categoría y estado, y ordenación (MatSort + paginator; hoy no existen).
Búsqueda universal — barra que consulta el nuevo endpoint backend /market/search (Eulerpool): resultados con nombre, categoría, ISIN, ticker, bolsa, moneda, proveedor; desambiguación obligatoria cuando hay varios candidatos (jamás auto-asignar a una posición). Flujo: buscar → seleccionar instrumento → crear/actualizar aportación o enlazar existente.
Detalle de instrumento — identificadores, cotización e histórico, transacciones del usuario, y para MANAGED_PORTFOLIO/fondos la composición subyacente con aviso explícito “exposición analítica, no suma patrimonio”.
Histórico — posiciones CLOSED (conservando compras, ventas, comisiones y P/L realizado), accesible pero fuera de la vista por defecto.
Separación overview/posiciones/detalle/histórico como pide el documento; nada de esto rompe contratos (extensiones additivas del DashboardResponse).

4.7 Roadmap de implementación (incrementos independientes y testeables)
#	Incremento	Contenido	Depende de
0	Fixes previos	Typo esponse (7 routers, con test), re-sincronizar er.sql con modelos, decidir scoping multi-user, CurrencyEnum tuplas	—
1	Esquema	Migración aditiva: instruments, instrument_identifiers, instrument_compositions, fx_rates, market_quote_history + columnas nuevas + seed desde ISINs existentes	0
2	Backend dominio	InstrumentService/Repository (CRUD + búsqueda local + enlazado aportaciones), endpoints nuevos /instruments, /market/search (proxy Eulerpool)	1
3	Eulerpool	Probe en vivo → EulerpoolMarketProvider + search + bulk + FX; config; tests (errores, rate limits, sin secretos en logs)	1
4	Valoración correcta	FX explícito, P/L con FIFO, cantidad derivada por semántica de acción, ACTIVE/CLOSED, P/L realizado; extender respuesta dashboard	1, 3
5	Frontend	Búsqueda universal, colores/filtros/orden, estado y cerradas, detalle con composición	2, 4
6	Import compat	source_id/origen en investments, external_ref en logs (trazabilidad futura; sin matching automático)	1
7	Histórico	Serie de cotizaciones/valoraciones para gráficos de evolución	3, 4
Riesgos: cobertura Eulerpool de fondos EU (mitigación: Yahoo fallback ya encadenado); semántica snapshot→evento en datos legacy (mitigación: lectura dual legacy/nueva); scoping multi-user puede cambiar lo que ve cada usuario (aprobar antes).

4.8 Decisiones que requieren tu aprobación
#	Decisión	Recomendación	Alternativa	Consecuencia de la recomendación
D1	¿Posición como tabla propia?	No: derivarla de transacciones/snapshots en servicio	Tabla positions materializada	Menos riesgo de sincronización; el coste es recomputar (trivial a este volumen)
D2	Semántica de investments_logs	Híbrido: legacy = snapshot (último log), nuevas = eventos por tipo de acción	Migrar todo a eventos	Cero migración de datos antigua; P/L histórico de legacy queda limitado
D3	Proveedor primario	Eulerpool primario + Yahoo fallback	Mantener Yahoo primario	Usa la clave ya contratada y el bulk; riesgo cubierto por la cadena existente
D4	Categorías de instrumento	Reutilizar investments_categories (seed ETF/FUND/STOCK/CRYPTO/BOND/MANAGED_PORTFOLIO/OTHER) + asset_class estricto para lógica	Enum hardcodeada	Configurable por ti sin despliegue; la lógica usa el enum estable
D5	Moneda base	EUR con fx_rates BCE	Sin conversión	Totales correctos; añade una entidad y dependencia de una fuente FX
D6	Método de coste	FIFO	Coste medio	Estándar y trazable; coincide con lo habitual en informes fiscales ES
D7	Borrado de inversiones	DELETE solo admin y solo sin historial financiero; lo normal es vender → CLOSED	Mantener DELETE para todos	Preserva histórico por diseño
D8	Scoping multi-user	Filtrar dashboard/investments por cuentas del usuario (salvo admin)	Global como ahora	Cambia resultados por usuario (no el contrato); corregiría la fuga P1-1
D9	Histórico de valoraciones	Posponer portfolio_valuations a post-diciembre; sí guardar quoted_at/historia de quotes	Todo ahora	Encaja en el plazo de diciembre
D10	Reconciliación bancaria (dic.)	Solo trazabilidad (source_id, external_ref)	Matching automático	Mínimo riesgo para el import actual; el matching automático queda para 2027
4.9 Recomendación final
Implementar ya (ordenado por valor/riesgo): fixes P2 (typo DELETE), re-sincronización de er.sql, esquema aditivo de instrumentos/identificadores/composiciones, Eulerpool sobre la abstracción existente, valoración con FX + FIFO + ACTIVE/CLOSED, y el dashboard con búsqueda/colores/estados. La base actual es mejor de lo que sugiere el documento: la abstracción de proveedor, el caché con estados, el script nocturno, el dedup y los 103 tests ya existen y se reutilizan tal cual.

Simplificar: la posición como tabla (derivarla), y la búsqueda universal (un solo endpoint proxy en backend, nada de llamadas desde Angular).

No implementar todavía: matching automático banco↔inversión, portfolio_valuations para gráficos de patrimonio histórico, y cualquier migración destructiva de investments_logs a eventos puros.

Posponer a post-diciembre 2026: valoraciones históricas diarias completas, atribución de riesgo, y expansión a otros proveedores más allá del fallback Yahoo.

Verificaciones bloqueadas por el modo de permisos de esta sesión
No pudieron ejecutarse en vivo (todas sustituidas por lectura directa o por documentación oficial, y quedan como paso 0 de Fase 2): spawn de agentes, curl/WebFetch/WebSearch, probe autenticado de Eulerpool, consulta al catálogo MyInvestor y acceso a la BD para contar ISINs distintos. Si quieres que haga esos probes antes de aprobar, cambia el modo de permisos y lo ejecuto sin tocar ningún fichero.

STOP — Fin de la Fase 1. No se ha modificado nada. Espero tu aprobación explícita (y las decisiones D1–D10) antes de comenzar la Fase 2.
