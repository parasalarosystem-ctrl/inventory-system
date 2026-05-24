"""Add indexes for transaction and inventory query performance

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-24

Indexes added:
  inventory          — (is_deleted, status), category_id, item_description, date, balance
  disposal_history   — inventory_id, event_date, event_type
  borrowing          — inventory_id, status
  audit_log          — timestamp
  pos_transaction    — created_at
  pos_transaction_item — transaction_id, inventory_id
"""
from alembic import op
from sqlalchemy import inspect


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def _existing_indexes(conn, table):
    return {ix['name'] for ix in inspect(conn).get_indexes(table)}


def create_if_missing(conn, name, table, columns, **kwargs):
    if name not in _existing_indexes(conn, table):
        op.create_index(name, table, columns, **kwargs)


def upgrade():
    conn = op.get_bind()

    # ── inventory ────────────────────────────────────────────────────────
    create_if_missing(conn, 'ix_inventory_deleted_status',  'inventory', ['is_deleted', 'status'])
    create_if_missing(conn, 'ix_inventory_category_id',     'inventory', ['category_id'])
    create_if_missing(conn, 'ix_inventory_item_description','inventory', ['item_description'])
    create_if_missing(conn, 'ix_inventory_date',            'inventory', ['date'])
    create_if_missing(conn, 'ix_inventory_balance',         'inventory', ['balance'])

    # ── disposal_history ─────────────────────────────────────────────────
    create_if_missing(conn, 'ix_disposal_history_inventory_id', 'disposal_history', ['inventory_id'])
    create_if_missing(conn, 'ix_disposal_history_event_date',   'disposal_history', ['event_date'])
    create_if_missing(conn, 'ix_disposal_history_event_type',   'disposal_history', ['event_type'])

    # ── borrowing ────────────────────────────────────────────────────────
    create_if_missing(conn, 'ix_borrowing_inventory_id', 'borrowing', ['inventory_id'])
    create_if_missing(conn, 'ix_borrowing_status',       'borrowing', ['status'])

    # ── audit_log ────────────────────────────────────────────────────────
    create_if_missing(conn, 'ix_audit_log_timestamp', 'audit_log', ['timestamp'])

    # ── pos_transaction ──────────────────────────────────────────────────
    create_if_missing(conn, 'ix_pos_transaction_created_at', 'pos_transaction', ['created_at'])

    # ── pos_transaction_item ─────────────────────────────────────────────
    create_if_missing(conn, 'ix_pos_transaction_item_transaction_id', 'pos_transaction_item', ['transaction_id'])
    create_if_missing(conn, 'ix_pos_transaction_item_inventory_id',   'pos_transaction_item', ['inventory_id'])


def downgrade():
    indexes = [
        ('ix_inventory_deleted_status',               'inventory'),
        ('ix_inventory_category_id',                  'inventory'),
        ('ix_inventory_item_description',             'inventory'),
        ('ix_inventory_date',                         'inventory'),
        ('ix_inventory_balance',                      'inventory'),
        ('ix_disposal_history_inventory_id',          'disposal_history'),
        ('ix_disposal_history_event_date',            'disposal_history'),
        ('ix_disposal_history_event_type',            'disposal_history'),
        ('ix_borrowing_inventory_id',                 'borrowing'),
        ('ix_borrowing_status',                       'borrowing'),
        ('ix_audit_log_timestamp',                    'audit_log'),
        ('ix_pos_transaction_created_at',             'pos_transaction'),
        ('ix_pos_transaction_item_transaction_id',    'pos_transaction_item'),
        ('ix_pos_transaction_item_inventory_id',      'pos_transaction_item'),
    ]
    conn = op.get_bind()
    for name, table in indexes:
        if name in _existing_indexes(conn, table):
            op.drop_index(name, table_name=table)
