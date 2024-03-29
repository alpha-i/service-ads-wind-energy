"""empty message

Revision ID: c92171f20895
Revises: 7044412b9b93
Create Date: 2018-10-31 09:07:13.684234

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c92171f20895'
down_revision = '7044412b9b93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('diagnostic_result')
    op.drop_table('diagnostic_task_status')
    op.drop_table('diagnostic_task')

    op.drop_table('detection_result')
    op.drop_table('detection_task_status')
    op.drop_table('detection_task')

    op.drop_table('datasources_to_training_task')
    op.drop_table('training_task_status')
    op.drop_table('training_task')
    op.drop_table('task')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('detection_result',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('detection_task_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('upload_code', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
    sa.Column('task_code', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='detection_result_company_id_fkey'),
    sa.ForeignKeyConstraint(['detection_task_id'], ['detection_task.id'], name='detection_result_detection_task_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='detection_result_pkey')
    )
    op.create_table('training_task',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('training_task_id_seq'::regclass)"), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('datasource_configuration_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('company_configuration_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('task_code', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('configuration', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('parent_training_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['company_configuration_id'], ['company_configuration.id'], name='training_task_company_configuration_id_fkey'),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='training_task_company_id_fkey'),
    sa.ForeignKeyConstraint(['datasource_configuration_id'], ['data_source_configuration.id'], name='training_task_datasource_configuration_id_fk'),
    sa.ForeignKeyConstraint(['parent_training_id'], ['training_task.id'], name='training_task_parent_training_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='training_task_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='training_task_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('task',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('type', postgresql.ENUM('TRAINING', 'DETECTION', 'DIAGNOSTIC', name='tasktypes'), autoincrement=False, nullable=True),
    sa.Column('task_code', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='task_pkey')
    )
    op.create_table('datasources_to_training_task',
    sa.Column('training_task_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('data_source_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['data_source_id'], ['data_source.id'], name='datasources_to_training_task_data_source_id_fkey'),
    sa.ForeignKeyConstraint(['training_task_id'], ['training_task.id'], name='datasources_to_training_task_training_task_id_fkey')
    )
    op.create_table('diagnostic_task',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('diagnostic_task_id_seq'::regclass)"), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('detection_task_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datasource_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upload_code', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('task_code', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='diagnostic_task_company_id_fkey'),
    sa.ForeignKeyConstraint(['datasource_id'], ['data_source.id'], name='diagnostic_task_datasource_id_fkey'),
    sa.ForeignKeyConstraint(['detection_task_id'], ['detection_task.id'], name='diagnostic_task_detection_task_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='diagnostic_task_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('training_task_status',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('training_task_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('message', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['training_task_id'], ['training_task.id'], name='training_task_status_training_task_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='training_task_status_pkey')
    )
    op.create_table('detection_task_status',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('detection_task_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('message', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['detection_task_id'], ['detection_task.id'], name='detection_task_status_detection_task_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='detection_task_status_pkey')
    )
    op.create_table('diagnostic_result',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('upload_code', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
    sa.Column('task_code', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
    sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('diagnostic_task_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='diagnostic_result_company_id_fkey'),
    sa.ForeignKeyConstraint(['diagnostic_task_id'], ['diagnostic_task.id'], name='diagnostic_result_diagnostic_task_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='diagnostic_result_pkey')
    )
    op.create_table('diagnostic_task_status',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('diagnostic_task_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('message', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['diagnostic_task_id'], ['diagnostic_task.id'], name='diagnostic_task_status_diagnostic_task_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='diagnostic_task_status_pkey')
    )
    op.create_table('detection_task',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('last_update', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('datasource_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('upload_code', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('configuration_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('task_code', sa.VARCHAR(length=60), autoincrement=False, nullable=False),
    sa.Column('training_task_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='detection_task_company_id_fkey'),
    sa.ForeignKeyConstraint(['configuration_id'], ['company_configuration.id'], name='detection_task_configuration_id_fkey'),
    sa.ForeignKeyConstraint(['datasource_id'], ['data_source.id'], name='detection_task_datasource_id_fkey'),
    sa.ForeignKeyConstraint(['training_task_id'], ['training_task.id'], name='detection_task_training_task_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='detection_task_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='detection_task_pkey')
    )
    # ### end Alembic commands ###
