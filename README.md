# StockPilot — Cloud-Native Inventory Management Platform

> **DevOps Final Capstone Project** | FastAPI · React · PostgreSQL · Docker · GitHub Actions · Terraform · AWS EKS · Helm · ArgoCD · Prometheus · Grafana

StockPilot is an enterprise-ready, fully containerised inventory management platform that tracks warehouse products, manages stock IN/OUT movements, enforces reorder thresholds, and provides real-time analytics. Every layer — from source code to cloud infrastructure — is automated through a GitOps DevSecOps pipeline.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              Internet Users                                 │
└─────────────────────────────────┬──────────────────────────────────────────┘
                                  │ HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              AWS Application Load Balancer (Ingress-Nginx)                  │
│         /api/* ──────────────────┐   /* ──────────────────────────────┐    │
└──────────────────────────────────┼──────────────────────────────────┬─┘    │
                                   │                                  │
         ┌─────────────────────────▼────────┐   ┌────────────────────▼──────┐
         │      FastAPI Backend             │   │   React Frontend           │
         │  (2 Replicas · HPA · non-root)   │   │  (2 Replicas · Nginx 8080) │
         │  /health  /ready  /metrics       │   │  Served as static SPA      │
         └────────┬──────────────┬──────────┘   └───────────────────────────┘
                  │              │
     ┌────────────▼──┐   ┌───────▼──────────────┐
     │  PostgreSQL   │   │ Prometheus & Grafana  │
     │  (PVC · 5Gi)  │   │ ServiceMonitor scrape │
     └───────────────┘   └──────────────────────┘

CI/CD GitOps Flow:
  Push to main → GitHub Actions (test → trivy scan → push GHCR) → update values-prod.yaml → ArgoCD detects → helm upgrade → Rolling deploy
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, psycopg v3, Pydantic v2 |
| **Frontend** | React 18, Vite, Vanilla CSS (responsive, glassmorphic) |
| **Database** | PostgreSQL 16 |
| **Containerisation** | Docker (multi-stage, non-root), Docker Compose |
| **CI/CD & Security** | GitHub Actions, Pytest, Trivy (HIGH/CRITICAL gate), GHCR |
| **Infrastructure** | Terraform, AWS VPC (2 AZ), EKS, NAT Gateway |
| **Kubernetes** | Helm 3, ingress-nginx, HPA, metrics-server, PVC |
| **GitOps** | ArgoCD (automated sync, prune, selfHeal) |
| **Observability** | kube-prometheus-stack, Grafana dashboards, ServiceMonitor |

---

## Project Structure

```text
inventory-management/
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions: test → scan → push → gitops bump
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app, all endpoints, Prometheus metrics
│   │   ├── models.py           # SQLAlchemy ORM: products, stock_movements
│   │   ├── schemas.py          # Pydantic v2 request/response schemas
│   │   ├── db.py               # Database engine, session, get_db dependency
│   │   └── config.py           # Settings from environment variables
│   ├── alembic/
│   │   └── versions/           # Database migration files
│   ├── tests/
│   │   ├── conftest.py         # SQLite test DB + FastAPI dependency override
│   │   └── test_api.py         # 12 tests covering all critical paths
│   ├── Dockerfile              # Non-root slim Python image
│   ├── requirements.txt        # Pinned Python dependencies
│   └── .env.example            # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main dashboard: sidebar, KPI cards, product table
│   │   ├── main.jsx            # React entry point
│   │   └── styles.css          # Full responsive CSS with transitions
│   ├── Dockerfile              # Multi-stage: Node build → nginx-unprivileged
│   ├── nginx.conf              # Nginx: serve SPA + proxy /api to backend
│   └── vite.config.js          # Vite with /api dev proxy
├── terraform/
│   ├── versions.tf             # Terraform ≥1.7.0, AWS provider ~>5.50
│   ├── providers.tf            # AWS provider + default tags
│   ├── variables.tf            # All variables with descriptions and defaults
│   ├── main.tf                 # VPC module + EKS module
│   ├── outputs.tf              # vpc_id, cluster_name, kubeconfig command
│   ├── terraform.tfvars.example # Safe to commit — no secrets
│   └── README.md               # Cost warning + usage steps + screenshot guide
├── helm/
│   └── stockpilot/
│       ├── Chart.yaml          # Chart metadata
│       ├── values.yaml         # Default values (all environments)
│       ├── values-dev.yaml     # Dev overrides (single replica, no ingress)
│       ├── values-prod.yaml    # Prod overrides (auto-updated by CI/CD)
│       └── templates/
│           ├── _helpers.tpl            # fullname, labels helpers
│           ├── backend-deployment.yaml # 2 replicas, probes, non-root, Secret env
│           ├── backend-service.yaml    # ClusterIP :8000
│           ├── frontend-deployment.yaml# 2 replicas, probes, non-root
│           ├── frontend-service.yaml   # ClusterIP :8080
│           ├── postgres.yaml           # Secret + PVC + Deployment + Service
│           ├── ingress.yaml            # /api→backend, /→frontend
│           ├── hpa.yaml                # CPU-based, min 2 max 6
│           └── servicemonitor.yaml     # Prometheus scrape config
├── k8s/
│   └── namespace.yaml          # stockpilot namespace with monitoring label
├── monitoring/
│   ├── prometheus-values.yaml  # kube-prometheus-stack helm values
│   └── grafana-dashboard.json  # 6-panel importable Grafana dashboard
├── argocd/
│   └── application.yaml        # ArgoCD Application: automated sync + prune
├── troubleshooting/
│   ├── broken-image.yaml       # Scenario: ImagePullBackOff
│   ├── broken-service.yaml     # Scenario: Service selector mismatch → 503
│   └── README.md               # Diagnose-and-fix runbook
├── scripts/
│   └── load-test.sh            # curl-only traffic generator for HPA + Grafana demo
├── demo/
│   ├── presentation.pptx       # 10-slide capstone deck (MANDATORY)
│   ├── VIDEO_SCRIPT.md         # Ordered timed walkthrough script
│   └── SCREENSHOTS_CHECKLIST.md# Every screenshot the rubric requires
├── docker-compose.yml          # Local full-stack: postgres + backend + frontend
├── .gitignore                  # Excludes .env, __pycache__, *.tfstate, etc.
└── README.md                   # This file
```

---

## Local Development & Setup

### Prerequisites
- Docker Desktop (with Docker Compose v2+)
- Python 3.12+ (for running tests locally)
- Node.js 22+ (for frontend development)

### Run the Full Stack Locally

```bash
# 1. Clone the repository
git clone https://github.com/manohar180/Inventory-management.git
cd Inventory-management

# 2. Copy and configure environment variables (optional for local compose)
cp backend/.env.example backend/.env

# 3. Start all services (postgres + backend + frontend)
docker compose up --build

# 4. Access the application
open http://localhost:3000          # React dashboard
open http://localhost:8000/docs     # FastAPI Swagger UI
open http://localhost:8000/health   # Health probe → {"status":"healthy"}
open http://localhost:8000/metrics  # Prometheus metrics
```

All three services start in the correct order:
- **postgres** starts first with a health check
- **backend** waits for postgres to be healthy, then runs `alembic upgrade head` before starting
- **frontend** starts and proxies `/api` to the backend

---

## Running Automated Tests

```bash
cd backend

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run the full test suite
pytest -v
# Expected: 12+ tests passing, using SQLite in-memory DB (no postgres needed)
```

Tests cover: health, root, create product, duplicate SKU (409), list/search, get 404, update, delete, stock IN, stock OUT, OUT-exceeds-stock (400), and inventory stats.

---

## CI/CD Pipeline & DevSecOps

The pipeline (`.github/workflows/ci-cd.yml`) runs automatically on every push to `main`:

```
Push to main
    │
    ├─► Job 1: test
    │     ├─ pytest (fails build on test failure)
    │     └─ npm run build (validates frontend compiles)
    │
    ├─► Job 2: build-scan-publish  [needs: test]
    │     ├─ docker build backend + frontend
    │     ├─ trivy scan both images (HIGH/CRITICAL → exit 1)
    │     └─ docker push to GHCR with SHA tag (only if scans clean)
    │
    └─► Job 3: gitops-bump  [needs: build-scan-publish, push to main only]
          ├─ update helm/stockpilot/values-prod.yaml with new SHA
          └─ git commit "[skip ci]" → ArgoCD picks up the change
```

**GitHub repository settings required:**
- Settings → Actions → General → Workflow permissions → **Read and write**
- Settings → Packages → stockpilot-backend/frontend → **Make public**

---

## Infrastructure as Code (Terraform)

AWS infrastructure lives in `terraform/` and is provisioned with:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # Edit region/cluster name if needed
terraform init
terraform plan     # Screenshot this for M7 submission
terraform apply    # Creates VPC + EKS (~15–20 min, costs ~$5/day)

# After evaluation — DESTROY to avoid charges
terraform destroy
```

**What gets created:**

| Resource | Details |
|----------|---------|
| VPC | `10.30.0.0/16` — 2 public + 2 private subnets, 2 AZs |
| Internet Gateway | Public subnet internet access |
| NAT Gateway | Single NAT (cost-saving) for private subnet egress |
| EKS Cluster | Kubernetes 1.31, public endpoint |
| Node Group | 2× t3.medium (scales to 4) |
| EKS Add-ons | CoreDNS, kube-proxy, vpc-cni, ebs-csi-driver |

⚠️ **Always run `terraform destroy` after evaluation to avoid AWS charges.**

---

## Kubernetes & Helm Deployment

```bash
# 0. Configure kubectl (after terraform apply)
aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks

# 1. Install prerequisites (once per cluster)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system

# 2. Create namespace
kubectl apply -f k8s/namespace.yaml

# 3. Deploy StockPilot
helm upgrade --install stockpilot helm/stockpilot \
  --namespace stockpilot \
  --values helm/stockpilot/values-prod.yaml

# 4. Verify
kubectl get pods    -n stockpilot   # All Running
kubectl get svc     -n stockpilot   # Services listed
kubectl get ingress -n stockpilot   # ADDRESS populated
kubectl get hpa     -n stockpilot   # TARGETS showing %
helm list           -n stockpilot   # Chart deployed
```

---

## GitOps with ArgoCD

ArgoCD watches `helm/stockpilot/` and auto-deploys when `values-prod.yaml` changes.

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get admin password
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo

# Access UI
kubectl port-forward svc/argocd-server 8080:443 -n argocd
# https://localhost:8080  →  admin / <password above>

# Apply StockPilot Application
kubectl apply -f argocd/application.yaml -n argocd
```

**GitOps flow:** push code → CI/CD updates `values-prod.yaml` → ArgoCD detects → `helm upgrade` → rolling deploy → zero downtime.

---

## Observability (Prometheus & Grafana)

```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --values monitoring/prometheus-values.yaml

# Access Prometheus (check Targets page for stockpilot → UP)
kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring
# http://localhost:9090/targets

# Access Grafana
kubectl port-forward svc/kube-prometheus-stack-grafana 3000:3000 -n monitoring
# http://localhost:3000  →  admin / StockPilot@Grafana2024
# Import: Dashboards → Import → Upload monitoring/grafana-dashboard.json

# Generate traffic to populate dashboard panels
BASE_URL=http://localhost:8000 bash scripts/load-test.sh
```

**Custom metrics exposed at `/metrics`:**
- `stockpilot_stock_movements_total{type="IN|OUT"}` — Counter of all stock adjustments
- `stockpilot_low_stock_products` — Gauge of products at or below reorder level

---

## Troubleshooting

See [`troubleshooting/README.md`](troubleshooting/README.md) for full runbooks.

**Quick diagnostic commands:**
```bash
kubectl get pods -n stockpilot                          # Pod status
kubectl describe pod <name> -n stockpilot               # Events + config
kubectl logs <name> -n stockpilot                       # Container logs
kubectl get endpoints -n stockpilot                     # Empty = selector mismatch
kubectl rollout undo deployment/<name> -n stockpilot    # Roll back
kubectl get events -n stockpilot --sort-by=lastTimestamp # Timeline of events
```

---

## Known Issues & Limitations

- **SQLite test dialect**: Test suite uses SQLite in-memory DB. Certain PostgreSQL-specific types (e.g., `RETURNING` with advanced extensions) are not exercised in CI.
- **Single NAT Gateway**: Cost-optimised for demo; not multi-AZ fault tolerant for production.
- **Starlette CVE mitigation**: `requirements.txt` pins `starlette>=1.3.1` to ensure all HIGH CVEs (CVE-2025-62727, CVE-2026-48818, CVE-2026-54283) are resolved in the Docker image.
- **Grafana password**: Demo password in `monitoring/prometheus-values.yaml` — rotate before any public deployment.

---

## Screenshots (Submission Evidence)

Add your screenshots here after running each component:

| Step | Screenshot file | Status |
|------|----------------|--------|
| App running in browser | `demo/screenshots/app-ui.png` | ☐ |
| pytest passing | `demo/screenshots/pytest-pass.png` | ☐ |
| GitHub Actions green | `demo/screenshots/ci-green.png` | ☐ |
| GHCR packages page | `demo/screenshots/ghcr-packages.png` | ☐ |
| terraform plan | `demo/screenshots/terraform-plan.png` | ☐ |
| AWS Console VPC | `demo/screenshots/aws-vpc.png` | ☐ |
| AWS Console EKS | `demo/screenshots/aws-eks.png` | ☐ |
| kubectl get pods (Running) | `demo/screenshots/kubectl-pods.png` | ☐ |
| helm list | `demo/screenshots/helm-list.png` | ☐ |
| Prometheus Targets UP | `demo/screenshots/prometheus-targets.png` | ☐ |
| Grafana live dashboard | `demo/screenshots/grafana-dashboard.png` | ☐ |
| ArgoCD synced | `demo/screenshots/argocd-synced.png` | ☐ |

---

## Submission Checklist

- [ ] GitHub repository URL submitted (public)
- [ ] `docker compose up --build` starts all 3 services
- [ ] 4+ REST API endpoints implemented
- [ ] Alembic migration file present
- [ ] `pytest` passes (12+ tests)
- [ ] `backend/Dockerfile` builds — non-root
- [ ] `frontend/Dockerfile` multi-stage — non-root
- [ ] GitHub Actions runs on push to main
- [ ] Trivy scan in pipeline, fails on HIGH/CRITICAL
- [ ] Images in GHCR with SHA tags (not `latest`)
- [ ] `terraform plan` output screenshot submitted
- [ ] VPC + EKS provisioned (AWS Console screenshot)
- [ ] `terraform destroy` completion screenshot
- [ ] `kubectl get pods` all Running
- [ ] `helm list` screenshot
- [ ] Ingress with address
- [ ] Prometheus Targets page → stockpilot UP
- [ ] Grafana dashboard with live data
- [ ] ArgoCD Application → Synced/Healthy
- [ ] `demo/presentation.pptx` committed (**MANDATORY**)
- [ ] Presentation video uploaded to `demo/` or GitHub Release (**MANDATORY**)
