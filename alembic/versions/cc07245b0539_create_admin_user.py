"""create admin user

Revision ID: cc07245b0539
Revises: ea2bea8905bf
Create Date: 2025-05-26 17:04:28.063015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc07245b0539'
down_revision: Union[str, None] = 'ea2bea8905bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO users (
            id,
            username,
            email,
            hashed_password,
            first_name,
            last_name,
            dob,
            gender,
            profile_image,
            description,
            is_admin,
            source_id
        ) VALUES (
            1,
            'admin_Events',
            'admin@example.com',
            '$2b$12$4a91cux50C/oVwBfSwsWs.aSEOM/MgjGziX22/ZKtMFDfq4ASNWHG',
            'Admin',
            NULL,
            NULL,
            'not_specified',
            NULL,
            'Administrator user',
            TRUE,
            1
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM users WHERE username = 'admin_Events';
        """
    )
