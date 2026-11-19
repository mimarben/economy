"""add isin to investments and market_quotes cache table

Revision ID: b7c4d9e2f8a1
Revises: a1b2c3d4e5f6
Create Date: 2026-11-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7c4d9e2f8a1'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add optional ISIN to investments and the market_quotes cache table."""
    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('isin', sa.String(length=12), nullable=True))
        batch_op.create_index('ix_investments_isin', ['isin'])

    op.create_table(
        'market_quotes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('isin', sa.String(length=12), nullable=False),
        sa.Column('symbol', sa.String(length=32), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('instrument_type', sa.String(length=32), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('last_price', sa.Numeric(18, 6), nullable=True),
        sa.Column('previous_close', sa.Numeric(18, 6), nullable=True),
        sa.Column('source', sa.String(length=20), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('isin', name='uq_market_quotes_isin'),
    )
    op.create_index('ix_market_quotes_isin', 'market_quotes', ['isin'])


def downgrade() -> None:
    """Remove market data support."""
    op.drop_index('ix_market_quotes_isin', table_name='market_quotes')
    op.drop_table('market_quotes')

    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.drop_index('ix_investments_isin')
        batch_op.drop_column('isin')
