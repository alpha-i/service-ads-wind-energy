"""empty message

Revision ID: 776de775357e
Revises: 677d78323388
Create Date: 2018-05-15 12:04:11.980859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '776de775357e'
down_revision = '677d78323388'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('detection_result', sa.Column('upload_code', sa.String(length=60), nullable=True))
    op.drop_constraint('detection_result_task_code_key', 'detection_result', type_='unique')
    op.create_unique_constraint(None, 'detection_result', ['upload_code'])
    op.drop_column('detection_result', 'task_code')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('detection_result', sa.Column('task_code', sa.VARCHAR(length=60), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'detection_result', type_='unique')
    op.create_unique_constraint('detection_result_task_code_key', 'detection_result', ['task_code'])
    op.drop_column('detection_result', 'upload_code')
    # ### end Alembic commands ###