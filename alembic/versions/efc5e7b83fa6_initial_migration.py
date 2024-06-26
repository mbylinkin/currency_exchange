"""Initial migration

Revision ID: efc5e7b83fa6
Revises:
Create Date: 2024-04-28 20:54:39.109806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efc5e7b83fa6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=3), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('sign', sa.String(length=1), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('currency_pkey')),
    sa.UniqueConstraint('code', name='currency_code_idx')
    )
    op.create_index(op.f('currency_id_idx'), 'currency', ['id'], unique=False)
    op.create_table('exchange_rates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('base_currency_id', sa.Integer(), nullable=True),
    sa.Column('target_currency_id', sa.Integer(), nullable=True),
    sa.Column('rate', sa.DECIMAL(precision=10, scale=6), nullable=True),
    sa.ForeignKeyConstraint(['base_currency_id'], ['currency.id'], name=op.f('exchange_rates_base_currency_id_fkey')),
    sa.ForeignKeyConstraint(['target_currency_id'], ['currency.id'], name=op.f('exchange_rates_target_currency_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('exchange_rates_pkey')),
    sa.UniqueConstraint('base_currency_id', 'target_currency_id', name='base_target_currency_idx')
    )
    op.create_index(op.f('exchange_rates_id_idx'), 'exchange_rates', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('exchange_rates_id_idx'), table_name='exchange_rates')
    op.drop_table('exchange_rates')
    op.drop_index(op.f('currency_id_idx'), table_name='currency')
    op.drop_table('currency')
    # ### end Alembic commands ###
