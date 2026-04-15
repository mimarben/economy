"""Add account_users many-to-many relationship

Revision ID: m2m_account_users
Revises: c059fc3d2f51
Create Date: 2026-04-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'm2m_account_users'
down_revision: Union[str, Sequence[str], None] = 'c059fc3d2f51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the account_users table
    op.create_table(
        'account_users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', 'user_id', name='uq_account_user')
    )
    op.create_index(op.f('ix_account_users_account_id'), 'account_users', ['account_id'], unique=False)
    op.create_index(op.f('ix_account_users_user_id'), 'account_users', ['user_id'], unique=False)

    # Migrate existing data from accounts.user_id to account_users
    op.execute('''
        INSERT INTO account_users (account_id, user_id, created_at, updated_at)
        SELECT id, user_id, created_at, updated_at FROM accounts
        WHERE user_id IS NOT NULL
    ''')

    # Remove the user_id foreign key from accounts
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_constraint('accounts_user_id_fkey', type_='foreignkey')
        batch_op.drop_index(op.f('ix_accounts_user_id'))
        batch_op.drop_column('user_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back user_id column to accounts
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(op.f('ix_accounts_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('accounts_user_id_fkey', 'users', ['user_id'], ['id'])

    # Migrate data back from account_users to accounts
    op.execute('''
        UPDATE accounts SET user_id = au.user_id
        FROM account_users au
        WHERE accounts.id = au.account_id
    ''')

    # Drop the account_users table
    op.drop_index(op.f('ix_account_users_user_id'), table_name='account_users')
    op.drop_index(op.f('ix_account_users_account_id'), table_name='account_users')
    op.drop_table('account_users')
