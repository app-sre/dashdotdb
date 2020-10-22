"""New Tables

Revision ID: f2ced20babab
Revises: e6210176f55c
Create Date: 2020-10-22 02:51:24.638927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2ced20babab'
down_revision = 'e6210176f55c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dvcluster',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('objectkind',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('validation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('validationtoken',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dvnamespace',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('cluster_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cluster_id'], ['dvcluster.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deploymentvalidation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('token_id', sa.Integer(), nullable=True),
    sa.Column('namespace_id', sa.Integer(), nullable=True),
    sa.Column('objectkind_id', sa.Integer(), nullable=True),
    sa.Column('validation_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['namespace_id'], ['dvnamespace.id'], ),
    sa.ForeignKeyConstraint(['objectkind_id'], ['objectkind.id'], ),
    sa.ForeignKeyConstraint(['token_id'], ['validationtoken.id'], ),
    sa.ForeignKeyConstraint(['validation_id'], ['validation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('deploymentvalidation')
    op.drop_table('dvnamespace')
    op.drop_table('validationtoken')
    op.drop_table('validation')
    op.drop_table('objectkind')
    op.drop_table('dvcluster')
    # ### end Alembic commands ###