"""Add children table

Revision ID: 99cf4e8d3edf
Revises: 984aa22be0f8
Create Date: 2023-03-09 10:49:09.145221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99cf4e8d3edf'
down_revision = '984aa22be0f8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('city', sa.String(), nullable=True))
    op.add_column('users', sa.Column('paid', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('subscription_end', sa.DateTime(), nullable=True))
    op.drop_column('users', 'telegram_chat_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('telegram_chat_id', sa.VARCHAR(), nullable=False))
    op.drop_column('users', 'subscription_end')
    op.drop_column('users', 'paid')
    op.drop_column('users', 'city')
    # ### end Alembic commands ###
