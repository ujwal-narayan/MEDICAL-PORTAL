"""User table

Revision ID: 55e4fad9f431
Revises: 
Create Date: 2018-04-26 15:41:41.997108

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55e4fad9f431'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.Column('usertype', sa.Integer(), nullable=True),
    sa.Column('password', sa.String(length=80), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('dayavail', sa.String(length=128), nullable=True),
    sa.Column('day_avail_s', sa.String(length=128), nullable=True),
    sa.Column('starttime', sa.String(length=80), nullable=True),
    sa.Column('endtime', sa.String(length=80), nullable=True),
    sa.Column('hospital', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('appointments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=140), nullable=True),
    sa.Column('slot', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_timestamp'), 'appointments', ['timestamp'], unique=False)
    op.create_table('bank_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('bankname', sa.String(length=80), nullable=True),
    sa.Column('ifsc', sa.String(length=80), nullable=True),
    sa.Column('acctname', sa.String(length=80), nullable=True),
    sa.Column('acctnum', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patint_health_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.String(length=80), nullable=True),
    sa.Column('allergym', sa.String(length=255), nullable=True),
    sa.Column('bpsys', sa.Integer(), nullable=True),
    sa.Column('bpdia', sa.Integer(), nullable=True),
    sa.Column('heartbeat', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reimbdata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('brno', sa.String(length=80), nullable=True),
    sa.Column('date', sa.String(length=80), nullable=True),
    sa.Column('amount', sa.String(length=128), nullable=True),
    sa.Column('status', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reimbdata')
    op.drop_table('patint_health_record')
    op.drop_table('bank_info')
    op.drop_index(op.f('ix_appointments_timestamp'), table_name='appointments')
    op.drop_table('appointments')
    op.drop_table('user')
    # ### end Alembic commands ###
