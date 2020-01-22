"""empty message

Revision ID: bf85affa4ad3
Revises: dd9e6651efa2
Create Date: 2019-11-26 22:13:45.517003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf85affa4ad3'
down_revision = 'dd9e6651efa2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_role', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_role', 'user', ['role'], unique=False)
    # ### end Alembic commands ###
