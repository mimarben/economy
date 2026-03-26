Contexto:
Aplicación fullstack:
- Backend: Flask + SQLAlchemy + PostgreSQL + Alembic + Pydantic
- Frontend: Angular 21 + Angular Material

Sistema actual:
- Importación de Excel bancario con transacciones
- Categorización híbrida:
  1. Reglas
  2. IA (fallback)

Problema actual:
- Las reglas están hardcodeadas en frontend (category-rules.const.ts)
- Quiero mover TODA la lógica al backend

---

ARQUITECTURA GLOBAL (OBLIGATORIO):

Flujo de categorización:

1. Backend recibe transacción (description, amount, type)
2. Backend aplica reglas activas ordenadas por prioridad
3. Si no hay match → usar IA
4. Si IA falla → marcar como "uncategorized"

El frontend NO aplica reglas.

---

1) Backend - CategoryRule

Modelo SQLAlchemy:

- Hereda de BaseAuditModel (api/models/core/base.py):
  - created_at
  - updated_at
  - created_by (opcional)

Campos:
- id
- name
- pattern (regex)
- type (expense | income | investment)
- category_id
- priority (int)
- is_active (bool)

Requisitos:
- Index por (type, priority)
- Validar regex en creación

---

Repository:
- get_all()
- get_active_by_type(type)
- create()
- update()
- delete()

---

Service:

Función clave:
categorize_transaction(description: str, type: str)

Lógica:
- Iterar reglas activas ordenadas por prioridad DESC
- regex match (case insensitive)
- return category_id si match
- si no → llamar a IA service

---

2) Importación (CRÍTICO)

Archivo:
- backend: api/services/imports/import_service.py
- frontend: transaction-import.service.ts

Requisitos:

- La importación debe ser UNA TRANSACCIÓN DB

Comportamiento:
- Parsear Excel
- Validar todas las filas
- Categorizar cada transacción:
    - reglas → IA → fallback null

Regla de negocio:

OPCIÓN A (RECOMENDADA):
- Insertar TODO
- Si no categorizado → category_id = null + flag "needs_review"

OPCIÓN B (STRICT MODE):
- Si alguna fila falla → rollback completo

Implementación:
- usar session.begin() (SQLAlchemy)
- commit solo si todo OK

IMPORTANTE:
- NO hacer commits por fila

---

3) Frontend - Categorization Rules

Eliminar completamente:
- category-rules.const.ts

Crear módulo:
- Categorization Rules

CRUD:
- Tabla Angular Material
- Formulario:
  - name
  - pattern
  - type (select)
  - category (select)
  - priority
  - is_active

Service:
- category-rule.service.ts (HTTP)

El frontend SOLO consume API

---

4) Dashboard (Summary)

Charts:
- ng2-charts + Chart.js

Componentes:
- expenses chart
- income chart
- investment chart
- comparison chart

Filtros:
- week / month / year / custom range

Backend:
- endpoint /summary

Debe devolver:
{
  totals_by_category,
  totals_over_time,
  income_vs_expense
}

El frontend NO calcula agregaciones

---

5) UI / UX

Angular Material custom theme:

- Sidenav layout
- Toolbar superior
- Cards con border-radius 16px
- Grid layout responsive
- Espaciado consistente (8px scale)

Opcional:
- Dark mode

---

Formato esperado:
- Código por capas
- Separación clara
- Explicaciones breves en comentarios