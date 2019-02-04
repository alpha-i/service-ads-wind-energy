"""empty message

Revision ID: 0038de4762fe
Revises: e365092ae0c0
Create Date: 2018-09-19 12:28:20.436556

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0038de4762fe'
down_revision = 'e365092ae0c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('healthscore')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('healthscore',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('turbine_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('component_code', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('value', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('source_prediction_id', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='healthscore_company_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='healthscore_pkey')
    )
    # ### end Alembic commands ###
