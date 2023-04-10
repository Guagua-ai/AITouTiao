"""add created_at to tweet table

Revision ID: 5608949cbcce
Revises: 6b6d731d4208
Create Date: 2023-04-08 20:15:38.328633

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '5608949cbcce'
down_revision = '6b6d731d4208'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('tweets')


def downgrade() -> None:
    op.create_table('tweets',
                    sa.Column('id', sa.INTEGER(),
                              autoincrement=True, nullable=False),
                    sa.Column('source_id', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('source_name', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('author', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('title', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('url', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('url_to_image', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('published_at', postgresql.TIMESTAMP(),
                              autoincrement=False, nullable=True),
                    sa.Column('content', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.column('created_at', postgresql.TIMESTAMP(),
                              autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='tweets_pkey'),
                    sa.UniqueConstraint('url', name='tweets_url_key')
                    )
