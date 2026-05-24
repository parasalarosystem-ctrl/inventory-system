"""Add missing inventory columns: property_no, officer, position

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-24

These columns exist in the model but were never created in the PostgreSQL
database (the DB was originally seeded via db.create_all() before the model
included them, or they were skipped during normalization).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def _existing_columns(conn, table):
    return [c['name'] for c in inspect(conn).get_columns(table)]


def upgrade():
    conn = op.get_bind()
    cols = _existing_columns(conn, 'inventory')

    if 'property_no' not in cols:
        op.add_column('inventory', sa.Column('property_no', sa.String(50), nullable=True))

    if 'officer' not in cols:
        op.add_column('inventory', sa.Column('officer', sa.String(100), nullable=True))

    if 'position' not in cols:
        op.add_column('inventory', sa.Column('position', sa.String(100), nullable=True))


def downgrade():
    conn = op.get_bind()
    cols = _existing_columns(conn, 'inventory')

    for col in ('property_no', 'officer', 'position'):
        if col in cols:
            op.drop_column('inventory', col)
