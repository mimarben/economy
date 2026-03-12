"""seed default categories

Revision ID: 0acf1443ad4f
Revises: e575401010de
Create Date: 2026-03-12 19:33:34.340553

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0acf1443ad4f"
down_revision: Union[str, Sequence[str], None] = "e575401010de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # UNIQUE constraints
    op.create_unique_constraint(
        "uq_expense_category_name", "expenses_categories", ["name"]
    )

    op.create_unique_constraint(
        "uq_income_category_name", "incomes_categories", ["name"]
    )
    op.create_unique_constraint(
        "uq_investment_category_name", "investments_categories", ["name"]
    )

    # Expense categories
    op.execute(
        """
    INSERT INTO expenses_categories (name, description, active) VALUES
    ('Supermercado', 'Compras de alimentación y hogar', true),
    ('Compras', 'Compras online o tiendas', true),
    ('Transporte', 'Taxi, Uber, transporte público', true),
    ('Gasolina', 'Combustible del coche', true),
    ('Restaurantes', 'Restaurantes y comida fuera', true),
    ('Suscripciones', 'Servicios recurrentes', true),
    ('Internet', 'Fibra e internet', true),
    ('Teléfono', 'Gastos de telefonía móvil', true),
    ('Educación', 'Educación y formación', true),
    ('Colegio Agustinas', 'Colegio Agustinas Valladolid', true),
    ('Kids&Us', 'Academia de inglés Kids&Us', true),
    ('Seguros', 'Seguros del hogar, coche, vida', true),
    ('Hogar', 'Gastos del hogar', true),
    ('Salud', 'Farmacia y gastos médicos', true),
    ('Ocio', 'Entretenimiento', true),
    ('Viajes', 'Viajes y vacaciones', true),
    ('Impuestos', 'Impuestos y tasas', true),
    ('Otros', 'Otros gastos', true);
    """
    )

    # Income categories
    op.execute(
        """
    INSERT INTO incomes_categories (name, description, active) VALUES
    ('Salario', 'Ingreso de nómina', true),
    ('Bonus', 'Bonificaciones laborales', true),
    ('Dividendos', 'Dividendos de inversiones', true),
    ('Intereses', 'Intereses bancarios o bonos', true),
    ('Venta de activos', 'Venta de inversiones', true),
    ('Reembolsos', 'Reembolsos o devoluciones', true),
    ('Otros ingresos', 'Otros ingresos', true);
    """
    )

    op.execute(
        """
        INSERT INTO investments_categories (name, description, active) VALUES
        ('ETF', 'Exchange Traded Funds', true),
        ('Acciones', 'Acciones individuales', true),
        ('Fondos', 'Fondos de inversión', true),
        ('Bonos', 'Bonos gubernamentales o corporativos', true),
        ('Cripto', 'Criptomonedas', true),
        ('Plan de pensiones', 'Planes de pensiones', true),
        ('Otros', 'Otros activos de inversión', true);
        """
    )


def downgrade() -> None:
    op.execute(
        """
    DELETE FROM expenses_categories
    WHERE name IN (
        'Supermercado',
        'Compras',
        'Transporte',
        'Gasolina',
        'Restaurantes',
        'Suscripciones',
        'Internet',
        'Teléfono',
        'Educación',
        'Colegio Agustinas',
        'Kids&Us',
        'Seguros',
        'Hogar',
        'Salud',
        'Ocio',
        'Viajes',
        'Impuestos',
        'Otros'
    );
    """
    )
    op.execute(
        """
    DELETE FROM incomes_categories
    WHERE name IN (
        'Salario',
        'Bonus',
        'Dividendos',
        'Intereses',
        'Venta de activos',
        'Reembolsos',
        'Otros ingresos'
    );
    """
    )
   
    op.execute(
        """
DELETE FROM investments_categories
WHERE name IN (
    'ETF',
    'Acciones',
    'Fondos',
    'Bonos',
    'Cripto',
    'Plan de pensiones',
    'Otros'
);
"""
    )



