"""empty message

Revision ID: 20b7d2bfd7b9
Revises: bf85affa4ad3
Create Date: 2019-11-26 22:14:21.904801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20b7d2bfd7b9'
down_revision = 'bf85affa4ad3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_passwd', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_passwd', 'user', ['passwd'], unique=False)
    # ### end Alembic commands ###
