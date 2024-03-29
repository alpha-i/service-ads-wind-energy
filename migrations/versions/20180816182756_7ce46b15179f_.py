"""empty message

Revision ID: 7ce46b15179f
Revises: 665ca9748b1b
Create Date: 2018-08-16 18:27:56.175788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ce46b15179f'
down_revision = '665ca9748b1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'company', ['name'])
    op.create_unique_constraint('unique_user_in_company', 'user', ['email', 'company_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_user_in_company', 'user', type_='unique')
    op.drop_constraint(None, 'company', type_='unique')
    # ### end Alembic commands ###
