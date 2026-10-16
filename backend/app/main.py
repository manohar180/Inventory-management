"""
Main FastAPI application for StockPilot.
Provides RESTful APIs for inventory management, health/readiness probes,
and Prometheus observability instrumentation.
"""

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text, or_
from prometheus_client import Counter, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.db import get_db, engine
from app.models import Product, StockMovement
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    StockMovementCreate,
    StockMovementResponse,
    InventoryStats,
    HealthResponse,
    ReadyResponse,
)

# ==========================================
# Custom Prometheus Metrics
# ==========================================

STOCK_MOVEMENTS_TOTAL = Counter(
    "stockpilot_stock_movements_total",
    "Total count of recorded stock movements",
    ["type"]  # 'IN' or 'OUT'
)

LOW_STOCK_GAUGE = Gauge(
    "stockpilot_low_stock_products",
    "Current number of products that are at or below reorder level"
)


def update_low_stock_metric(db: Session) -> int:
    """Helper to recalculate and update the low stock gauge metric."""
    count = db.scalar(
        select(func.count(Product.id)).where(Product.quantity <= Product.reorder_level)
    ) or 0
    LOW_STOCK_GAUGE.set(count)
    return count


# ==========================================
# Application Lifespan
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize low stock gauge if possible
    try:
        with Session(engine) as session:
            update_low_stock_metric(session)
    except Exception:
        # DB might not be ready yet upon very initial boot
        pass
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="StockPilot Cloud-Native Inventory Management API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for decoupled frontend development and API proxying
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument FastAPI with Prometheus metrics
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/health", "/ready", "/metrics"]
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")


# ==========================================
# Health & Status Endpoints
# ==========================================

@app.get(
    "/",
    tags=["Root"],
    summary="Root API info"
)
def read_root():
    """Returns basic service descriptor."""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Probes"],
    summary="Liveness probe"
)
def health_check():
    """Liveness probe: verifies that the application process is running."""
    return HealthResponse(status="ok")


@app.get(
    "/ready",
    response_model=ReadyResponse,
    tags=["Probes"],
    summary="Readiness probe"
)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe: validates database connectivity with a ping query."""
    try:
        db.execute(text("SELECT 1"))
        return ReadyResponse(status="ready", database="connected")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(exc)}"
        )


# ==========================================
# Inventory Analytics Endpoint
# ==========================================

@app.get(
    "/api/inventory/stats",
    response_model=InventoryStats,
    tags=["Inventory Analytics"],
    summary="Retrieve inventory overview statistics"
)
def get_inventory_stats(db: Session = Depends(get_db)):
    """
    Computes total products, total stock units, low-stock item count,
    and aggregate total inventory value.
    """
    products = db.scalars(select(Product)).all()
    total_products = len(products)
    total_units = sum(p.quantity for p in products)
    low_stock_count = sum(1 for p in products if p.quantity <= p.reorder_level)
    total_stock_value = round(sum(p.quantity * p.price for p in products), 2)

    # Sync Prometheus gauge
    LOW_STOCK_GAUGE.set(low_stock_count)

    return InventoryStats(
        total_products=total_products,
        total_units=total_units,
        low_stock_count=low_stock_count,
        total_stock_value=total_stock_value
    )


# ==========================================
# Product Catalog Endpoints
# ==========================================

@app.get(
    "/api/products",
    response_model=List[ProductResponse],
    tags=["Products"],
    summary="List products with optional search and low-stock filter"
)
def list_products(
    search: Optional[str] = Query(None, description="Filter by name, SKU, or category"),
    low_stock: Optional[bool] = Query(False, description="Filter only items at or below reorder level"),
    db: Session = Depends(get_db)
):
    """Retrieves all products with optional text search and low-stock filtering."""
    query = select(Product)

    if search:
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Product.name.ilike(term),
                Product.sku.ilike(term),
                Product.category.ilike(term)
            )
        )

    if low_stock:
        query = query.where(Product.quantity <= Product.reorder_level)

    products = db.scalars(query).all()
    return [ProductResponse.model_validate(prod) for prod in products]


@app.get(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Get product details by ID"
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieves a single product by its unique integer identifier."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return ProductResponse.model_validate(product)


@app.post(
    "/api/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create a new product"
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a new product in inventory.
    Enforces uniqueness on SKU code (returns 409 Conflict on duplication).
    """
    # Check for duplicate SKU
    existing = db.scalar(select(Product).where(Product.sku == payload.sku))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{payload.sku}' already exists"
        )

    product = Product(
        name=payload.name,
        sku=payload.sku,
        category=payload.category,
        price=payload.price,
        quantity=payload.quantity,
        reorder_level=payload.reorder_level
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # If product was created with initial stock, record initial stock movement
    if product.quantity > 0:
        movement = StockMovement(
            product_id=product.id,
            movement_type="IN",
            quantity=product.quantity,
            note="Initial stock upon creation"
        )
        db.add(movement)
        db.commit()
        STOCK_MOVEMENTS_TOTAL.labels(type="IN").inc()

    update_low_stock_metric(db)
    return ProductResponse.model_validate(product)


@app.put(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Update product details"
)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    """Updates product attributes, validating that SKU does not collide with another product."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    # Check for SKU conflict if updating SKU
    if payload.sku and payload.sku != product.sku:
        conflict = db.scalar(
            select(Product).where(Product.sku == payload.sku, Product.id != product_id)
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"SKU '{payload.sku}' is already assigned to product ID {conflict.id}"
            )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    update_low_stock_metric(db)
    return ProductResponse.model_validate(product)


@app.delete(
    "/api/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
    summary="Delete a product"
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Deletes product and cascades associated movement audit records."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    db.delete(product)
    db.commit()

    update_low_stock_metric(db)
    return None


# ==========================================
# Stock Movement Endpoints
# ==========================================

@app.post(
    "/api/products/{product_id}/movements",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Stock Movements"],
    summary="Record a stock movement (IN or OUT)"
)
def create_stock_movement(
    product_id: int,
    payload: StockMovementCreate,
    db: Session = Depends(get_db)
):
    """
    Records an inventory movement:
      - IN: Increments product quantity.
      - OUT: Decrements product quantity.
    Rejects with 400 Bad Request if OUT quantity exceeds current available stock.
    """
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    if payload.movement_type == "IN":
        product.quantity += payload.quantity
    elif payload.movement_type == "OUT":
        if payload.quantity > product.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock: requested {payload.quantity} units, "
                    f"but only {product.quantity} units are in stock."
                )
            )
        product.quantity -= payload.quantity

    movement = StockMovement(
        product_id=product.id,
        movement_type=payload.movement_type,
        quantity=payload.quantity,
        note=payload.note
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)

    # Update Prometheus metrics
    STOCK_MOVEMENTS_TOTAL.labels(type=payload.movement_type).inc()
    update_low_stock_metric(db)

    return movement


@app.get(
    "/api/products/{product_id}/movements",
    response_model=List[StockMovementResponse],
    tags=["Stock Movements"],
    summary="Get movement history for a product"
)
def get_product_movements(product_id: int, db: Session = Depends(get_db)):
    """Returns the chronological audit trail of stock adjustments for a specific product."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    movements = db.scalars(
        select(StockMovement)
        .where(StockMovement.product_id == product_id)
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
    ).all()

    return movements
