"""change type of user_id field in twitter_users

Revision ID: a583899ca05a
Revises: 7ef180efbf19
Create Date: 2023-04-24 01:55:56.931266

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a583899ca05a'
down_revision = '7ef180efbf19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('twitter_users',
                    sa.Column('id', sa.INTEGER(),
                              autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('username', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('display_name', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.Column('profile_image_url', sa.VARCHAR(),
                              autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='twitter_users_pkey')
                    )


def downgrade() -> None:
    op.drop_table('twitter_users')
