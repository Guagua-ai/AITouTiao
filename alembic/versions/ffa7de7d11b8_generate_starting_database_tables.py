"""Generate starting database tables

Revision ID: ffa7de7d11b8
Revises: 
Create Date: 2023-04-09 21:58:47.919180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ffa7de7d11b8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('collections')
    op.drop_table('tweets')
    op.drop_table('view_history')
    op.drop_table('collections_tweets')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('role', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('quota', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('profile_image', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('email', name='users_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('collections_tweets',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('collection_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('tweet_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], name='collections_tweets_collection_id_fkey'),
    sa.ForeignKeyConstraint(['tweet_id'], ['tweets.id'], name='collections_tweets_tweet_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='collections_tweets_pkey')
    )
    op.create_table('view_history',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='view_history_pkey'),
    sa.UniqueConstraint('user_id', 'post_id', 'timestamp', name='view_history_user_id_post_id_timestamp_key')
    )
    op.create_table('tweets',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('source_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('author', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('url_to_image', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('published_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='tweets_pkey'),
    sa.UniqueConstraint('url', name='tweets_url_key')
    )
    op.create_table('collections',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('last_accessed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='collections_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='collections_pkey'),
    sa.UniqueConstraint('name', name='collections_name_key')
    )
    # ### end Alembic commands ###
