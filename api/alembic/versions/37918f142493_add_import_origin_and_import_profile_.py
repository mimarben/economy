"""add import_origin and import_profile  and relations with cards and accounts

Revision ID: 37918f142493
Revises: df68c2d66940
Create Date: 2026-04-06 07:45:17.363811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37918f142493'
down_revision: Union[str, Sequence[str], None] = 'df68c2d66940'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
