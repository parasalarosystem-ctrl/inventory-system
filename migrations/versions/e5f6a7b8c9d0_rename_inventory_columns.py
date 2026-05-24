"""Rename inventory columns to match product-oriented naming

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-24

Renames:
  item_description   -> product_name
  estimated_useful_life -> unit
  receipt_qty        -> quantity
  amount             -> selling_price
  reorder_point      -> restock_threshold
  date               -> expiry_date
  image_filename     -> product_image
"""
from alembic import op
from sqlalchemy import inspect


revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def _existing_indexes(conn, table):
    return {ix['name'] for ix in inspect(conn).get_indexes(table)}


def upgrade():
    conn = op.get_bind()

    op.alter_column('inventory', 'item_description',    new_column_name='product_name')
    op.alter_column('inventory', 'estimated_useful_life', new_column_name='unit')
    op.alter_column('inventory', 'receipt_qty',         new_column_name='quantity')
    op.alter_column('inventory', 'amount',              new_column_name='selling_price')
    op.alter_column('inventory', 'reorder_point',       new_column_name='restock_threshold')
    op.alter_column('inventory', 'date',                new_column_name='expiry_date')
    op.alter_column('inventory', 'image_filename',      new_column_name='product_image')

    # Rename the two indexes whose column names changed
    existing = _existing_indexes(conn, 'inventory')
    if 'ix_inventory_item_description' in existing:
        op.execute('ALTER INDEX ix_inventory_item_description RENAME TO ix_inventory_product_name')
    if 'ix_inventory_date' in existing:
        op.execute('ALTER INDEX ix_inventory_date RENAME TO ix_inventory_expiry_date')


def downgrade():
    conn = op.get_bind()

    op.alter_column('inventory', 'product_name',      new_column_name='item_description')
    op.alter_column('inventory', 'unit',              new_column_name='estimated_useful_life')
    op.alter_column('inventory', 'quantity',          new_column_name='receipt_qty')
    op.alter_column('inventory', 'selling_price',     new_column_name='amount')
    op.alter_column('inventory', 'restock_threshold', new_column_name='reorder_point')
    op.alter_column('inventory', 'expiry_date',       new_column_name='date')
    op.alter_column('inventory', 'product_image',     new_column_name='image_filename')

    existing = _existing_indexes(conn, 'inventory')
    if 'ix_inventory_product_name' in existing:
        op.execute('ALTER INDEX ix_inventory_product_name RENAME TO ix_inventory_item_description')
    if 'ix_inventory_expiry_date' in existing:
        op.execute('ALTER INDEX ix_inventory_expiry_date RENAME TO ix_inventory_date')
