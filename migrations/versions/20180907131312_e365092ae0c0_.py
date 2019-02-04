"""empty message

Revision ID: e365092ae0c0
Revises: 9265739eb1bd
Create Date: 2018-09-07 13:13:12.688222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e365092ae0c0'
down_revision = '9265739eb1bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('variablehealth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_update', sa.DateTime(timezone=True), nullable=True),
    sa.Column('group_variable_id', sa.String(), nullable=False),
    sa.Column('group_variable_name', sa.String(), nullable=False),
    sa.Column('component_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['component_id'], ['componenthealth.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_variablehealth_created_at'), 'variablehealth', ['created_at'], unique=False)
    op.create_index(op.f('ix_variablehealth_last_update'), 'variablehealth', ['last_update'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_variablehealth_last_update'), table_name='variablehealth')
    op.drop_index(op.f('ix_variablehealth_created_at'), table_name='variablehealth')
    op.drop_table('variablehealth')
    # ### end Alembic commands ###
