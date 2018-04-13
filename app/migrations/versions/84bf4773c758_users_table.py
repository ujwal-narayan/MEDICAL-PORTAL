"""users table

Revision ID: 84bf4773c758
Revises: 43db25fba480
Create Date: 2018-04-13 18:48:27.899644

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84bf4773c758'
down_revision = '43db25fba480'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('usertype', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'usertype')
    # ### end Alembic commands ###