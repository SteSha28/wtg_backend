"""Add default source_user

Revision ID: 14a1a93fdbe8
Revises: 76977b6bfa1e
Create Date: 2025-04-29 13:15:47.629558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14a1a93fdbe8'
down_revision: Union[str, None] = '76977b6bfa1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        INSERT INTO source_users (id, name, description)
        VALUES (1, 'default_source', 'unknown_source');
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM source_users
        WHERE id = 1;
        """
    )
