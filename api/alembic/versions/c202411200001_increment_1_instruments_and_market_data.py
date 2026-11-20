"""Increment 1: Instruments, Identifiers, Compositions, FX Rates and Market Quote History

Revision ID: c202411200001
Revises: b7c4d9e2f8a1
Create Date: 2026-11-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c202411200001'
down_revision: Union[str, Sequence[str], None] = 'b7c4d9e2f8a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create instruments table
    op.create_table(
        'instruments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_class', sa.String(length=32), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('instrument_type', sa.String(length=32), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['investments_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_instruments_name', 'instruments', ['name'])
    op.create_index('ix_instruments_instrument_type', 'instruments', ['instrument_type'])

    # Create instrument_identifiers table with unique constraint using func.coalesce
    op.create_table(
        'instrument_identifiers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('instrument_id', sa.Integer(), nullable=False),
        sa.Column('identifier_type', sa.String(length=16), nullable=False),
        sa.Column('value', sa.String(length=64), nullable=False),
        sa.Column('exchange', sa.String(length=16), nullable=True),
        sa.Column('provider', sa.String(length=32), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # Unique constraint over (identifier_type, value, exchange, provider)
    # COALESCE used to treat NULL and empty string as equivalent
    op.execute("""
        CREATE UNIQUE INDEX uq_instrument_identifier_namespace 
        ON instrument_identifiers (
            identifier_type, 
            value, 
            COALESCE(NULLIF(exchange, ''), ''),
            COALESCE(NULLIF(provider, ''), '')
        )
    """)

    # Create instrument_compositions table
    op.create_table(
        'instrument_compositions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('parent_instrument_id', sa.Integer(), nullable=False),
        sa.Column('child_instrument_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Numeric(18, 10), nullable=False),
        sa.Column('weight', sa.Numeric(18, 10), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['child_instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('parent_instrument_id', 'child_instrument_id', name='uq_instrument_composition_unique')
    )
    op.create_index('ix_instrument_compositions_parent', 'instrument_compositions', ['parent_instrument_id'])
    op.create_index('ix_instrument_compositions_child', 'instrument_compositions', ['child_instrument_id'])

    # Create fx_rates table
    op.create_table(
        'fx_rates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('base_currency', sa.String(length=8), nullable=False),
        sa.Column('target_currency', sa.String(length=8), nullable=False),
        sa.Column('rate', sa.Numeric(18, 10), nullable=False),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # Unique constraint over (base_currency, target_currency, source, published_at)
    op.execute("""
        CREATE UNIQUE INDEX uq_fx_rate_unique 
        ON fx_rates (base_currency, target_currency, source, published_at)
    """)
    op.create_index('ix_fx_rate_base_target', 'fx_rates', ['base_currency', 'target_currency'])

    # Create market_quote_history table
    op.create_table(
        'market_quote_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('instrument_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(18, 10), nullable=False),
        sa.Column('quoted_at', sa.DateTime(), nullable=False),
        sa.Column('price_type', sa.String(length=16), nullable=True),
        sa.Column('source', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_market_quote_history_instrument', 'market_quote_history', ['instrument_id'])
    op.create_index('ix_market_quote_history_quoted_at', 'market_quote_history', ['quoted_at'])

    # Add new columns to investments table
    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('instrument_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('source_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_investments_instrument', 'instruments', ['instrument_id'], ['id'])
        batch_op.create_foreign_key('fk_investments_source', 'sources', ['source_id'], ['id'])

    # Add new columns to investments_logs table
    with op.batch_alter_table('investments_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fees', sa.Numeric(18, 10), nullable=True))
        batch_op.add_column(sa.Column('external_ref', sa.String(length=255), nullable=True))

    # Add new columns to market_quotes table
    with op.batch_alter_table('market_quotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('instrument_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('quoted_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('price_type', sa.String(length=16), nullable=True))
        batch_op.create_foreign_key('fk_market_quotes_instrument', 'instruments', ['instrument_id'], ['id'])


def downgrade() -> None:
    # Drop new columns from market_quotes table
    with op.batch_alter_table('market_quotes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_market_quotes_instrument', type_='foreignkey')
        batch_op.drop_column('price_type')
        batch_op.drop_column('quoted_at')
        batch_op.drop_column('instrument_id')

    # Drop new columns from investments_logs table
    with op.batch_alter_table('investments_logs', schema=None) as batch_op:
        batch_op.drop_column('external_ref')
        batch_op.drop_column('fees')

    # Drop new columns from investments table
    with op.batch_alter_table('investments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_investments_source', type_='foreignkey')
        batch_op.drop_constraint('fk_investments_instrument', type_='foreignkey')
        batch_op.drop_column('source_id')
        batch_op.drop_column('instrument_id')

    # Drop market_quote_history table
    op.drop_index('ix_market_quote_history_quoted_at', table_name='market_quote_history')
    op.drop_index('ix_market_quote_history_instrument', table_name='market_quote_history')
    op.drop_table('market_quote_history')

    # Drop fx_rates table
    op.drop_index('ix_fx_rate_base_target', table_name='fx_rates')
    op.execute('DROP INDEX IF EXISTS uq_fx_rate_unique')
    op.drop_table('fx_rates')

    # Drop instrument_compositions table
    op.drop_index('ix_instrument_compositions_child', table_name='instrument_compositions')
    op.drop_index('ix_instrument_compositions_parent', table_name='instrument_compositions')
    op.drop_table('instrument_compositions')

    # Drop instrument_identifiers table
    op.execute('DROP INDEX IF EXISTS uq_instrument_identifier_namespace')
    op.drop_table('instrument_identifiers')

    # Drop instruments table
    op.drop_index('ix_instruments_instrument_type', table_name='instruments')
    op.drop_index('ix_instruments_name', table_name='instruments')
    op.drop_table('instruments')
