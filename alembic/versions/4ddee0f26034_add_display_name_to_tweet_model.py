"""add display name to tweet model

Revision ID: 4ddee0f26034
Revises: ffa7de7d11b8
Create Date: 2023-04-12 21:59:47.642879

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4ddee0f26034'
down_revision = 'ffa7de7d11b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tweets', sa.Column('display_name', sa.VARCHAR(), autoincrement=False, nullable=True))


def downgrade() -> None:
    pass
