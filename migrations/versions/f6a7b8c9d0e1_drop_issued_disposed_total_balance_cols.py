"""Drop issued_qty, disposed_qty, total, balance, total_balance_amount columns

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-24

quantity is now the single source of truth for current stock on hand.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def _existing_indexes(conn, table):
    return {ix['name'] for ix in inspect(conn).get_indexes(table)}


def upgrade():
    conn = op.get_bind()
    existing = _existing_indexes(conn, 'inventory')

    if 'ix_inventory_balance' in existing:
        op.drop_index('ix_inventory_balance', table_name='inventory')

    op.drop_column('inventory', 'issued_qty')
    op.drop_column('inventory', 'disposed_qty')
    op.drop_column('inventory', 'total')
    op.drop_column('inventory', 'balance')
    op.drop_column('inventory', 'total_balance_amount')

    if 'ix_inventory_quantity' not in existing:
        op.create_index('ix_inventory_quantity', 'inventory', ['quantity'])


def downgrade():
    op.add_column('inventory', sa.Column('total_balance_amount', sa.Float(), nullable=True))
    op.add_column('inventory', sa.Column('balance', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('inventory', sa.Column('total', sa.Float(), nullable=True))
    op.add_column('inventory', sa.Column('disposed_qty', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('inventory', sa.Column('issued_qty', sa.Integer(), nullable=True))
    op.create_index('ix_inventory_balance', 'inventory', ['balance'])
    op.drop_index('ix_inventory_quantity', table_name='inventory')
