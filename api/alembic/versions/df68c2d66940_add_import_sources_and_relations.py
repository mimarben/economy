"""add import_sources and relations

Revision ID: df68c2d66940
Revises: 63829b82b09d
Create Date: 2026-04-06 07:30:08.156540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df68c2d66940'
down_revision: Union[str, Sequence[str], None] = '63829b82b09d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
