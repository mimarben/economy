"""add import_origin and import_profile  and relations with cards and accounts v3

Revision ID: af01a4e790bf
Revises: dcbad4bcf160
Create Date: 2026-04-06 08:29:46.103370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af01a4e790bf'
down_revision: Union[str, Sequence[str], None] = 'dcbad4bcf160'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
