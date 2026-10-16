"""
Comprehensive unit and integration test suite for StockPilot.
Tests all endpoints, validations, business constraints, error codes, and metrics.
Uses an isolated in-memory SQLite database via FastAPI dependency override.
"""

from fastapi.testclient import TestClient


# ==========================================
# 1. System & Probe Tests
# ==========================================

def test_root_endpoint(client: TestClient):
    """Verify root endpoint returns basic application service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "StockPilot"
    assert data["status"] == "running"
    assert "version" in data


def test_health_probe(client: TestClient):
    """Verify Kubernetes liveness probe returns healthy 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_readiness_probe(client: TestClient):
    """Verify Kubernetes readiness probe validates database connection."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_metrics_endpoint(client: TestClient):
    """Verify Prometheus metrics are exposed at /metrics including custom gauges."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "stockpilot_low_stock_products" in response.text
    assert "stockpilot_stock_movements_total" in response.text


# ==========================================
# 2. Product Catalog CRUD Tests
# ==========================================

def test_create_product_success(client: TestClient):
    """Verify product creation with valid attributes and initial stock tracking."""
    payload = {
        "name": "Heavy Duty Wrench",
        "sku": "WRN-101",
        "category": "Tools",
        "price": 24.99,
        "quantity": 20,
        "reorder_level": 5
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "Heavy Duty Wrench"
    assert data["sku"] == "WRN-101"
    assert data["price"] == 24.99
    assert data["quantity"] == 20
    assert data["is_low_stock"] is False


def test_create_product_duplicate_sku_returns_409(client: TestClient):
    """Verify unique constraint on SKU returns 409 Conflict."""
    payload = {
        "name": "Cordless Drill",
        "sku": "DRL-200",
        "category": "Power Tools",
        "price": 79.99,
        "quantity": 10,
        "reorder_level": 5
    }
    # Initial creation
    res1 = client.post("/api/products", json=payload)
    assert res1.status_code == 201

    # Attempt duplicate creation
    res2 = client.post("/api/products", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_create_product_validation_negative_values(client: TestClient):
    """Verify Pydantic validation rejects negative price and quantity with 422."""
    payload_bad_price = {
        "name": "Safety Goggles",
        "sku": "SFT-001",
        "category": "Safety",
        "price": -10.0,
        "quantity": 5,
        "reorder_level": 2
    }
    res1 = client.post("/api/products", json=payload_bad_price)
    assert res1.status_code == 422

    payload_bad_qty = {
        "name": "Safety Gloves",
        "sku": "SFT-002",
        "category": "Safety",
        "price": 10.0,
        "quantity": -5,
        "reorder_level": 2
    }
    res2 = client.post("/api/products", json=payload_bad_qty)
    assert res2.status_code == 422


def test_list_products_and_search(client: TestClient):
    """Verify listing products and filtering by search query."""
    client.post("/api/products", json={"name": "Steel Hammer", "sku": "HAM-01", "category": "Hardware", "price": 15.0, "quantity": 12, "reorder_level": 3})
    client.post("/api/products", json={"name": "Copper Wire 50m", "sku": "WIR-50", "category": "Electrical", "price": 45.0, "quantity": 8, "reorder_level": 2})

    # Search by name match
    res_search = client.get("/api/products?search=hammer")
    assert res_search.status_code == 200
    items = res_search.json()
    assert len(items) == 1
    assert items[0]["sku"] == "HAM-01"

    # Search by category match
    res_cat = client.get("/api/products?search=Electrical")
    assert res_cat.status_code == 200
    assert len(res_cat.json()) == 1


def test_list_products_low_stock_filter(client: TestClient):
    """Verify ?low_stock=true returns only products at or below reorder level."""
    # Low stock item: quantity 2 <= reorder_level 5
    client.post("/api/products", json={"name": "Paint Roller", "sku": "PNT-01", "category": "Paint", "price": 8.0, "quantity": 2, "reorder_level": 5})
    # Normal stock item: quantity 50 > reorder_level 10
    client.post("/api/products", json={"name": "Paint Brush Set", "sku": "PNT-02", "category": "Paint", "price": 12.0, "quantity": 50, "reorder_level": 10})

    res = client.get("/api/products?low_stock=true")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["sku"] == "PNT-01"
    assert items[0]["is_low_stock"] is True


def test_get_product_by_id_success(client: TestClient):
    """Verify retrieving single product by ID."""
    created = client.post("/api/products", json={"name": "Angle Grinder", "sku": "GRN-01", "category": "Tools", "price": 65.0, "quantity": 7, "reorder_level": 2}).json()
    prod_id = created["id"]

    res = client.get(f"/api/products/{prod_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Angle Grinder"


def test_get_product_not_found_returns_404(client: TestClient):
    """Verify 404 is returned when requesting nonexistent product ID."""
    response = client.get("/api/products/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_product_success(client: TestClient):
    """Verify modifying product attributes via PUT."""
    created = client.post("/api/products", json={"name": "Screwdriver Kit", "sku": "SCR-10", "category": "Tools", "price": 19.99, "quantity": 15, "reorder_level": 5}).json()
    prod_id = created["id"]

    update_payload = {"name": "Pro Screwdriver Kit", "price": 22.50}
    response = client.put(f"/api/products/{prod_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pro Screwdriver Kit"
    assert data["price"] == 22.50
    assert data["quantity"] == 15  # Unchanged


def test_update_product_sku_conflict_returns_409(client: TestClient):
    """Verify updating a product's SKU to an already-used SKU returns 409."""
    client.post("/api/products", json={"name": "Item A", "sku": "SKU-A", "category": "Cat", "price": 10.0, "quantity": 5, "reorder_level": 2})
    prod_b = client.post("/api/products", json={"name": "Item B", "sku": "SKU-B", "category": "Cat", "price": 12.0, "quantity": 5, "reorder_level": 2}).json()

    # Attempt to rename Item B's SKU to SKU-A
    res = client.put(f"/api/products/{prod_b['id']}", json={"sku": "SKU-A"})
    assert res.status_code == 409


def test_delete_product_success(client: TestClient):
    """Verify deleting product removes it from catalog and returns 204."""
    created = client.post("/api/products", json={"name": "Discontinued Item", "sku": "DIS-01", "category": "Misc", "price": 5.0, "quantity": 1, "reorder_level": 0}).json()
    prod_id = created["id"]

    res_del = client.delete(f"/api/products/{prod_id}")
    assert res_del.status_code == 204

    # Subsequent GET returns 404
    assert client.get(f"/api/products/{prod_id}").status_code == 404


def test_delete_product_not_found_returns_404(client: TestClient):
    """Verify deleting non-existent product ID returns 404."""
    response = client.delete("/api/products/888888")
    assert response.status_code == 404


# ==========================================
# 3. Stock Movement & Ledger Tests
# ==========================================

def test_stock_movement_in_increases_quantity(client: TestClient):
    """Verify stock IN movement correctly adds inventory units."""
    created = client.post("/api/products", json={"name": "Plywood Sheet", "sku": "PLY-01", "category": "Lumber", "price": 30.0, "quantity": 10, "reorder_level": 5}).json()
    prod_id = created["id"]

    # Inbound restock of 15 units
    res_move = client.post(f"/api/products/{prod_id}/movements", json={"movement_type": "IN", "quantity": 15, "note": "Weekly shipment"})
    assert res_move.status_code == 201
    assert res_move.json()["movement_type"] == "IN"
    assert res_move.json()["quantity"] == 15

    # Check updated quantity: 10 + 15 = 25
    updated = client.get(f"/api/products/{prod_id}").json()
    assert updated["quantity"] == 25


def test_stock_movement_out_decreases_quantity(client: TestClient):
    """Verify stock OUT movement correctly subtracts inventory units."""
    created = client.post("/api/products", json={"name": "Cement Bag", "sku": "CMT-01", "category": "Masonry", "price": 12.0, "quantity": 30, "reorder_level": 10}).json()
    prod_id = created["id"]

    # Outbound dispatch of 10 units
    res_move = client.post(f"/api/products/{prod_id}/movements", json={"movement_type": "OUT", "quantity": 10, "note": "Dispatched order #440"})
    assert res_move.status_code == 201

    # Check updated quantity: 30 - 10 = 20
    updated = client.get(f"/api/products/{prod_id}").json()
    assert updated["quantity"] == 20


def test_stock_movement_out_exceeding_stock_returns_400(client: TestClient):
    """Verify stock OUT movement exceeding current quantity is rejected with 400 Bad Request."""
    created = client.post("/api/products", json={"name": "Precision Caliper", "sku": "CAL-01", "category": "Tools", "price": 40.0, "quantity": 5, "reorder_level": 2}).json()
    prod_id = created["id"]

    # Request 20 units when only 5 exist
    res = client.post(f"/api/products/{prod_id}/movements", json={"movement_type": "OUT", "quantity": 20, "note": "Excess request"})
    assert res.status_code == 400
    assert "Insufficient stock" in res.json()["detail"]

    # Verify stock remained untouched at 5
    product_check = client.get(f"/api/products/{prod_id}").json()
    assert product_check["quantity"] == 5


def test_get_product_movements_history(client: TestClient):
    """Verify retrieving chronological movement audit history for a product."""
    created = client.post("/api/products", json={"name": "Safety Helmet", "sku": "HLM-01", "category": "Safety", "price": 18.0, "quantity": 10, "reorder_level": 3}).json()
    prod_id = created["id"]

    # Add 2 movements
    client.post(f"/api/products/{prod_id}/movements", json={"movement_type": "IN", "quantity": 5})
    client.post(f"/api/products/{prod_id}/movements", json={"movement_type": "OUT", "quantity": 3})

    # History includes initial creation IN + 2 subsequent movements = 3 total
    res = client.get(f"/api/products/{prod_id}/movements")
    assert res.status_code == 200
    movements = res.json()
    assert len(movements) == 3


# ==========================================
# 4. Inventory Analytics Statistics Test
# ==========================================

def test_inventory_stats_calculation(client: TestClient):
    """Verify /api/inventory/stats aggregates units, products, low-stock count, and value."""
    # Item 1: 10 units @ $20 = $200 (reorder 5, normal)
    client.post("/api/products", json={"name": "Item 1", "sku": "ITM-001", "category": "A", "price": 20.0, "quantity": 10, "reorder_level": 5})
    # Item 2: 2 units @ $50 = $100 (reorder 5, LOW STOCK)
    client.post("/api/products", json={"name": "Item 2", "sku": "ITM-002", "category": "B", "price": 50.0, "quantity": 2, "reorder_level": 5})

    res = client.get("/api/inventory/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_products"] == 2
    assert stats["total_units"] == 12
    assert stats["low_stock_count"] == 1
    assert stats["total_stock_value"] == 300.0
