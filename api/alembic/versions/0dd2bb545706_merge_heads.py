"""merge heads

Revision ID: 0dd2bb545706
Revises: a5242832fd8c, add_expense_user_tracking
Create Date: 2026-04-23 19:03:27.681546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dd2bb545706'
down_revision: Union[str, Sequence[str], None] = ('a5242832fd8c', 'add_expense_user_tracking')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
