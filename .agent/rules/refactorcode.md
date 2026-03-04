---
trigger: always_on
---

ECONOMY APP TECHNICAL SPECIFICATION AND IMPROVEMENT DOCUMENT Version:
1.0 Date: 2026

Stack actual: Backend: Flask, SQLAlchemy, PostgreSQL, Alembic, Pydantic
Frontend: Angular 19, Angular Material

  --------------
  1. OBJECTIVE
  --------------

Este documento define las mejoras técnicas necesarias para evolucionar
la aplicación Economy hacia estándares modernos de desarrollo
manteniendo la arquitectura actual.

Objetivos: 1. Revisar la estructura del backend. 2. Mejorar la
seguridad. 3. Mejorar la visualización del frontend Angular. 4. Aplicar
buenas prácticas modernas. 5. Realizar cambios incrementales sin
reescribir la aplicación.

  -------------------------
  2. CURRENT ARCHITECTURE
  -------------------------

Backend: - Flask API - SQLAlchemy ORM - PostgreSQL - Alembic - Pydantic

Frontend: - Angular 19 - Angular Material

La aplicación gestiona: usuarios, hogares, cuentas bancarias, gastos,
ingresos, inversiones y ahorro.

  -------------------
  3. DATABASE MODEL
  -------------------

Entidades principales:

users households household_members accounts banks expenses incomes
investments savings sources

Categorías:

catExpenses catIncomes catInvestment

Históricos:

savingsLog investmentLog

Resumen financiero:

financial_summary

  --------------------------
  4. DATABASE IMPROVEMENTS
  --------------------------

4.1 Naming conventions

Usar snake_case en todas las columnas.

Incorrecto: AccountId bankID userID

Correcto: account_id bank_id user_id

4.2 Auditoría

Añadir en todas las tablas:

created_at updated_at deleted_at

4.3 Índices recomendados

user_id account_id category_id household_id date

Ejemplo: CREATE INDEX idx_expenses_user_id ON expenses(user_id);

4.4 Identificadores

Migrar progresivamente a UUID.

Ejemplo: id UUID PRIMARY KEY DEFAULT gen_random_uuid()

  -------------------------
  5. BACKEND ARCHITECTURE
  -------------------------

Arquitectura por capas:

Controller Service Repository Model Schema

Controller: gestiona endpoints HTTP.

Service: contiene lógica de negocio.

Repository: acceso a base de datos.

Model: modelos SQLAlchemy.

Schema: validación Pydantic.

  ----------------------
  6. BACKEND STRUCTURE
  ----------------------

backend/

app/ api/ routes/ auth_routes.py expenses_routes.py incomes_routes.py
accounts_routes.py

services/ expense_service.py income_service.py

repositories/ expense_repository.py

models/ user.py expense.py income.py

schemas/ expense_schema.py income_schema.py

core/ config.py security.py logging.py

db/ session.py migrations/

alembic/ run.py

  ------------------------------
  7. SQLALCHEMY BEST PRACTICES
  ------------------------------

Evitar:

User.query.filter(…)

Usar:

stmt = select(User).where(User.email == email) result =
session.execute(stmt).scalar_one()

  ------------------------
  8. PYDANTIC VALIDATION
  ------------------------

Separar modelos de entrada y salida.

Entrada: ExpenseCreate

Salida: ExpenseResponse

Ejemplo campos:

ExpenseCreate amount category_id description date

ExpenseResponse id amount category description

  ---------------------
  9. BACKEND SECURITY
  ---------------------

Autenticación: JWT + refresh tokens

Librería recomendada: flask-jwt-extended

Password hashing: argon2 o bcrypt

Rate limiting: flask-limiter

Ejemplo: 100 requests por minuto

CORS: flask-cors

Security headers: Content-Security-Policy X-Frame-Options
X-Content-Type-Options Strict-Transport-Security

  ------------------------
  10. ALEMBIC MIGRATIONS
  ------------------------

No modificar migraciones existentes.

Crear nuevas revisiones:

alembic revision –autogenerate

Revisar manualmente antes de aplicar.

  ---------------------------
  11. FRONTEND ARCHITECTURE
  ---------------------------

src/app

core services guards interceptors

shared components dialogs tables

features dashboard expenses incomes investments accounts

  -----------------------------
  12. ANGULAR MATERIAL LAYOUT
  -----------------------------

mat-sidenav-container

sidenav dashboard expenses incomes investments accounts

content router-outlet

  -------------------------
  13. MATERIAL COMPONENTS
  -------------------------

mat-table mat-paginator mat-sort mat-dialog mat-snackbar mat-form-field

Tabla gastos:

date description category account amount actions

  ---------------------
  14. USER EXPERIENCE
  ---------------------

Filtros:

last 7 days last month last year

Búsqueda:

description category account

Dashboard:

expenses by category income vs expense net worth evolution

Charts: Chart.js

  -----------------
  15. PERFORMANCE
  -----------------

Crear índices en:

expenses(user_id) expenses(date) expenses(category_id) accounts(user_id)
household_members(household_id)

  -------------
  16. ROADMAP
  -------------

Fase 1 Refactor backend

Fase 2 Seguridad

Fase 3 Frontend Angular Material

Fase 4 Dashboard financiero

  ----------------
  17. CONCLUSION
  ----------------

La arquitectura actual es funcional pero puede mejorar en:

estructura backend seguridad consistencia de datos experiencia de
usuario

Las mejoras propuestas alinean la aplicación con estándares modernos de
desarrollo.
