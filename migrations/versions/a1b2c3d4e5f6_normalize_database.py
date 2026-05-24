"""Normalize database: Category table, remove redundant Inventory columns, drop HistoryLog

Revision ID: a1b2c3d4e5f6
Revises: cba1e127601f
Create Date: 2026-05-24

Changes:
  - Ensure `category` table exists
  - Add `category_id` FK to `inventory`
  - Migrate existing undertaking_property strings into `category` rows
  - Drop redundant columns from `inventory`:
      undertaking_property, borrower_name, date_borrowed,
      disposal_date, disposal_reason
  - Drop unused `history_log` table (superseded by disposal_history)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect


revision = 'a1b2c3d4e5f6'
down_revision = 'cba1e127601f'
branch_labels = None
depends_on = None


def _existing_tables(conn):
    return inspect(conn).get_table_names()


def _existing_columns(conn, table):
    return [c['name'] for c in inspect(conn).get_columns(table)]


def upgrade():
    conn = op.get_bind()

    # 1. Create category table only if it doesn't exist yet
    if 'category' not in _existing_tables(conn):
        op.create_table(
            'category',
            sa.Column('id',   sa.Integer(),   nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'),
        )

    # 2. Add category_id to inventory if missing
    if 'category_id' not in _existing_columns(conn, 'inventory'):
        op.add_column('inventory', sa.Column('category_id', sa.Integer(), nullable=True))

    # 3. Seed Category from distinct undertaking_property values
    if 'undertaking_property' in _existing_columns(conn, 'inventory'):
        rows = conn.execute(
            text("""
                SELECT DISTINCT undertaking_property
                FROM inventory
                WHERE undertaking_property IS NOT NULL
                  AND undertaking_property <> ''
            """)
        ).fetchall()

        for (name,) in rows:
            conn.execute(
                text("INSERT INTO category (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                {'name': name}
            )

        # Back-fill category_id
        conn.execute(
            text("""
                UPDATE inventory
                SET category_id = c.id
                FROM category c
                WHERE c.name = inventory.undertaking_property
                  AND inventory.undertaking_property IS NOT NULL
                  AND inventory.undertaking_property <> ''
            """)
        )

    # 4. Add FK constraint if not already present
    existing_fks = [fk['name'] for fk in inspect(conn).get_foreign_keys('inventory')]
    if 'fk_inventory_category_id' not in existing_fks:
        op.create_foreign_key(
            'fk_inventory_category_id', 'inventory', 'category',
            ['category_id'], ['id']
        )

    # 5. Drop redundant columns that now live in other tables
    for col in ('undertaking_property', 'borrower_name', 'date_borrowed',
                'disposal_date', 'disposal_reason'):
        if col in _existing_columns(conn, 'inventory'):
            op.drop_column('inventory', col)

    # 6. Drop history_log if present (superseded by disposal_history)
    if 'history_log' in _existing_tables(conn):
        op.drop_table('history_log')


def downgrade():
    conn = op.get_bind()

    # Restore history_log
    if 'history_log' not in _existing_tables(conn):
        op.create_table(
            'history_log',
            sa.Column('id',              sa.Integer(),  nullable=False),
            sa.Column('item_id',         sa.Integer(),  nullable=False),
            sa.Column('event_type',      sa.String(50), nullable=False),
            sa.Column('quantity',        sa.Integer(),  nullable=False),
            sa.Column('remarks',         sa.Text(),     nullable=True),
            sa.Column('status_snapshot', sa.String(50), nullable=True),
            sa.Column('event_date',      sa.DateTime(), nullable=True),
            sa.Column('is_resolved',     sa.Boolean(),  nullable=True),
            sa.ForeignKeyConstraint(['item_id'], ['inventory.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    # Restore dropped columns
    inv_cols = _existing_columns(conn, 'inventory')
    for col, typ in [
        ('undertaking_property', sa.String(100)),
        ('borrower_name',        sa.String(100)),
        ('date_borrowed',        sa.Date()),
        ('disposal_date',        sa.Date()),
        ('disposal_reason',      sa.String(255)),
    ]:
        if col not in inv_cols:
            op.add_column('inventory', sa.Column(col, typ, nullable=True))

    # Re-populate undertaking_property from category names
    conn.execute(
        text("""
            UPDATE inventory
            SET undertaking_property = c.name
            FROM category c
            WHERE c.id = inventory.category_id
        """)
    )

    # Drop FK, category_id column, and category table
    op.drop_constraint('fk_inventory_category_id', 'inventory', type_='foreignkey')
    op.drop_column('inventory', 'category_id')
    op.drop_table('category')
