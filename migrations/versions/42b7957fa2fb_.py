"""empty message

Revision ID: 42b7957fa2fb
Revises: ec19284d4dbd
Create Date: 2021-05-31 13:05:28.749925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42b7957fa2fb'
down_revision = 'ec19284d4dbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'first_name_ar')
    op.drop_column('users', 'last_name_ar')
    # ### end Alembic commands ###
    


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_name_ar', sa.VARCHAR(), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('first_name_ar', sa.VARCHAR(), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
    