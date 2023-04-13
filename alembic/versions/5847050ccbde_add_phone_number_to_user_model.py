"""add phone number to user model

Revision ID: 5847050ccbde
Revises: 4ddee0f26034
Create Date: 2023-04-13 00:57:07.839875

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5847050ccbde'
down_revision = '4ddee0f26034'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))

def downgrade() -> None:
    pass
