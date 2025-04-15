"""Add active or not in users

Revision ID: e4291e4beb9e
Revises: 8e41d1ac6405
Create Date: 2025-04-15 11:32:06.469526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4291e4beb9e'
down_revision: Union[str, None] = '8e41d1ac6405'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Rename the existing table
    op.rename_table('users', 'users_old')

    # Step 2: Create a new table with the updated schema
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),  # Set NOT NULL constraint
        sa.Column('surname1', sa.String(), nullable=False),  # Set NOT NULL constraint
        sa.Column('surname2', sa.String()),
        sa.Column('dni', sa.String(), nullable=False),  # Set NOT NULL constraint
        sa.Column('email', sa.String()),
        sa.Column('telephone', sa.Integer()),
        sa.Column('active', sa.Boolean(), nullable=True),  # New column added
    )

    # Step 3: Copy data from the old table to the new table
    op.execute(
        """
        INSERT INTO users (id, name, surname1, surname2, dni, email, telephone)
        SELECT id, name, surname1, surname2, dni, email, telephone FROM users_old
        """
    )

    # Step 4: Drop the old table
    op.drop_table('users_old')



def downgrade() -> None:
    # Reverse the steps for downgrading (if needed)
    op.rename_table('users', 'users_new')

    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('surname1', sa.String(), nullable=True),
        sa.Column('surname2', sa.String()),
        sa.Column('dni', sa.String(), nullable=True),
        sa.Column('email', sa.String()),
        sa.Column('telephone', sa.Integer()),
    )

    op.execute(
        """
        INSERT INTO users (id, name, surname1, surname2, dni, email, telephone)
        SELECT id, name, surname1, surname2, dni, email, telephone FROM users_new
        """
    )

    op.drop_table('users_new')