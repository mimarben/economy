"""account_balance_numeric_20_10_for_crypto

Revision ID: a80dc79a6368
Revises: incomes_ignore_flag
Create Date: 2026-06-03 17:02:36.367414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a80dc79a6368'
down_revision: Union[str, Sequence[str], None] = 'incomes_ignore_flag'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.NUMERIC(precision=12, scale=2),
               type_=sa.Numeric(precision=20, scale=10),
               existing_nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.Numeric(precision=20, scale=10),
               type_=sa.NUMERIC(precision=12, scale=2),
               existing_nullable=True)
