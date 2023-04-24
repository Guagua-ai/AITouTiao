"""create twitter user table

Revision ID: 7ef180efbf19
Revises: 2fb4327bb1c3
Create Date: 2023-04-24 00:44:39.596676

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7ef180efbf19'
down_revision = '2fb4327bb1c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('twitter_users',
                    sa.Column('id', sa.INTEGER(),
                              autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.INTEGER(),
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
    pass
