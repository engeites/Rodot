"""added new models: Media and DailyTip

Revision ID: 327df5e49e0c
Revises: f692f1a304c6
Create Date: 2023-03-28 20:09:48.674811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '327df5e49e0c'
down_revision = 'f692f1a304c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'users', ['telegram_user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    # ### end Alembic commands ###
