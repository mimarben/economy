"""Refactor source_rules to independent regex matching

Revision ID: source_rules_v2
Revises: source_rules_v1
Create Date: 2026-04-28 00:00:00.000000

Drops category_rule_id (association model) and adds name/pattern/type/priority
so SourceRule mirrors CategoryRule and runs independently during categorization.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'source_rules_v2'
down_revision: Union[str, Sequence[str], None] = 'source_rules_v1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TRANSACTION_ENUM = sa.Enum('expense', 'income', 'investment', name='transactionenum', create_type=False)


def upgrade() -> None:
    # Remove old association columns / indexes
    op.drop_index('idx_source_rules_category_rule_id', table_name='source_rules')
    op.drop_index('idx_source_rules_active', table_name='source_rules')
    op.drop_constraint('source_rules_category_rule_id_fkey', 'source_rules', type_='foreignkey')
    op.drop_column('source_rules', 'category_rule_id')

    # Add independent matching columns (server_default allows existing rows)
    op.add_column('source_rules', sa.Column('name', sa.String(255), nullable=False, server_default='migrated'))
    op.add_column('source_rules', sa.Column('pattern', sa.String(1000), nullable=False, server_default='.*'))
    op.add_column('source_rules', sa.Column('type', _TRANSACTION_ENUM, nullable=False, server_default='expense'))
    op.add_column('source_rules', sa.Column('priority', sa.Integer(), nullable=False, server_default='100'))

    # Remove server defaults — enforce at application level going forward
    op.alter_column('source_rules', 'name', server_default=None)
    op.alter_column('source_rules', 'pattern', server_default=None)
    op.alter_column('source_rules', 'type', server_default=None)
    op.alter_column('source_rules', 'priority', server_default=None)

    # New indexes mirroring category_rules
    op.create_index('idx_source_rules_active_type_priority', 'source_rules', ['is_active', 'type', 'priority'])
    op.create_index('idx_source_rules_type_priority', 'source_rules', ['type', 'priority'])


def downgrade() -> None:
    op.drop_index('idx_source_rules_type_priority', table_name='source_rules')
    op.drop_index('idx_source_rules_active_type_priority', table_name='source_rules')

    op.drop_column('source_rules', 'priority')
    op.drop_column('source_rules', 'type')
    op.drop_column('source_rules', 'pattern')
    op.drop_column('source_rules', 'name')

    op.add_column('source_rules', sa.Column('category_rule_id', sa.Integer(), nullable=False))
    op.create_foreign_key('source_rules_category_rule_id_fkey', 'source_rules', 'category_rules', ['category_rule_id'], ['id'])
    op.create_index('idx_source_rules_category_rule_id', 'source_rules', ['category_rule_id'])
    op.create_index('idx_source_rules_active', 'source_rules', ['is_active'])
