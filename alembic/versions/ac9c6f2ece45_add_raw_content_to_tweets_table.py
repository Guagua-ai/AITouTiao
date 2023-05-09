"""add raw content to tweets table

Revision ID: ac9c6f2ece45
Revises: 10d17405f968
Create Date: 2023-05-09 03:07:30.572885

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ac9c6f2ece45'
down_revision = '10d17405f968'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tweets', sa.Column(
        'raw_content', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('tweets', 'raw_content')
