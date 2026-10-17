#!/usr/bin/env bash
# ==============================================================================
# scripts/load-test.sh — StockPilot Traffic Generator
#
# WHY:  Generates realistic HTTP traffic so that:
#       1. The HPA sees CPU load and scales the backend pods
#       2. Grafana panels show live, non-zero data for the presentation video
#       3. Prometheus target appears as "UP" and metrics fill in
#
# WHEN: Run AFTER the app is deployed and port-forwarded (or Ingress is active).
# HOW:  Uses only `curl` and `bash` — no extra tools needed.
#
# USAGE:
#   # Option A: via Ingress hostname (replace with your real hostname)
#   BASE_URL=http://stockpilot.example.com bash scripts/load-test.sh
#
#   # Option B: via kubectl port-forward (local testing)
#   kubectl port-forward svc/stockpilot-stockpilot-backend 8000:8000 -n stockpilot &
#   BASE_URL=http://localhost:8000 bash scripts/load-test.sh
#
#   # Option C: via docker compose (local dev)
#   BASE_URL=http://localhost:3000 bash scripts/load-test.sh
#
# STOP: Press Ctrl+C to stop the load test.
# ==============================================================================

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_URL="${BASE_URL:-http://localhost:8000}"
DURATION="${DURATION:-300}"       # Run for 5 minutes by default
SLEEP_BETWEEN="${SLEEP:-0.3}"     # Seconds between each request batch
REQUEST_TIMEOUT=5                  # curl timeout per request

echo "============================================================"
echo "  StockPilot Load Test"
echo "  Target : ${BASE_URL}"
echo "  Duration: ${DURATION}s (Ctrl+C to stop early)"
echo "============================================================"
echo ""

# ── Helper: silent curl, prints status code ───────────────────────────────────
hit() {
  local method="${1}"
  local path="${2}"
  local data="${3:-}"
  local status

  if [ -n "${data}" ]; then
    status=$(curl -s -o /dev/null -w "%{http_code}" \
      --max-time "${REQUEST_TIMEOUT}" \
      -X "${method}" \
      -H "Content-Type: application/json" \
      -d "${data}" \
      "${BASE_URL}${path}" 2>/dev/null || echo "ERR")
  else
    status=$(curl -s -o /dev/null -w "%{http_code}" \
      --max-time "${REQUEST_TIMEOUT}" \
      -X "${method}" \
      "${BASE_URL}${path}" 2>/dev/null || echo "ERR")
  fi
  echo "${status}"
}

# ── Seed: Create demo products if they don't exist yet ────────────────────────
echo "[seed] Creating demo products..."

PRODUCTS=(
  '{"name":"Wireless Keyboard","sku":"WKB-001","category":"Electronics","price":49.99,"quantity":150,"reorder_level":20}'
  '{"name":"USB-C Hub 7-Port","sku":"USBH-007","category":"Electronics","price":34.99,"quantity":8,"reorder_level":15}'
  '{"name":"Mechanical Pencil Set","sku":"MPS-012","category":"Stationery","price":12.50,"quantity":300,"reorder_level":50}'
  '{"name":"Ergonomic Mouse","sku":"ERM-003","category":"Electronics","price":79.99,"quantity":45,"reorder_level":10}'
  '{"name":"A4 Notebook 200pg","sku":"NB-A4-200","category":"Stationery","price":5.99,"quantity":5,"reorder_level":30}'
  '{"name":"HDMI Cable 2m","sku":"HDMI-2M","category":"Cables","price":14.99,"quantity":200,"reorder_level":40}'
)

PRODUCT_IDS=()
for product in "${PRODUCTS[@]}"; do
  response=$(curl -s --max-time "${REQUEST_TIMEOUT}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d "${product}" \
    "${BASE_URL}/api/products" 2>/dev/null || echo "{}")
  pid=$(echo "${response}" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*' || echo "")
  if [ -n "${pid}" ]; then
    PRODUCT_IDS+=("${pid}")
    echo "[seed]   Created product id=${pid}"
  fi
done

echo "[seed] Done. Product IDs: ${PRODUCT_IDS[*]:-none}"
echo ""

# ── Main Load Loop ────────────────────────────────────────────────────────────
START=$(date +%s)
ITERATION=0

echo "[load] Starting traffic generation for ${DURATION}s..."
echo ""

while true; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START ))

  if [ "${ELAPSED}" -ge "${DURATION}" ]; then
    echo ""
    echo "[load] Duration reached (${DURATION}s). Stopping."
    break
  fi

  ITERATION=$(( ITERATION + 1 ))
  echo -n "[${ELAPSED}s / iter ${ITERATION}] "

  # ── Health & stats (always-green endpoints) ───────────────────────────────
  echo -n "health=$(hit GET /health) "
  echo -n "stats=$(hit GET /api/inventory/stats) "

  # ── Product listing with and without filters ──────────────────────────────
  echo -n "list=$(hit GET /api/products) "
  echo -n "low=$(hit GET '/api/products?low_stock=true') "
  echo -n "search=$(hit GET '/api/products?search=key') "

  # ── Individual product GETs ───────────────────────────────────────────────
  if [ "${#PRODUCT_IDS[@]}" -gt 0 ]; then
    # Pick a random product from seeded list
    IDX=$(( RANDOM % ${#PRODUCT_IDS[@]} ))
    PID="${PRODUCT_IDS[$IDX]}"
    echo -n "get=${PID}:$(hit GET /api/products/${PID}) "

    # ── Stock IN movement (restocking) ──────────────────────────────────────
    echo -n "in=$(hit POST /api/products/${PID}/movements \
      '{"movement_type":"IN","quantity":5,"note":"load-test restock"}') "

    # ── Stock OUT movement (sale/dispatch) ──────────────────────────────────
    echo -n "out=$(hit POST /api/products/${PID}/movements \
      '{"movement_type":"OUT","quantity":2,"note":"load-test dispatch"}') "

    # ── Movement history ────────────────────────────────────────────────────
    echo -n "moves=$(hit GET /api/products/${PID}/movements) "
  fi

  # ── 404 probe (generates error-rate data without breaking anything) ───────
  echo -n "404=$(hit GET /api/products/999999) "

  # ── Metrics endpoint ──────────────────────────────────────────────────────
  echo -n "metrics=$(hit GET /metrics) "

  echo ""
  sleep "${SLEEP_BETWEEN}"
done

echo ""
echo "============================================================"
echo "  Load test complete."
echo "  Total iterations: ${ITERATION}"
echo "  Check Grafana for live panels."
echo "  Check kubectl get hpa -n stockpilot for scale events."
echo "============================================================"
