import React, { useState, useEffect } from 'react';

export default function App() {
  // Application Data States
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState({
    total_products: 0,
    total_units: 0,
    low_stock_count: 0,
    total_stock_value: 0.0,
  });

  // UI & Filter States
  const [loading, setLoading] = useState(true);
  const [backendError, setBackendError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [activeTab, setActiveTab] = useState('inventory'); // 'inventory' | 'stats'

  // Modal State: null | { mode: 'create' | 'edit' | 'movement', product?: object }
  const [activeModal, setActiveModal] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    category: '',
    price: '',
    quantity: '',
    reorder_level: '10',
  });
  const [movementData, setMovementData] = useState({
    movement_type: 'IN',
    quantity: '1',
    note: '',
  });

  // Toast Notification State
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  // ==========================================
  // API Fetch Functions (Relative URLs /api/...)
  // ==========================================

  const loadStats = async () => {
    try {
      const res = await fetch('/api/inventory/stats');
      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to load inventory stats`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching inventory stats:', err);
    }
  };

  const loadProducts = async () => {
    try {
      setLoading(true);
      setBackendError(null);
      const params = new URLSearchParams();
      if (searchTerm.trim()) params.append('search', searchTerm.trim());
      if (lowStockOnly) params.append('low_stock', 'true');

      const url = `/api/products${params.toString() ? `?${params.toString()}` : ''}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch product catalog`);
      const data = await res.json();
      setProducts(data);
    } catch (err) {
      console.error('Error loading products:', err);
      setBackendError(err.message || 'Unable to reach StockPilot API service.');
    } finally {
      setLoading(false);
    }
  };

  // Initial load and filter re-fetch
  useEffect(() => {
    loadStats();
    loadProducts();
  }, [searchTerm, lowStockOnly]);

  // ==========================================
  // Form & Action Handlers
  // ==========================================

  const openCreateModal = () => {
    setFormData({
      name: '',
      sku: '',
      category: '',
      price: '',
      quantity: '0',
      reorder_level: '10',
    });
    setActiveModal({ mode: 'create' });
  };

  const openEditModal = (product) => {
    setFormData({
      name: product.name,
      sku: product.sku,
      category: product.category,
      price: product.price.toString(),
      quantity: product.quantity.toString(),
      reorder_level: product.reorder_level.toString(),
    });
    setActiveModal({ mode: 'edit', product });
  };

  const openMovementModal = (product) => {
    setMovementData({
      movement_type: 'IN',
      quantity: '5',
      note: 'Routine restock',
    });
    setActiveModal({ mode: 'movement', product });
  };

  const closeModal = () => {
    setActiveModal(null);
  };

  // Submit Create or Edit Product
  const handleProductSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name: formData.name.trim(),
        sku: formData.sku.trim().toUpperCase(),
        category: formData.category.trim(),
        price: parseFloat(formData.price) || 0.0,
        quantity: parseInt(formData.quantity, 10) || 0,
        reorder_level: parseInt(formData.reorder_level, 10) || 0,
      };

      if (activeModal.mode === 'create') {
        const res = await fetch('/api/products', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (res.status === 409) {
          showToast(`SKU '${payload.sku}' already exists!`, 'error');
          return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to create product`);
        showToast(`Product '${payload.name}' added successfully!`, 'success');
      } else if (activeModal.mode === 'edit') {
        const prodId = activeModal.product.id;
        const res = await fetch(`/api/products/${prodId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (res.status === 409) {
          showToast(`SKU '${payload.sku}' is assigned to another product!`, 'error');
          return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to update product`);
        showToast(`Product updated successfully!`, 'success');
      }

      closeModal();
      loadProducts();
      loadStats();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Submit Stock Movement (IN or OUT)
  const handleMovementSubmit = async (e) => {
    e.preventDefault();
    try {
      const prodId = activeModal.product.id;
      const qty = parseInt(movementData.quantity, 10);
      if (qty <= 0) {
        showToast('Quantity must be greater than zero', 'error');
        return;
      }

      const res = await fetch(`/api/products/${prodId}/movements`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          movement_type: movementData.movement_type,
          quantity: qty,
          note: movementData.note.trim() || undefined,
        }),
      });

      if (res.status === 400) {
        const errDetail = await res.json();
        showToast(errDetail.detail || 'Insufficient stock for OUT movement!', 'error');
        return;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to register movement`);

      showToast(`Stock ${movementData.movement_type} of ${qty} units recorded!`, 'success');
      closeModal();
      loadProducts();
      loadStats();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Delete Product
  const handleDeleteProduct = async (product) => {
    if (!window.confirm(`Are you sure you want to delete '${product.name}' (SKU: ${product.sku})?`)) {
      return;
    }
    try {
      const res = await fetch(`/api/products/${product.id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to delete product`);
      showToast(`Product deleted successfully`, 'success');
      loadProducts();
      loadStats();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // ==========================================
  // Render JSX
  // ==========================================

  return (
    <div className="app-container">
      {/* Toast Feedback */}
      {toast && (
        <div className="toast-container" id="toast-notification">
          <div className={`toast ${toast.type}`}>
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* Sidebar Navigation */}
      <aside className="sidebar" id="app-sidebar">
        <div className="brand">
          <div className="brand-icon">
            <svg viewBox="0 0 24 24">
              <path d="M21 16.5C21 16.88 20.79 17.21 20.47 17.38L12.57 21.82C12.41 21.94 12.21 22 12 22C11.79 22 11.59 21.94 11.43 21.82L3.53 17.38C3.21 17.21 3 16.88 3 16.5V7.5C3 7.12 3.21 6.79 3.53 6.62L11.43 2.18C11.59 2.06 11.79 2 12 2C12.21 2 12.41 2.06 12.57 2.18L20.47 6.62C20.79 6.79 21 7.12 21 7.5V16.5Z" />
            </svg>
          </div>
          <span className="brand-name">StockPilot</span>
        </div>

        <nav className="sidebar-nav">
          <button
            id="nav-inventory-btn"
            className={`nav-item ${activeTab === 'inventory' ? 'active' : ''}`}
            onClick={() => setActiveTab('inventory')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24">
              <rect x="2" y="3" width="20" height="14" rx="2" />
              <line x1="8" y1="21" x2="16" y2="21" />
              <line x1="12" y1="17" x2="12" y2="21" />
            </svg>
            <span className="nav-text">Inventory Catalog</span>
          </button>

          <button
            id="nav-stats-btn"
            className={`nav-item ${activeTab === 'stats' ? 'active' : ''}`}
            onClick={() => setActiveTab('stats')}
          >
            <svg className="nav-icon" viewBox="0 0 24 24">
              <path d="M18 20V10" />
              <path d="M12 20V4" />
              <path d="M6 20v-6" />
            </svg>
            <span className="nav-text">Warehouse Analytics</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <p>StockPilot Cloud-Native v1.0</p>
          <p>EKS • FastAPI • React</p>
        </div>
      </aside>

      {/* Main View Area */}
      <div className="main-wrapper">
        {/* Sticky Topbar */}
        <header className="topbar" id="app-topbar">
          <div className="topbar-left">
            <h1 id="page-title">{activeTab === 'inventory' ? 'Inventory Catalog' : 'Warehouse Analytics'}</h1>
            <p>Real-time automated inventory tracking and replenishment control</p>
          </div>
          <div className="topbar-actions">
            <button
              id="refresh-btn"
              className="btn btn-secondary btn-sm"
              onClick={() => {
                loadStats();
                loadProducts();
                showToast('Refreshed inventory data', 'success');
              }}
            >
              Refresh
            </button>
            <button id="add-product-btn" className="btn btn-primary" onClick={openCreateModal}>
              + Add Product
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="content-body">
          {/* KPI Analytics Cards */}
          <section className="kpi-grid" id="kpi-cards-grid">
            <div className="kpi-card" id="kpi-total-products">
              <div className="kpi-icon indigo">
                <svg viewBox="0 0 24 24">
                  <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div className="kpi-details">
                <span className="kpi-title">Total Products</span>
                <span className="kpi-value">{stats.total_products}</span>
              </div>
            </div>

            <div className="kpi-card" id="kpi-total-units">
              <div className="kpi-icon emerald">
                <svg viewBox="0 0 24 24">
                  <path d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </div>
              <div className="kpi-details">
                <span className="kpi-title">Total Stock Units</span>
                <span className="kpi-value">{stats.total_units.toLocaleString()}</span>
              </div>
            </div>

            <div className="kpi-card" id="kpi-low-stock">
              <div className="kpi-icon amber">
                <svg viewBox="0 0 24 24">
                  <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="kpi-details">
                <span className="kpi-title">Low Stock Alerts</span>
                <span className="kpi-value">{stats.low_stock_count}</span>
              </div>
            </div>

            <div className="kpi-card" id="kpi-stock-value">
              <div className="kpi-icon purple">
                <svg viewBox="0 0 24 24">
                  <line x1="12" y1="1" x2="12" y2="23" />
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
              </div>
              <div className="kpi-details">
                <span className="kpi-title">Inventory Value</span>
                <span className="kpi-value">${stats.total_stock_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
            </div>
          </section>

          {/* Backend Error State Banner */}
          {backendError && (
            <div className="state-container" style={{ background: 'var(--status-danger-bg)', borderRadius: 'var(--radius-lg)' }} id="backend-error-state">
              <p className="state-title" style={{ color: '#fb7185' }}>Backend Communication Error</p>
              <p className="state-subtitle">{backendError}</p>
              <button className="btn btn-secondary btn-sm" onClick={() => loadProducts()}>Retry Connection</button>
            </div>
          )}

          {/* Controls Bar: Search & Low Stock Toggle */}
          <section className="controls-bar">
            <div className="search-filter-group">
              <div className="search-box">
                <svg viewBox="0 0 24 24">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <input
                  id="search-input"
                  type="text"
                  className="search-input"
                  placeholder="Search products by name, SKU, or category..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <button
                id="low-stock-toggle"
                className={`filter-toggle ${lowStockOnly ? 'active' : ''}`}
                onClick={() => setLowStockOnly(!lowStockOnly)}
              >
                <span>Low Stock Only</span>
                {stats.low_stock_count > 0 && <span className="stock-badge low">{stats.low_stock_count}</span>}
              </button>
            </div>
          </section>

          {/* Product Data Table */}
          <section className="table-card" id="products-table-card">
            {loading ? (
              <div className="state-container" id="loading-state">
                <div className="spinner"></div>
                <p className="state-subtitle">Loading inventory records...</p>
              </div>
            ) : products.length === 0 ? (
              <div className="state-container" id="empty-state">
                <p className="state-title">No Products Found</p>
                <p className="state-subtitle">
                  {searchTerm || lowStockOnly
                    ? 'No products matched your search or low-stock criteria.'
                    : 'Your warehouse catalog is currently empty. Click "+ Add Product" to get started.'}
                </p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="data-table" id="products-table">
                  <thead>
                    <tr>
                      <th>Product Name</th>
                      <th>SKU</th>
                      <th>Category</th>
                      <th>Price</th>
                      <th>Stock Units</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((prod) => (
                      <tr key={prod.id} id={`product-row-${prod.id}`}>
                        <td>
                          <strong>{prod.name}</strong>
                        </td>
                        <td>
                          <span className="sku-tag">{prod.sku}</span>
                        </td>
                        <td>
                          <span className="category-tag">{prod.category}</span>
                        </td>
                        <td>${prod.price.toFixed(2)}</td>
                        <td>
                          <strong>{prod.quantity}</strong>
                          <span style={{ fontSize: '11px', color: 'var(--text-dim)', marginLeft: '6px' }}>
                            (Min: {prod.reorder_level})
                          </span>
                        </td>
                        <td>
                          {prod.quantity === 0 ? (
                            <span className="stock-badge critical">
                              <span className="badge-dot"></span> Out of Stock
                            </span>
                          ) : prod.is_low_stock ? (
                            <span className="stock-badge low">
                              <span className="badge-dot"></span> Low Stock
                            </span>
                          ) : (
                            <span className="stock-badge ok">
                              <span className="badge-dot"></span> In Stock
                            </span>
                          )}
                        </td>
                        <td>
                          <div className="table-actions">
                            <button
                              id={`stock-btn-${prod.id}`}
                              className="btn btn-secondary btn-sm"
                              onClick={() => openMovementModal(prod)}
                              title="Add or remove warehouse units"
                            >
                              Stock IN/OUT
                            </button>
                            <button
                              id={`edit-btn-${prod.id}`}
                              className="btn btn-secondary btn-sm"
                              onClick={() => openEditModal(prod)}
                            >
                              Edit
                            </button>
                            <button
                              id={`delete-btn-${prod.id}`}
                              className="btn btn-danger btn-sm"
                              onClick={() => handleDeleteProduct(prod)}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </main>
      </div>

      {/* ==========================================
          Add / Edit Product Modal
          ========================================== */}
      {activeModal && (activeModal.mode === 'create' || activeModal.mode === 'edit') && (
        <div className="modal-overlay" id="product-modal-overlay" onClick={closeModal}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title" id="modal-heading">
                {activeModal.mode === 'create' ? 'Add New Product' : 'Edit Product'}
              </h3>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>
            <form onSubmit={handleProductSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label htmlFor="form-product-name">Product Name *</label>
                  <input
                    id="form-product-name"
                    className="form-input"
                    type="text"
                    required
                    placeholder="e.g. Industrial Drill Press"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="form-product-sku">SKU Code *</label>
                    <input
                      id="form-product-sku"
                      className="form-input"
                      type="text"
                      required
                      placeholder="e.g. DRL-500"
                      value={formData.sku}
                      onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="form-product-category">Category *</label>
                    <input
                      id="form-product-category"
                      className="form-input"
                      type="text"
                      required
                      placeholder="e.g. Heavy Equipment"
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="form-product-price">Unit Price ($) *</label>
                    <input
                      id="form-product-price"
                      className="form-input"
                      type="number"
                      step="0.01"
                      min="0"
                      required
                      placeholder="0.00"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="form-product-reorder">Reorder Threshold *</label>
                    <input
                      id="form-product-reorder"
                      className="form-input"
                      type="number"
                      min="0"
                      required
                      placeholder="10"
                      value={formData.reorder_level}
                      onChange={(e) => setFormData({ ...formData, reorder_level: e.target.value })}
                    />
                  </div>
                </div>

                {activeModal.mode === 'create' && (
                  <div className="form-group">
                    <label htmlFor="form-product-quantity">Initial Stock Quantity</label>
                    <input
                      id="form-product-quantity"
                      className="form-input"
                      type="number"
                      min="0"
                      placeholder="0"
                      value={formData.quantity}
                      onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                    />
                  </div>
                )}
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button id="modal-save-btn" type="submit" className="btn btn-primary">
                  {activeModal.mode === 'create' ? 'Create Product' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==========================================
          Stock Movement Modal (IN / OUT)
          ========================================== */}
      {activeModal && activeModal.mode === 'movement' && (
        <div className="modal-overlay" id="movement-modal-overlay" onClick={closeModal}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title" id="movement-modal-heading">
                Stock Movement: {activeModal.product.name}
              </h3>
              <button className="modal-close" onClick={closeModal}>✕</button>
            </div>
            <form onSubmit={handleMovementSubmit}>
              <div className="modal-body">
                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Current Inventory: <strong>{activeModal.product.quantity} units</strong> (SKU: {activeModal.product.sku})
                </p>

                <div className="movement-selector">
                  <button
                    type="button"
                    id="movement-type-in-btn"
                    className={`movement-btn ${movementData.movement_type === 'IN' ? 'active-in' : ''}`}
                    onClick={() => setMovementData({ ...movementData, movement_type: 'IN' })}
                  >
                    + Stock IN (Restock)
                  </button>
                  <button
                    type="button"
                    id="movement-type-out-btn"
                    className={`movement-btn ${movementData.movement_type === 'OUT' ? 'active-out' : ''}`}
                    onClick={() => setMovementData({ ...movementData, movement_type: 'OUT' })}
                  >
                    - Stock OUT (Dispatch)
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="movement-quantity-input">Quantity Units *</label>
                  <input
                    id="movement-quantity-input"
                    className="form-input"
                    type="number"
                    min="1"
                    required
                    value={movementData.quantity}
                    onChange={(e) => setMovementData({ ...movementData, quantity: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="movement-note-input">Audit Note / PO Number</label>
                  <input
                    id="movement-note-input"
                    className="form-input"
                    type="text"
                    placeholder="e.g. Inbound purchase order #892"
                    value={movementData.note}
                    onChange={(e) => setMovementData({ ...movementData, note: e.target.value })}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button id="movement-submit-btn" type="submit" className="btn btn-primary">
                  Confirm {movementData.movement_type} Movement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
