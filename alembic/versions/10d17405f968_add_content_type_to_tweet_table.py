"""add content type to tweet table

Revision ID: 10d17405f968
Revises: fe87c99b8df1
Create Date: 2023-04-26 22:00:52.111836

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '10d17405f968'
down_revision = 'fe87c99b8df1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # add the content_type column to the tweet table
    op.add_column('tweets', sa.Column('content_type', sa.String(), nullable=True))

    # backfill the content_type column with text
    op.execute("UPDATE tweets SET content_type='text'")

    # set the content_type column to not nullable
    op.alter_column('tweets', 'content_type', nullable=False)


def downgrade() -> None:
    # drop the content_type column from the tweet table
    op.drop_column('tweets', 'content_type')