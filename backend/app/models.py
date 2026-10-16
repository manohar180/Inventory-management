"""
SQLAlchemy ORM models defining the database schema for StockPilot.
Tables:
  - products: Catalog of warehouse items, stock counts, and reorder levels.
  - stock_movements: Ledger of inbound (IN) and outbound (OUT) inventory adjustments.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Product(Base):
    """
    Represents an inventory item stored in the warehouse.
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # One-to-many relationship: A product can have multiple inventory movements
    movements: Mapped[List["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="StockMovement.id.desc()"
    )

    def is_low_stock(self) -> bool:
        """Helper to determine if inventory has hit or dropped below reorder threshold."""
        return self.quantity <= self.reorder_level


class StockMovement(Base):
    """
    Ledger recording all inventory transactions (IN for restocking, OUT for dispatch/sale).
    """
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    movement_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'IN' or 'OUT'
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Reference back to the associated product
    product: Mapped["Product"] = relationship("Product", back_populates="movements")
