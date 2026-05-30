"""add ignore_in_analysis to incomes table

Revision ID: add_ignore_in_analysis_to_incomes
Revises: make_accounts_user_id_nullable
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'incomes_ignore_flag'
down_revision: Union[str, Sequence[str], None] = 'make_accounts_user_id_nullable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('incomes', sa.Column('ignore_in_analysis', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('incomes', 'ignore_in_analysis')
