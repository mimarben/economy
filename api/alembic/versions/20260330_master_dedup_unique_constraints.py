"""add unique constraints on master entities for natural keys

Revision ID: 20260330masteruniquekeys
Revises: 5d98c32cee83
Create Date: 2026-03-30 13:40:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '20260330masteruniquekeys'
down_revision = '5d98c32cee83'
branch_labels = None
depends_on = None


def _assert_no_duplicates(conn, table, column):
    duplicates = conn.execute(
        text(
            f"""
            SELECT {column}, COUNT(*) AS cnt
            FROM {table}
            WHERE {column} IS NOT NULL
            GROUP BY {column}
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()
    if duplicates:
        duplicate_vals = ', '.join(str(r[0]) for r in duplicates[:10])
        raise RuntimeError(
            f"Duplicate values detected for {table}.{column}: {duplicate_vals}. "
            "Resolve duplicates before applying this migration."
        )


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # Account IBAN
    if 'uq_accounts_iban' not in [uc['name'] for uc in inspector.get_unique_constraints('accounts')]:
        _assert_no_duplicates(conn, 'accounts', 'iban')
        with op.batch_alter_table('accounts', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_accounts_iban', ['iban'])

    # User DNI
    if 'uq_users_dni' not in [uc['name'] for uc in inspector.get_unique_constraints('users')]:
        _assert_no_duplicates(conn, 'users', 'dni')
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_users_dni', ['dni'])

    # Bank CIF
    bank_columns = [c['name'] for c in inspector.get_columns('banks')]
    if 'cif' not in bank_columns:
        with op.batch_alter_table('banks', schema=None) as batch_op:
            batch_op.add_column(sa.Column('cif', sa.String(), nullable=True))
        inspector = inspect(conn)  # refresh inspector metadata

    if 'uq_banks_cif' not in [uc['name'] for uc in inspector.get_unique_constraints('banks')]:
        _assert_no_duplicates(conn, 'banks', 'cif')
        with op.batch_alter_table('banks', schema=None) as batch_op:
            batch_op.create_unique_constraint('uq_banks_cif', ['cif'])


def downgrade() -> None:
    with op.batch_alter_table('banks', schema=None) as batch_op:
        batch_op.drop_constraint('uq_banks_cif', type_='unique')
        batch_op.drop_column('cif')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_dni', type_='unique')
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_constraint('uq_accounts_iban', type_='unique')
