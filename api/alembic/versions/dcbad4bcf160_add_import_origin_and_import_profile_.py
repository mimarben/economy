"""add import_origin and import_profile  and relations with cards and accounts v2

Revision ID: dcbad4bcf160
Revises: 37918f142493
Create Date: 2026-04-06 08:27:48.227227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcbad4bcf160'
down_revision: Union[str, Sequence[str], None] = '37918f142493'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
