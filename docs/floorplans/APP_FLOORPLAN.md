# Economy — Plano de la aplicación (floorplan)

- **Fecha:** 2026-11-13
- **Fuente:** verificación estática del código durante la auditoría (`docs/audits/UX_PRODUCTIVITY_IMPORT_AUDIT.md`). Todas las salas y conexiones están confirmadas por código salvo las marcas ⚠ (hallazgos de la auditoría).
- **Lectura:** el edificio se lee de arriba (entrada) hacia abajo (datos). Cada "planta" es una capa de la arquitectura real.

```
                        ┌─────────────────────────────┐
                        │   NGINX (80/443, TLS)       │  Entrance / lobby
                        │   economy.app.local         │  proxies /api → backend
                        └──────┬──────────────┬───────┘
                    :4200      │              │ :5001
        ┌──────────────────────┘              └──────────────────────┐
        ▼                                                            ▼
╔═════════════════════════════════════════╗      ╔════════════════════════════════════════╗
║ FLOOR 1 — CLIENT (Angular 21 + Material)║      ║ FLOOR 1–4 — BACKEND (FastAPI, :5001)   ║
║                                          ═╪════▶║ all routers behind require_access_token ║
║  ┌─ Auth wing ─────────┐  ┌─ Master wing ─┐    ╚════════════════════════════════════════╝
║  │ /login  /register   │  │ /users banks  │     FLOOR 2 — ROUTERS (/api)
║  └─────────────────────┘  │ cards accounts│     ┌────────────┬────────────┬─────────────┐
║                           │ sources       │     │ auth       │ users      │ households  │
║  ┌─ Money wing ─────────┐ │ households    │     │ expenses   │ incomes    │ investments │
║  │ /expenses  /incomes  │ └───────────────┘     │ savings    │ cards      │ category_   │
║  │ /savings(+_log)      │                        │            │            │ rules       │
║  │ /investments(+_log)  │  ┌─ Rules wing ───┐    │ summaries  │ finance    │ source_rules│
║  │ + categories ×3      │  │ /category_rules│    │ imports ◀──┼── THE import door
║  └─────────────────────┘  │ /source_rules   │    │ import-origins / import-profiles    │
║                           └─────────────────┘    │ ai (idle endpoint)                  │
║  ┌─ Analysis wing ──────┐                        └─────┬──────────────────────────────┘
║  │ /financial_summary   │                        FLOOR 3 — SERVICES
║  │ /charts (chart.js)   │                        ┌─────────────────────────────────────┐
║  └─────────────────────┘  ┌─ Import wing ──┐     │ ImportService (atomic bulk)         │
║                           │ /excel_import ◀─╗    │  ├─ CategorizationService (rules→AI)│
║  ╔══ LOCKED ROOMS (dead code, no doors) ══╗║    │  ├─ dedup_service (sha256 hash)     │
║  ║ import-preview/  column-mapper/        ║║    │  └─ (AI never wired in) ⚠          │
║  ║ bank-format.service import-transform   ║║    │ Expense/Income/Investment services  │
║  ╚═════════════════════════════════════════╝    │ SummaryService · AuthService(+JWT)   │
║   In-browser engine room: SheetJS parser,       └─────┬──────────────────────────────┘
║   rule-categorizer, 8 catalog loads on entry         FLOOR 4 — REPOSITORIES
└──────────────────────────────────────────────┐  ┌─────────────────────────────────────┐
                                                │  │ Expense/Income/Investment/… repos   │
                                                │  │ BaseRepository (soft-delete, flush) │
                                                │  └─────┬──────────────────────────────┘
┌──────────────────────────────────────────────┴────────▼───────────────────────────────┐
║ BASEMENT — PostgreSQL 18 (bind mount ./database/postgres, real data)                   │
║  22 tables: expenses* incomes* investments(+logs) savings(+logs) category_rules        │
║  source_rules  accounts  banks  cards  sources  users  households(+members)            │
║  import_origins  import_profiles  account_users  places  alembic_version               │
║  * UNIQUE (account_id, dedup_hash)   ⚠ no transfers, no import_batches, no date index  │
└────────────────────────────────────────────────────────────────────────────────────────┘
   ANNEX (docker container, running but unplumbed): llama.cpp qwen2.5-7b @ ai:8180
```

## Qué revela el plano

- **Una única puerta principal** (`/api` vía nginx) y todos los routers de negocio tras JWT (`api/routers/__init__.py:60-66`).
- **El ala de importación es la sala más transitada**: 8 cargas de catálogo al entrar, parseo SheetJS en navegador, y un único POST a `/imports/transactions/bulk`.
- **Salas cerradas (código muerto)**: los componentes de preview/column-mapper y dos servicios no tienen rutas que los referencien.
- **El anexo sin tuberías**: el contenedor de IA corre pero nada del flujo de importación lo llama.
- **Muros portantes ausentes en el sótano**: sin tablas `transfers` ni `import_batches`, y `ignore_in_analysis` se guarda pero ninguna consulta de resúmenes lo usa.

## Referencia de evidencias (detalladas en la auditoría)

| Elemento del plano | Evidencia |
|---|---|
| Entrada nginx | `docker-compose.yml:85-99` |
| Rutas frontend | `client/src/app/app.routes.ts:7-40` |
| Registro de routers + JWT | `api/routers/__init__.py:32-67` |
| ImportService | `api/services/imports/import_service.py:35-195` |
| Dedup hash | `api/services/core/dedup_service.py:29-46` |
| IA desconectada | `excel-import.component.ts:342-373` (comentado), `import_service.py:33` |
| 22 tablas + UNIQUE dedup | `.claude/database/er.sql` |
| Falta transfers/batches/índice date | er.sql completo + grep (ver auditoría P0-3, P1-1, P3-1) |
