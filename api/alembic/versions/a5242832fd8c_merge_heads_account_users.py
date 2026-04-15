"""merge heads account_users

Revision ID: a5242832fd8c
Revises: 3d8e9f2a1b4c, m2m_account_users
Create Date: 2026-04-15 18:45:55.921882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5242832fd8c'
down_revision: Union[str, Sequence[str], None] = ('3d8e9f2a1b4c', 'm2m_account_users')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
