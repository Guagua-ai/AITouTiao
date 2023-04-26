"""Add visibility column to Tweet

Revision ID: fe87c99b8df1
Revises: d6424f8c661f
Create Date: 2023-04-26 03:14:26.439713

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fe87c99b8df1'
down_revision = 'd6424f8c661f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add the column with a temporary default value
    op.add_column('tweets', sa.Column('visibility', sa.String(), nullable=True, server_default='private'))

    # Step 2: Backfill the existing rows with the desired default value
    op.execute("UPDATE tweets SET visibility = 'public';")

    # Step 3: Alter the column to set the desired default value and make it non-nullable
    op.alter_column('tweets', 'visibility', nullable=False, server_default='private')


def downgrade() -> None:
    pass
