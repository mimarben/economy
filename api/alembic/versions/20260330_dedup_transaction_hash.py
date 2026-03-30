"""add transaction dedup hash on expenses, incomes, investments

Revision ID: 20260330dedup
Revises: e575401010de
Create Date: 2026-03-30 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import hashlib
from decimal import Decimal, ROUND_HALF_UP

# revision identifiers, used by Alembic.
revision = '20260330dedup'
down_revision = 'e575401010de'
branch_labels = None
depends_on = None


def _normalize_description(description):
    if description is None:
        return ''
    return ' '.join(str(description).strip().lower().split())


def _normalize_date(dt):
    if isinstance(dt, str):
        dt = sa.sql.literal_column(f"'{dt}'")
    if hasattr(dt, 'strftime'):
        return dt.strftime('%Y-%m-%d')
    return str(dt)


def _normalize_amount(amount):
    return f"{Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"


def _dedup(account_id, dt, amount, description):
    normalized = f"{account_id}|{_normalize_date(dt)}|{_normalize_amount(amount)}|{_normalize_description(description)}"
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def upgrade():
    # Add dedup_hash columns as nullable initially
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dedup_hash', sa.String(length=64), nullable=True))
    with op.batch_alter_table('incomes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dedup_hash', sa.String(length=64), nullable=True))
    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dedup_hash', sa.String(length=64), nullable=True))

    conn = op.get_bind()

    for table in ('expenses', 'incomes', 'investments'):
        rows = conn.execute(text(f"SELECT id, account_id, date, amount, description FROM {table}"))
        updates = []
        for row in rows:
            account_id = row['account_id']
            date_value = row['date']
            amount = row['amount']
            description = row['description']
            if account_id is None:
                continue
            dedup_hash = _dedup(account_id, date_value, amount, description)
            updates.append({'id': row['id'], 'dedup_hash': dedup_hash})

        for u in updates:
            conn.execute(text(f"UPDATE {table} SET dedup_hash = :dedup_hash WHERE id = :id"), **u)

        # Remove exact duplicates for existing data (keep first row by id)
        conn.execute(text(f"DELETE FROM {table} WHERE id NOT IN (SELECT min(id) FROM {table} GROUP BY account_id, dedup_hash)"))

    # Make dedup_hash non-null and add unique constraints
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.alter_column('dedup_hash', nullable=False)
        batch_op.create_unique_constraint('uq_expenses_account_dedup_hash', ['account_id', 'dedup_hash'])
    with op.batch_alter_table('incomes', schema=None) as batch_op:
        batch_op.alter_column('dedup_hash', nullable=False)
        batch_op.create_unique_constraint('uq_incomes_account_dedup_hash', ['account_id', 'dedup_hash'])
    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.alter_column('dedup_hash', nullable=False)
        batch_op.create_unique_constraint('uq_investments_account_dedup_hash', ['account_id', 'dedup_hash'])


def downgrade():
    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.drop_constraint('uq_investments_account_dedup_hash', type_='unique')
        batch_op.drop_column('dedup_hash')
    with op.batch_alter_table('incomes', schema=None) as batch_op:
        batch_op.drop_constraint('uq_incomes_account_dedup_hash', type_='unique')
        batch_op.drop_column('dedup_hash')
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_constraint('uq_expenses_account_dedup_hash', type_='unique')
        batch_op.drop_column('dedup_hash')
