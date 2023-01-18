"""Add category column to ratingitem

Revision ID: e7c24ae46946
Revises: caa21930c35b
Create Date: 2023-01-17 18:48:47.040253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7c24ae46946'
down_revision = 'caa21930c35b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rating_items', sa.Column('category', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rating_items', 'category')
    # ### end Alembic commands ###
