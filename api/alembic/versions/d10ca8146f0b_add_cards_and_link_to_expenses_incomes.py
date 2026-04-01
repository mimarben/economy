"""add cards and link to expenses/incomes

Revision ID: d10ca8146f0b
Revises: 20260330masteruniquekeys
Create Date: 2026-04-01 23:57:22.588776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd10ca8146f0b'
down_revision: Union[str, Sequence[str], None] = '20260330masteruniquekeys'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
