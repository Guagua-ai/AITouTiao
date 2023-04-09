"""add created_at to tweet table

Revision ID: 5608949cbcce
Revises: 6b6d731d4208
Create Date: 2023-04-08 20:15:38.328633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5608949cbcce'
down_revision = '6b6d731d4208'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tweets', sa.Column('created_at', sa.DateTime))


def downgrade() -> None:
    pass
