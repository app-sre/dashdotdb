"""empty message

Revision ID: c18e90484e36
Revises: 248a30ecba33
Create Date: 2023-09-15 08:25:10.687747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c18e90484e36'
down_revision = '248a30ecba33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('doradeployment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('trigger_reason', sa.String(length=256), nullable=True),
    sa.Column('finish_timestamp', sa.DateTime(), nullable=True),
    sa.Column('app_name', sa.String(length=256), nullable=True),
    sa.Column('env_name', sa.String(length=256), nullable=True),
    sa.Column('pipeline', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('app_name', 'env_name', 'pipeline', 'trigger_reason', name='doradeployment_trigger_reason_app_name_env_name_pipeline_uc')
    )
    op.create_index(op.f('ix_doradeployment_app_name'), 'doradeployment', ['app_name'], unique=False)
    op.create_index(op.f('ix_doradeployment_env_name'), 'doradeployment', ['env_name'], unique=False)
    op.create_index(op.f('ix_doradeployment_finish_timestamp'), 'doradeployment', ['finish_timestamp'], unique=False)
    op.create_index(op.f('ix_doradeployment_pipeline'), 'doradeployment', ['pipeline'], unique=False)
    op.create_index(op.f('ix_doradeployment_trigger_reason'), 'doradeployment', ['trigger_reason'], unique=False)
    op.create_table('doracommit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deployment_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('revision', sa.String(length=40), nullable=True),
    sa.Column('repo', sa.String(length=256), nullable=True),
    sa.Column('lttc', sa.Interval(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_id'], ['doradeployment.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('deployment_id', 'revision', 'repo', name='doracommit_depid_rev_repo_uc')
    )
    op.create_index(op.f('ix_doracommit_deployment_id'), 'doracommit', ['deployment_id'], unique=False)
    op.create_index(op.f('ix_doracommit_timestamp'), 'doracommit', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_doracommit_timestamp'), table_name='doracommit')
    op.drop_index(op.f('ix_doracommit_deployment_id'), table_name='doracommit')
    op.drop_table('doracommit')
    op.drop_index(op.f('ix_doradeployment_trigger_reason'), table_name='doradeployment')
    op.drop_index(op.f('ix_doradeployment_pipeline'), table_name='doradeployment')
    op.drop_index(op.f('ix_doradeployment_finish_timestamp'), table_name='doradeployment')
    op.drop_index(op.f('ix_doradeployment_env_name'), table_name='doradeployment')
    op.drop_index(op.f('ix_doradeployment_app_name'), table_name='doradeployment')
    op.drop_table('doradeployment')
    # ### end Alembic commands ###
