"""make accounts.user_id nullable (unused legacy column, M2M via account_users)

Revision ID: make_accounts_user_id_nullable
Revises: 0dd2bb545706, source_rules_v2
Create Date: 2026-05-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'make_accounts_user_id_nullable'
down_revision: Union[str, Sequence[str], None] = ('0dd2bb545706', 'source_rules_v2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('accounts', 'user_id', nullable=True)


def downgrade() -> None:
    op.alter_column('accounts', 'user_id', nullable=False)
