"""Add expense user tracking fields

Revision ID: add_expense_user_tracking
Revises: m2m_account_users
Create Date: 2026-04-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_expense_user_tracking'
down_revision: Union[str, Sequence[str], None] = 'm2m_account_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_personal column to expenses
    op.add_column('expenses', sa.Column('is_personal', sa.Boolean(), nullable=False, server_default='true'))
    
    # Add user_id foreign key to expenses
    op.add_column('expenses', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_expenses_user_id'), 'expenses', ['user_id'], unique=False)
    op.create_foreign_key('fk_expenses_user_id', 'expenses', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key and index
    op.drop_constraint('fk_expenses_user_id', 'expenses', type_='foreignkey')
    op.drop_index(op.f('ix_expenses_user_id'), table_name='expenses')
    
    # Drop columns
    op.drop_column('expenses', 'user_id')
    op.drop_column('expenses', 'is_personal')
