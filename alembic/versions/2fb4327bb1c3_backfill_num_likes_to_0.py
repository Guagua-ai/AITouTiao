"""Backfill num_likes to 0

Revision ID: 2fb4327bb1c3
Revises: e4f778ebcc68
Create Date: 2023-04-23 17:41:47.663326

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2fb4327bb1c3'
down_revision = 'e4f778ebcc68'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Backfill num_likes to 0
    op.execute("UPDATE tweets SET num_likes = 0 WHERE num_likes IS NULL")


def downgrade() -> None:
    op.execute("UPDATE tweets SET num_likes = NULL WHERE num_likes = 0")
