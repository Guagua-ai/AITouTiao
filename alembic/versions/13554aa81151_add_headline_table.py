"""Add headline table

Revision ID: 13554aa81151
Revises: ac9c6f2ece45
Create Date: 2023-05-28 19:16:31.537321

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '13554aa81151'
down_revision = 'ac9c6f2ece45'
branch_labels = None
depends_on = None


def upgrade() -> None:
    check_if_table_exists_and_drop('headliners')

    op.create_table('headliners', 
                    sa.Column('id', sa.Integer(), nullable=False), 
                    sa.Column('tweet_id', sa.Integer(), nullable=False), 
                    sa.Column('title', sa.String(), nullable=True), 
                    sa.Column('image_url', sa.String(), nullable=True), 
                    sa.Column('published_at', sa.DateTime(), nullable=True), 
                    sa.Column('created_at', sa.DateTime(), nullable=True), 
                    sa.ForeignKeyConstraint(['tweet_id'], ['tweets.id'], ), 
                    sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('tweet_id'))


def downgrade() -> None:
    check_if_table_exists_and_drop('headliners')


def check_if_table_exists_and_drop(table_name):
    connection = op.get_bind()
    inspector = Inspector.from_engine(connection)
    if table_name in inspector.get_table_names():
        op.drop_table(table_name)