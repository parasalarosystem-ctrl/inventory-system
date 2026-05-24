"""Drop property_no, officer, position from inventory

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-24

These columns are not needed by the system and have been removed from
the model and all application code.
"""
from alembic import op
from sqlalchemy import inspect


revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def _existing_columns(conn, table):
    return [c['name'] for c in inspect(conn).get_columns(table)]


def upgrade():
    conn = op.get_bind()
    cols = _existing_columns(conn, 'inventory')
    for col in ('property_no', 'officer', 'position'):
        if col in cols:
            op.drop_column('inventory', col)


def downgrade():
    import sqlalchemy as sa
    conn = op.get_bind()
    cols = _existing_columns(conn, 'inventory')
    for col, typ in [
        ('property_no', sa.String(50)),
        ('officer',     sa.String(100)),
        ('position',    sa.String(100)),
    ]:
        if col not in cols:
            op.add_column('inventory', sa.Column(col, typ, nullable=True))
