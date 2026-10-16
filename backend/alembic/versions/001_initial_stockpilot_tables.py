"""create initial stockpilot tables

Revision ID: 001_initial_stockpilot_tables
Revises: 
Create Date: 2026-10-16 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = "001_initial_stockpilot_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create 'products' table
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_level", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku", name="uq_products_sku")
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=True)
    op.create_index(op.f("ix_products_category"), "products", ["category"], unique=False)

    # 2. Create 'stock_movements' table
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("movement_type", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name="fk_stock_movements_product_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_stock_movements_id"), "stock_movements", ["id"], unique=False)
    op.create_index(op.f("ix_stock_movements_product_id"), "stock_movements", ["product_id"], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index(op.f("ix_stock_movements_product_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_id"), table_name="stock_movements")
    op.drop_table("stock_movements")

    op.drop_index(op.f("ix_products_category"), table_name="products")
    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
