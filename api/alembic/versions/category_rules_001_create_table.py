"""Create category_rules table

Revision ID: category_rules_001
Revises: 0acf1443ad4f
Create Date: 2026-03-26 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "category_rules_001"
down_revision: Union[str, Sequence[str], None] = "0acf1443ad4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type for transaction type
    sa.Enum('expense', 'income', 'investment', name='transactionenum').create(op.get_bind(), checkfirst=True)
    
    # Create category_rules table
    op.create_table(
        'category_rules',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('pattern', sa.String(1000), nullable=False),
        sa.Column('type', sa.Enum('expense', 'income', 'investment', name='transactionenum'), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False, onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_category_rules_active_type_priority', 'is_active', 'type', 'priority'),
        sa.Index('idx_category_rules_type_priority', 'type', 'priority'),
    )


def downgrade() -> None:
    op.drop_table('category_rules')
    sa.Enum('expense', 'income', 'investment', name='transactionenum').drop(op.get_bind(), checkfirst=True)
