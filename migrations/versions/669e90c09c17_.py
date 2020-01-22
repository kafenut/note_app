"""empty message

Revision ID: 669e90c09c17
Revises: 99eca89cebc7
Create Date: 2019-10-17 22:54:06.521381

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '669e90c09c17'
down_revision = '99eca89cebc7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Follow',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.drop_table('follow')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follow',
    sa.Column('follower_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('followed_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], name='follow_ibfk_1'),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], name='follow_ibfk_2'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('Follow')
    # ### end Alembic commands ###
