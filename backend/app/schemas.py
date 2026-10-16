"""
Pydantic v2 validation and serialization schemas for StockPilot.
Enforces business constraints on products, stock movements, and analytics.
"""

from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ==========================================
# Product Schemas
# ==========================================

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product item name")
    sku: str = Field(..., min_length=2, max_length=100, description="Unique Stock Keeping Unit code")
    category: str = Field(..., min_length=1, max_length=100, description="Category classification")
    price: float = Field(..., ge=0.0, description="Unit price (cannot be negative)")
    quantity: int = Field(default=0, ge=0, description="Available stock quantity (cannot be negative)")
    reorder_level: int = Field(default=10, ge=0, description="Threshold triggering low stock alert")


class ProductCreate(ProductBase):
    """Payload for creating a new product."""
    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, v: str) -> str:
        return v.strip().upper()


class ProductUpdate(BaseModel):
    """Payload for modifying an existing product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0.0)
    quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v else v


class ProductResponse(ProductBase):
    """Schema returned to API clients representing a product."""
    id: int
    created_at: datetime
    is_low_stock: bool = False

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Stock Movement Schemas
# ==========================================

class StockMovementCreate(BaseModel):
    """Payload for registering inventory adjustments (IN or OUT)."""
    movement_type: Literal["IN", "OUT"] = Field(..., description="IN for restocking, OUT for dispatch/sale")
    quantity: int = Field(..., gt=0, description="Movement quantity must be greater than zero")
    note: Optional[str] = Field(None, max_length=255, description="Optional audit note or reference")

    @field_validator("movement_type")
    @classmethod
    def uppercase_movement_type(cls, v: str) -> str:
        return v.strip().upper()


class StockMovementResponse(BaseModel):
    """Schema returned representing a registered movement."""
    id: int
    product_id: int
    movement_type: str
    quantity: int
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Inventory Stats & Health Schemas
# ==========================================

class InventoryStats(BaseModel):
    """Aggregated dashboard KPIs for warehouse inventory."""
    total_products: int
    total_units: int
    low_stock_count: int
    total_stock_value: float


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReadyResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
