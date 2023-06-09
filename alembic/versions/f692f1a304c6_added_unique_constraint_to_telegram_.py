"""added unique constraint to telegram_user_id in User model

Revision ID: f692f1a304c6
Revises: bb3482c98204
Create Date: 2023-03-23 13:18:50.165788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f692f1a304c6'
down_revision = 'bb3482c98204'
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
