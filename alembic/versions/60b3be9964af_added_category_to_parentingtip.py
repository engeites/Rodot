"""Added category to ParentingTip

Revision ID: 60b3be9964af
Revises: 160326627624
Create Date: 2023-04-03 14:34:53.679366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60b3be9964af'
down_revision = '160326627624'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'daily_tips', ['header'])
    op.add_column('parenting_tips', sa.Column('category', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parenting_tips', 'category')
    op.drop_constraint(None, 'daily_tips', type_='unique')
    # ### end Alembic commands ###
