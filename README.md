# StockPilot — Cloud-Native Inventory Management Platform

StockPilot is an enterprise-ready, containerized inventory management platform engineered to track warehouse products, streamline stock movements (IN/OUT), enforce reorder thresholds, and provide real-time inventory analytics. Built with FastAPI, PostgreSQL, and React, StockPilot is deployed using an automated DevSecOps pipeline with GitOps delivery onto AWS EKS.

---

## Architecture Overview

```
                                +---------------------------+
                                |      Internet Users       |
                                +-------------+-------------+
                                              |
                                              v
                              +---------------+---------------+
                              |    AWS Application Load       |
                              |          Balancer             |
                              +---------------+---------------+
                                              |
                                              v
                         +--------------------+--------------------+
                         |             Nginx Ingress               |
                         |  / -> Frontend     /api -> Backend     |
                         +--------+--------------------+-----------+
                                  |                    |
                                  v                    v
                   +--------------+----+        +------+--------------+
                   |  React Frontend   |        |   FastAPI Backend   |
                   |  (2 Replicas)     |        |   (2 Replicas, HPA) |
                   +-------------------+        +------+-------+------+
                                                       |       |
                                     +-----------------+       +-----------------+
                                     |                                           |
                                     v                                           v
                         +-----------+-----------+                   +-----------+-----------+
                         |      PostgreSQL       |                   |  Prometheus & Grafana |
                         |   (StatefulSet/PVC)   |                   |    (/metrics scrap)   |
                         +-----------------------+                   +-----------------------+
```

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, psycopg v3, Pydantic v2
- **Frontend**: React 18, Vite, Vanilla Modern CSS (Responsive, Glassmorphic styling)
- **Database**: PostgreSQL 16
- **Containerization**: Docker (Multi-stage non-root images), Docker Compose
- **Continuous Integration & DevSecOps**: GitHub Actions, Pytest, Trivy (High/Critical vulnerability gating), GHCR
- **Infrastructure as Code (IaC)**: Terraform, AWS VPC, Subnets across 2 AZs, NAT Gateway, AWS EKS
- **Orchestration & Packaging**: Kubernetes, Helm 3, Ingress-Nginx, HPA, Metrics Server
- **GitOps Continuous Delivery**: ArgoCD
- **Observability**: Prometheus (kube-prometheus-stack), Grafana custom dashboards, ServiceMonitor

---

## Project Structure

```text
inventory-management/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD workflows
├── backend/                # FastAPI application, database models, Alembic, tests
├── frontend/               # React + Vite dashboard source code
├── terraform/              # Terraform AWS VPC & EKS cluster infrastructure
├── helm/
│   └── stockpilot/         # StockPilot Helm chart (Deployments, Ingress, HPA, values)
├── k8s/                    # Core Kubernetes manifests (namespace, bootstrap)
├── monitoring/             # Prometheus & Grafana configurations and dashboards
├── argocd/                 # ArgoCD Application manifests for GitOps sync
├── troubleshooting/        # Diagnostic scenarios and troubleshooting guides
├── scripts/                # Traffic generators and verification utilities
├── demo/                   # Capstone presentation deck and video walkthrough
├── docker-compose.yml      # Local full-stack orchestration
└── README.md               # Technical project documentation
```

---

## Local Development & Setup

### Prerequisites
- Docker & Docker Compose v2+
- Python 3.12+
- Node.js 20+

### Running Locally with Docker Compose
```bash
# 1. Clone repository
git clone <YOUR_REPO_URL>
cd inventory-management

# 2. Build and start services
docker compose up --build

# 3. Access endpoints
# Frontend Dashboard: http://localhost:3000
# Backend Swagger Docs: http://localhost:8000/docs
# Health Probe: http://localhost:8000/health
# Prometheus Metrics: http://localhost:8000/metrics
```

---

## Running Automated Tests

```bash
cd backend
python -m venv .venv
# Activate virtualenv (Linux/macOS: source .venv/bin/activate, Windows: .venv\Scripts\activate)
pip install -r requirements.txt
pytest -v
```

---

## CI/CD Pipeline & DevSecOps

The automated pipeline (`.github/workflows/ci-cd.yml`) enforces the following workflow:
1. **Testing**: Runs `pytest` and frontend production build on pull requests and pushes to `main`.
2. **Container Build & Trivy Scan**: Builds backend and frontend container images, executes Trivy security vulnerability scans, and fails if HIGH or CRITICAL vulnerabilities are found.
3. **Publish to GHCR**: Pushes verified container images to GitHub Container Registry tagged with the commit SHA (`${{ github.sha }}`).
4. **GitOps Bump**: Automatically updates `helm/stockpilot/values-prod.yaml` with the newly published image SHA and commits back with `[skip ci]`.

---

## Infrastructure as Code (Terraform)

AWS infrastructure is defined declaratively under `terraform/`:
- **VPC**: 2 Public Subnets, 2 Private Subnets spanning 2 Availability Zones in `ap-south-1`.
- **EKS Cluster**: Managed control plane with a managed worker node group (2 x `t3.medium`).
- **Networking**: Internet Gateway and a cost-optimized single NAT Gateway.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## Kubernetes & Helm Deployment

Deploying StockPilot onto Kubernetes via Helm:
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy via Helm
helm upgrade --install stockpilot ./helm/stockpilot -n stockpilot -f ./helm/stockpilot/values-prod.yaml
```

---

## GitOps with ArgoCD

ArgoCD continuously monitors this repository and synchronizes the deployed state in Kubernetes with `helm/stockpilot/`:
- **Application Manifest**: `argocd/application.yaml`
- **Sync Policy**: Automated with prune and self-heal enabled.

---

## Observability (Prometheus & Grafana)

StockPilot exposes native runtime and custom business metrics at `/metrics`:
- `stockpilot_stock_movements_total{type="IN|OUT"}`: Total counter of inventory stock adjustments.
- `stockpilot_low_stock_products`: Current gauge of products whose quantity has reached or dropped below reorder level.

Prometheus and Grafana are configured under `monitoring/`:
- `monitoring/prometheus-values.yaml`: Scrape configuration and ServiceMonitor discovery.
- `monitoring/grafana-dashboard.json`: 6-panel real-time operational dashboard.

---

## Troubleshooting & Failure Drills

The `troubleshooting/` directory contains intentional failure manifests used for operational runbooks:
- `troubleshooting/broken-image.yaml`: Debugging `ImagePullBackOff` and container image resolution.
- `troubleshooting/broken-service.yaml`: Debugging service selector mismatches and routing failures.

---

## Known Issues & Limitations

- Local SQLite test mocks do not validate PostgreSQL-specific dialect features (such as `RETURNING` clauses with certain custom extensions).
- Single NAT Gateway architecture in Terraform provides cost efficiency for academic demonstration but does not provide multi-AZ NAT fault tolerance.

---

## Submission & Verification Checklist

- [ ] GitHub repository URL submitted
- [ ] Application starts via `docker compose up --build`
- [ ] Pytest suite passing with 10+ tests
- [ ] Non-root Dockerfiles with multi-stage build
- [ ] GitHub Actions CI/CD with Trivy scan passing
- [ ] Images published to GHCR with Git SHA tags
- [ ] Terraform plan & AWS VPC/EKS provisioned
- [ ] Helm chart deployed on Kubernetes with Ingress & HPA
- [ ] Prometheus scraping app and Grafana dashboard populated
- [ ] ArgoCD application synchronizing GitOps state
- [ ] Mandatory presentation video uploaded to `demo/` or GitHub Releases
- [ ] Mandatory presentation slide deck committed to `demo/presentation.pptx`
