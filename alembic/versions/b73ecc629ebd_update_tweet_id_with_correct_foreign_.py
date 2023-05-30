"""Update tweet_id with correct foreign key setting.

Revision ID: b73ecc629ebd
Revises: 13554aa81151
Create Date: 2023-05-29 23:20:25.145844

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'b73ecc629ebd'
down_revision = '13554aa81151'
branch_labels = None
depends_on = None


def upgrade() -> None:
    check_if_table_exists_and_drop('headliners')
    
    op.create_table('headliners',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('tweet_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('image_url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('published_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['tweet_id'], ['tweets.id'], name='headliners_tweet_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='headliners_pkey'),
    sa.UniqueConstraint('tweet_id', name='headliners_tweet_id_key'))


def downgrade() -> None:
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


def check_if_table_exists_and_drop(table_name):
    connection = op.get_bind()
    inspector = Inspector.from_engine(connection)
    if table_name in inspector.get_table_names():
        op.drop_table(table_name)