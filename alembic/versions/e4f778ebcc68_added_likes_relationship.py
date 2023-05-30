"""Added likes relationship

Revision ID: e4f778ebcc68
Revises: 5847050ccbde
Create Date: 2023-04-22 16:48:05.711077

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e4f778ebcc68'
down_revision = '5847050ccbde'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add likes relationship
    op.create_table('likes',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('tweet_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['tweet_id'], ['tweets.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'))
    op.add_column('tweets', sa.Column(
        'num_likes', sa.Integer(), nullable=True))
    op.add_column('collections', sa.Column(
        'last_accesss_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_likes_tweet_id'), 'likes', ['tweet_id'], unique=False)
    op.create_index(op.f('ix_likes_user_id'), 'likes', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop likes relationship
    op.drop_index(op.f('ix_likes_user_id'), table_name='likes')
    op.drop_index(op.f('ix_likes_tweet_id'), table_name='likes')
    op.drop_column('collections', 'last_accesss_at')
    op.drop_column('tweets', 'num_likes')
    op.drop_table('likes')
