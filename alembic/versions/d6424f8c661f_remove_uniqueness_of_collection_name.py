"""remove uniqueness of collection name

Revision ID: d6424f8c661f
Revises: a583899ca05a
Create Date: 2023-04-24 22:37:12.417419

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd6424f8c661f'
down_revision = 'a583899ca05a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('collections_name_key', 'collections', type_='unique')


def downgrade() -> None:
    pass
