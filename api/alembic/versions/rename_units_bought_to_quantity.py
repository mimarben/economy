"""rename units_bought to quantity and make current_value nullable in investments_logs

Revision ID: a1b2c3d4e5f6
Revises: f9c1c8a9bb59
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'a80dc79a6368'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('investments_logs', 'current_value', existing_type=sa.Numeric(12, 2), nullable=True)
    op.alter_column('investments_logs', 'units_bought', new_column_name='quantity', existing_type=sa.Numeric(12, 6), nullable=True)


def downgrade() -> None:
    op.alter_column('investments_logs', 'quantity', new_column_name='units_bought', existing_type=sa.Numeric(12, 6), nullable=True)
    op.alter_column('investments_logs', 'current_value', existing_type=sa.Numeric(12, 2), nullable=False)
