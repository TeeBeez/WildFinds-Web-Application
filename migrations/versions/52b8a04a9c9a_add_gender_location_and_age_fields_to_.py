"""Add gender, location, and age fields to User model

Revision ID: 52b8a04a9c9a
Revises: 
Create Date: 2024-10-25 22:54:57.616351

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '52b8a04a9c9a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gender', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=True))
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=128),
               type_=sa.String(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=128),
               existing_nullable=True)
        batch_op.drop_column('age')
        batch_op.drop_column('location')
        batch_op.drop_column('gender')

    # ### end Alembic commands ###
