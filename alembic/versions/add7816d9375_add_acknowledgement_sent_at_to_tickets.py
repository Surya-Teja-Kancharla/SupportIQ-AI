"""add acknowledgement sent at to tickets

Revision ID: add7816d9375
Revises: 3695a5f7fbcc
Create Date: 2026-07-05 20:54:17.898898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add7816d9375'
down_revision: Union[str, Sequence[str], None] = '3695a5f7fbcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
