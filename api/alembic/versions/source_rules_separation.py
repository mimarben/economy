"""Separate source rules into dedicated table

Revision ID: source_rules_v1
Revises: 3d8e9f2a1b4c
Create Date: 2026-04-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'source_rules_v1'
down_revision: Union[str, Sequence[str], None] = '3d8e9f2a1b4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create source_rules table
    op.create_table(
        'source_rules',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('category_rule_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['category_rule_id'], ['category_rules.id'], ),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_source_rules_category_rule_id', 'source_rules', ['category_rule_id'])
    op.create_index('idx_source_rules_source_id', 'source_rules', ['source_id'])
    op.create_index('idx_source_rules_active', 'source_rules', ['is_active'])

    # Note: source_id removal from category_rules is handled separately
    # to ensure data integrity (no source_id on category_rules in current schema)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop source_rules table and indexes
    op.drop_index('idx_source_rules_active', 'source_rules')
    op.drop_index('idx_source_rules_source_id', 'source_rules')
    op.drop_index('idx_source_rules_category_rule_id', 'source_rules')
    op.drop_table('source_rules')
