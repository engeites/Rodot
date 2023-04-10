"""added Advice model

Revision ID: 160326627624
Revises: e142dd926d79
Create Date: 2023-04-01 21:11:20.534336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '160326627624'
down_revision = 'e142dd926d79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'daily_tips', ['header'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'daily_tips', type_='unique')
    # ### end Alembic commands ###