"""empty message

Revision ID: 9d64fd56c7e4
Revises: 963bd51e139c
Create Date: 2023-01-11 14:24:27.047343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d64fd56c7e4'
down_revision = '963bd51e139c'
branch_labels = None
depends_on = None


def upgrade():
    # Alembic does not alter the varchar(64) change - need to do this manually here
    op.execute('ALTER TABLE image ALTER COLUMN name TYPE varchar(128);')


def downgrade():
    # Alembic does not alter the varchar(64) change - need to do this manually here
    op.execute('ALTER TABLE image ALTER COLUMN name TYPE varchar(64);')
