"""Add date_posted to Post model

Revision ID: 6096d4b57956
Revises: 52b8a04a9c9a
Create Date: 2024-11-11 19:00:58.594087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6096d4b57956'
down_revision = '52b8a04a9c9a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('date_posted')

    # ### end Alembic commands ###
