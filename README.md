# StockPilot — Cloud-Native Inventory Management Platform

A full-stack inventory management system built with **FastAPI, React, and PostgreSQL**, supported by a DevSecOps delivery pipeline using Docker, GitHub Actions, Trivy, Terraform, Kubernetes, Helm, ArgoCD, Prometheus, and Grafana.

StockPilot helps warehouse operators manage products, track stock movements, identify low-stock items, and monitor inventory metrics through a responsive dashboard. The project also demonstrates how an application can be tested, packaged, scanned, deployed, and monitored using modern cloud-native practices.

<p align="center">
  <img src="demo/screenshots/app-dashboard.png" alt="StockPilot inventory dashboard" width="100%">
</p>

<p align="center">
  <strong>Full-Stack Development · Infrastructure as Code · DevSecOps · GitOps · Observability</strong>
</p>

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Application Screenshots](#application-screenshots)
- [API Reference](#api-reference)
- [Getting Started](#getting-started)
- [Testing](#testing)
- [Docker and Containerization](#docker-and-containerization)
- [CI/CD and DevSecOps](#cicd-and-devsecops)
- [Infrastructure as Code](#infrastructure-as-code)
- [Kubernetes and Helm](#kubernetes-and-helm)
- [GitOps with ArgoCD](#gitops-with-argocd)
- [Monitoring and Observability](#monitoring-and-observability)
- [Repository Structure](#repository-structure)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)
- [Cleanup and Cost Management](#cleanup-and-cost-management)
- [Future Improvements](#future-improvements)

---

## Project Overview

StockPilot is designed to demonstrate both application development and the engineering practices required to deliver and operate an application in a cloud-native environment.

The application provides inventory management capabilities through a React dashboard and a REST API. PostgreSQL stores product and stock movement records, while SQLAlchemy and Alembic handle database access and schema migrations.

Around the application, the project implements an automated delivery workflow that tests the code, builds container images, scans them for vulnerabilities, publishes versioned images to GitHub Container Registry (GHCR), and updates Helm configuration for ArgoCD to reconcile.

### What the project demonstrates

- Building a full-stack application with a REST API and relational database.
- Managing database schema changes through migrations.
- Writing automated API tests.
- Containerizing services using Docker.
- Automating validation and delivery through GitHub Actions.
- Scanning container images with Trivy.
- Defining cloud infrastructure using Terraform.
- Deploying services using Kubernetes and Helm.
- Applying GitOps principles with ArgoCD.
- Collecting application metrics with Prometheus and visualizing them in Grafana.

## Key Features

### Inventory management

- Create, view, update, and delete products.
- Assign each product a unique SKU.
- Store product names, categories, prices, quantities, and reorder levels.
- Search products and filter low-stock items.
- Record stock IN and OUT transactions.
- Maintain a history of stock movements.
- Reject stock OUT transactions that exceed the available quantity.
- Display inventory statistics, including product counts, stock quantities, low-stock alerts, and inventory value.

### Application reliability

- REST API built with FastAPI.
- PostgreSQL database with SQLAlchemy ORM.
- Alembic database migrations.
- Request validation using Pydantic.
- Health and readiness endpoints.
- Automated tests using Pytest.
- Prometheus instrumentation for application monitoring.

### DevOps and cloud-native delivery

- Docker Compose for local development.
- Separate backend and frontend container images.
- GitHub Actions for automated testing and delivery.
- Trivy vulnerability scanning.
- GitHub Container Registry for image publishing.
- Terraform-managed AWS infrastructure.
- Kubernetes deployments, services, probes, and Helm templates.
- ArgoCD-based GitOps deployment.
- Prometheus and Grafana monitoring.
- Troubleshooting manifests for common Kubernetes failures.

---

## Architecture

### Application architecture

```text
                       Users / Browser
                              |
                              v
                       React Frontend
                         Nginx :8080
                              |
                              v
                       FastAPI Backend
                           :8000
                         /       \
                        v         v
                  PostgreSQL   /metrics
                     :5432         |
                                   v
                               Prometheus
                                   |
                                   v
                                 Grafana
```

In a Kubernetes deployment, the ingress controller routes application traffic to the frontend or backend services. The backend connects to PostgreSQL and exposes application metrics for Prometheus to scrape.

### CI/CD and GitOps architecture

```text
Developer pushes code to main
              |
              v
       GitHub Actions
              |
              v
     Automated quality gates
       - Backend tests
       - Frontend build
              |
              v
       Build Docker images
              |
              v
        Trivy security scan
              |
              v
       Publish images to GHCR
              |
              v
     Update Helm image tags
       with commit SHA
              |
              v
          ArgoCD detects
          Git repository change
              |
              v
       Reconcile Kubernetes
       with desired Git state
```

The workflow separates image building and publishing from Kubernetes deployment. The CI pipeline updates the desired image versions in Git, and ArgoCD is responsible for reconciling the cluster with that configuration.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite, CSS |
| Backend | Python 3.12, FastAPI, Uvicorn |
| Database | PostgreSQL 16 |
| ORM and migrations | SQLAlchemy, Alembic |
| Validation | Pydantic |
| Testing | Pytest, HTTPX |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Container registry | GitHub Container Registry |
| Security scanning | Trivy |
| Infrastructure as Code | Terraform, AWS |
| Container orchestration | Kubernetes, Amazon EKS |
| Deployment packaging | Helm |
| GitOps | ArgoCD |
| Metrics | Prometheus |
| Dashboards | Grafana |

---

## Application Screenshots

The following screenshots are included in the repository under `demo/screenshots/`.

### Inventory dashboard

![StockPilot dashboard](demo/screenshots/app-dashboard.png)

The dashboard provides an overview of inventory and helps users identify products that require attention.

### Product creation and editing

![Product creation and editing modal](demo/screenshots/app-modal.png)

### Stock movements

![Stock movement interface](demo/screenshots/app-stock-movement.png)

### Low-stock monitoring

![Low-stock products](demo/screenshots/app-low-stock.png)

### REST API documentation

![FastAPI Swagger UI](demo/screenshots/api-swagger.png)

### CI/CD pipeline

![GitHub Actions workflow](demo/screenshots/ci-all-green.png)

### Kubernetes deployment

![Kubernetes pods](demo/screenshots/kubectl-pods.png)

### Monitoring dashboard

![Grafana dashboard](demo/screenshots/grafana-dashboard.png)

Additional infrastructure, CI/CD, Helm, and monitoring evidence is available in the `demo/screenshots/` directory.

---

## API Reference

When the backend is running, interactive API documentation is available at:

**Swagger UI:** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Application health check |
| GET | `/ready` | Readiness check, including database connectivity |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/products` | List products |
| POST | `/api/products` | Create a product |
| GET | `/api/products/{id}` | Retrieve a product |
| PUT | `/api/products/{id}` | Update a product |
| DELETE | `/api/products/{id}` | Delete a product |
| POST | `/api/products/{id}/movements` | Record a stock movement |
| GET | `/api/products/{id}/movements` | Retrieve stock movement history |
| GET | `/api/inventory/stats` | Retrieve inventory statistics |

Product listing supports search and low-stock filtering through the available query parameters.

### Example health check

```bash
curl http://localhost:8000/health
```

### Example: list products

```bash
curl http://localhost:8000/api/products
```

### Example: retrieve inventory statistics

```bash
curl http://localhost:8000/api/inventory/stats
```

The API uses appropriate HTTP responses for conditions such as missing products, duplicate SKUs, invalid requests, and insufficient stock.

---

## Getting Started

### Prerequisites

For the simplest setup, install:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose v2 or later

Python 3.12 and Node.js 22 are useful if you want to run backend tests or develop the frontend outside Docker.

### 1. Clone the repository

```bash
git clone https://github.com/manohar180/Inventory-management.git
cd Inventory-management
```

### 2. Start the application

```bash
docker compose up --build
```

Docker Compose builds the application images and starts PostgreSQL, the backend, and the frontend.

The backend waits for PostgreSQL to become healthy before starting. Its startup command applies the Alembic migrations before launching the API.

### 3. Open the application

| Service | URL |
|---|---|
| StockPilot dashboard | http://localhost:3000 |
| FastAPI Swagger UI | http://localhost:8000/docs |
| API health check | http://localhost:8000/health |
| API readiness check | http://localhost:8000/ready |
| Prometheus metrics endpoint | http://localhost:8000/metrics |

### 4. Stop the application

```bash
docker compose down
```

To also delete the local PostgreSQL data volume:

```bash
docker compose down -v
```

**Warning:** Removing the volume permanently deletes the database data stored in that Docker volume.

---

## Testing

The backend test suite is located in `backend/tests/`.

It covers application health, database readiness, product CRUD operations, validation, duplicate SKUs, product search, low-stock filtering, stock movements, movement history, and inventory statistics.

The test configuration uses an isolated SQLite database rather than the PostgreSQL database used by the application.

### Run tests locally

From the repository root:

**Windows PowerShell**

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
pytest -v
```

**Linux or macOS**

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
pytest -v
```

Review the final Pytest summary to confirm the actual number of passing tests.

The GitHub Actions workflow also runs the backend tests and frontend production build before proceeding to the image publishing stage.

---

## Docker and Containerization

The project uses separate Docker images for the backend and frontend.

### Backend

The backend container uses Python and Uvicorn to run the FastAPI application. It installs the backend dependencies and runs database migrations during startup.

### Frontend

The frontend uses a multi-stage Docker build:

1. A Node.js stage installs dependencies and builds the React application.
2. An Nginx runtime stage serves the generated static assets.

This avoids shipping the Node.js build environment in the frontend runtime image.

### Docker Compose services

| Service | Purpose | Local port |
|---|---|---|
| `postgres` | PostgreSQL database | `5432` |
| `backend` | FastAPI REST API | `8000` |
| `frontend` | React application served by Nginx | `3000` |

The Compose configuration uses a health check for PostgreSQL and a shared Docker network for communication between services.

---

## CI/CD and DevSecOps

The workflow is defined in `.github/workflows/ci-cd.yml`.

It runs on pushes to `main` and pull requests targeting `main`. Documentation-only changes covered by the configured path exclusions do not trigger the push workflow.

### Pipeline stages

**Stage 1 — Test and build validation**

- Installs backend dependencies.
- Runs the Pytest suite.
- Installs frontend dependencies using `npm ci`.
- Runs the frontend production build.

**Stage 2 — Build, scan, and publish**

- Builds the backend Docker image.
- Builds the frontend Docker image.
- Scans both images using Trivy.
- Publishes the images to GHCR after successful scans on pushes to `main`.

The configured Trivy policy checks HIGH and CRITICAL vulnerabilities and uses `--ignore-unfixed` to skip findings without an available fix.

**Stage 3 — GitOps version update**

- Updates the backend and frontend image tags in `helm/stockpilot/values-prod.yaml`.
- Uses the Git commit SHA as the image version.
- Commits and pushes the updated Helm values.
- Allows ArgoCD to detect the change and reconcile the deployment.

### Container image naming

The workflow publishes images using the following naming convention:

```text
ghcr.io/manohar180/stockpilot-backend:<commit-sha>
ghcr.io/manohar180/stockpilot-frontend:<commit-sha>
```

The actual published tags should be verified in the repository's GitHub Packages page.

### Required GitHub configuration

Check the following settings if the workflow cannot publish packages or push the GitOps update:

- Repository Actions permissions allow the required workflow writes.
- The workflow has the necessary `packages: write` permission for GHCR.
- The GitOps job has `contents: write`.
- The published packages are accessible to the cluster, or registry credentials are configured when required.

The security scan is a delivery gate: a failed scan prevents the normal image publishing path from proceeding.

---

## Infrastructure as Code

The `terraform/` directory contains the Terraform configuration for provisioning AWS infrastructure.

The configuration uses the AWS provider and community VPC and EKS modules.

### Infrastructure components

- Virtual Private Cloud (VPC).
- Public and private subnets across Availability Zones.
- Internet Gateway and NAT Gateway.
- Amazon EKS cluster.
- Managed Kubernetes node group.
- Required EKS add-ons.
- Network configuration and cluster outputs.

The committed example variables use the Mumbai AWS region (`ap-south-1`). Confirm the region and availability zones in your own Terraform variables before applying.

### Provision infrastructure

```bash
cd terraform

cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` as needed, then run:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Review the plan carefully before approving the apply operation.

### Configure kubectl

For the default example region and cluster name:

```bash
aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks
kubectl get nodes
```

Use the actual region and cluster name if you changed the Terraform variables.

**AWS cost warning:** EKS control planes, EC2 worker nodes, NAT Gateways, and load balancers can incur charges while running. Destroy resources after the evaluation when they are no longer needed.

---

## Kubernetes and Helm

The Helm chart is located in `helm/stockpilot/`.

It defines the Kubernetes resources required to deploy the frontend, backend, and PostgreSQL.

### Deployment components

- Backend Deployment and ClusterIP Service.
- Frontend Deployment and ClusterIP Service.
- PostgreSQL Deployment, Service, and credential Secret.
- Ingress rules for frontend and API routing.
- Liveness and readiness probes.
- Optional Horizontal Pod Autoscaler configuration.
- Optional ServiceMonitor for Prometheus.

The chart includes environment-specific values:

| File | Purpose |
|---|---|
| `values.yaml` | Default configuration |
| `values-dev.yaml` | Development overrides |
| `values-prod.yaml` | Production image overrides used by the CI/CD workflow |

### Install prerequisites

Configure `kubectl` to use the target cluster, then install the ingress controller and metrics server.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

helm upgrade --install metrics-server metrics-server/metrics-server \
  --namespace kube-system
```

Install the monitoring stack before the application if you want Prometheus to discover the application's ServiceMonitor.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/prometheus-values.yaml
```

### Deploy StockPilot

```bash
kubectl apply -f k8s/namespace.yaml

helm upgrade --install stockpilot helm/stockpilot \
  --namespace stockpilot \
  --values helm/stockpilot/values-prod.yaml
```

The production values must point to images that exist in GHCR and are accessible to Kubernetes.

### Verify the deployment

```bash
kubectl get pods -n stockpilot
kubectl get services -n stockpilot
kubectl get ingress -n stockpilot
kubectl get hpa -n stockpilot
helm list -n stockpilot
```

The expected pod count depends on the active values, replica settings, and deployment configuration. Confirm the actual desired and ready replica counts rather than assuming every environment runs the same number of pods.

### Validate the Helm chart

```bash
helm lint helm/stockpilot
```

For a rendered-manifest check:

```bash
helm template stockpilot helm/stockpilot \
  --namespace stockpilot \
  --values helm/stockpilot/values-prod.yaml
```

---

## GitOps with ArgoCD

ArgoCD configuration is stored in `argocd/application.yaml`.

The Application tracks the repository's `main` branch and the `helm/stockpilot` chart. Its automated sync policy enables pruning and self-healing.

### Install ArgoCD

```bash
kubectl create namespace argocd

kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Access the ArgoCD interface

Start port forwarding:

```bash
kubectl port-forward svc/argocd-server \
  8080:443 \
  -n argocd
```

Open https://localhost:8080.

Retrieve the initial administrator password:

```bash
kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

### Apply the StockPilot Application

If StockPilot is already installed as a separate Helm release, remove or migrate that release before handing ownership to ArgoCD to avoid resource ownership conflicts.

Then apply the Application:

```bash
kubectl apply -f argocd/application.yaml
```

Check its status:

```bash
kubectl get applications -n argocd
```

The application should be verified in the ArgoCD UI for synchronization and health.

**Configuration note:** The committed ArgoCD Application explicitly sets `hpa.enabled=false`. If autoscaling is required in the ArgoCD-managed deployment, review this override and the resource requests before enabling the HPA.

---

## Monitoring and Observability

StockPilot exposes application metrics at `/metrics` and includes monitoring configuration in the `monitoring/` directory.

### Prometheus

The `monitoring/prometheus-values.yaml` file configures the kube-prometheus-stack installation, including ServiceMonitor discovery and resource settings.

Access Prometheus with port forwarding:

```bash
kubectl port-forward \
  svc/kube-prometheus-stack-prometheus \
  9090:9090 \
  -n monitoring
```

Open http://localhost:9090/targets and verify that the StockPilot target is present and healthy.

### Grafana

Start port forwarding:

```bash
kubectl port-forward \
  svc/kube-prometheus-stack-grafana \
  3000:3000 \
  -n monitoring
```

Open http://localhost:3000.

Import `monitoring/grafana-dashboard.json` through the Grafana dashboard import interface. Use the configured credentials for the environment and change the demo password before any public deployment.

### Application metrics

The backend exposes custom metrics for inventory activity, including:

- `stockpilot_stock_movements_total` — stock movement counter by movement type.
- `stockpilot_low_stock_products` — gauge of products at or below their reorder threshold.

The Prometheus instrumentation also collects HTTP request and latency metrics.

### Generate demonstration traffic

The repository includes `scripts/load-test.sh` for generating requests.

For example, from a Bash-compatible shell:

```bash
BASE_URL=http://localhost:8000 DURATION=30 bash scripts/load-test.sh
```

Use the correct reachable API URL for your environment. In Kubernetes, the local port may need to be forwarded to the backend service first.

---

## Repository Structure

```text
Inventory-management/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── db.py
│   │   └── config.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_api.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── vite.config.js
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── versions.tf
│   └── terraform.tfvars.example
├── helm/
│   └── stockpilot/
│       ├── templates/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       └── values-prod.yaml
├── k8s/
│   └── namespace.yaml
├── argocd/
│   └── application.yaml
├── monitoring/
│   ├── prometheus-values.yaml
│   └── grafana-dashboard.json
├── scripts/
│   └── load-test.sh
├── troubleshooting/
│   ├── broken-image.yaml
│   ├── broken-service.yaml
│   └── README.md
├── demo/
│   ├── screenshots/
│   ├── presentation.pptx
│   ├── SCREENSHOTS_CHECKLIST.md
│   └── VIDEO_SCRIPT.md
├── docker-compose.yml
└── README.md
```

---

## Troubleshooting

### Backend cannot connect to PostgreSQL

- Check the PostgreSQL container status.
- Review the `DATABASE_URL` environment variable.
- Confirm that the database health check passes.
- Review backend logs.

```bash
docker compose ps
docker compose logs backend
docker compose logs postgres
```

### Kubernetes pod is stuck in ImagePullBackOff

```bash
kubectl get pods -n stockpilot
kubectl describe pod <pod-name> -n stockpilot
```

Check the image repository, tag, registry access, and pod events.

### Service has no endpoints

```bash
kubectl get services -n stockpilot
kubectl get endpoints -n stockpilot
kubectl get pods -n stockpilot --show-labels
```

Compare the Service selector with the labels on the target pods.

### Application is not ready

```bash
kubectl describe pod <pod-name> -n stockpilot
kubectl logs <pod-name> -n stockpilot
kubectl get events -n stockpilot --sort-by=.lastTimestamp
```

Check readiness probe failures, environment variables, database connectivity, and startup logs.

For more detailed troubleshooting, see [`troubleshooting/README.md`](troubleshooting/README.md).

---

## Known Limitations

StockPilot is an educational cloud-native capstone project. The following items should be addressed before treating it as a production system.

| Area | Current consideration |
|---|---|
| Database persistence | The Kubernetes PostgreSQL manifest uses `emptyDir`; database data can be lost when the pod is replaced. |
| Database high availability | The demo database deployment is not a highly available managed database service. |
| Secrets | Demo credentials are present in configuration values and should be replaced with a proper secrets-management solution. |
| Transport security | Configure TLS and a real domain before exposing the application publicly. |
| Concurrent stock updates | Stock movement operations should use suitable database locking or atomic updates to prevent concurrent requests from overselling stock. |
| Automated tests | The test suite uses SQLite, so PostgreSQL-specific behaviour is not fully covered. |
| Vulnerability scanning | The Trivy policy ignores unfixed vulnerabilities; scan results should be reviewed regularly. |
| Autoscaling | The ArgoCD Application currently disables the HPA through a Helm parameter. |
| AWS cost and availability | A single NAT Gateway and demo-oriented infrastructure are not a fully resilient production design. |

These limitations are documented to distinguish a working capstone implementation from a production-hardened service.

---

## Cleanup and Cost Management

If you created AWS resources for a demonstration, clean them up when finished.

First, remove the StockPilot Application and associated resources according to the current ArgoCD ownership state. Remove the ingress controller and wait for its AWS load balancer to be deleted before destroying the VPC.

After checking that the cluster is no longer needed:

```bash
cd terraform
terraform destroy
```

Review the destruction plan before confirming. Then check the AWS Console for remaining EKS clusters, EC2 instances, NAT Gateways, Elastic IP addresses, and load balancers.

Do not run `terraform destroy` against infrastructure that other applications or users depend on.

---

## Future Improvements

Potential next steps include:

- Use Amazon RDS or persistent EBS-backed storage for PostgreSQL.
- Manage secrets with AWS Secrets Manager and an external-secrets integration.
- Enable TLS using cert-manager and a domain name.
- Add database-backed integration tests to CI.
- Improve concurrency handling for stock updates.
- Add role-based authentication and authorization.
- Configure alerting for application failures and resource saturation.
- Enable and validate Kubernetes autoscaling where appropriate.
- Add a reproducible end-to-end deployment test.
- Add a recorded demonstration showing the complete CI/CD and GitOps workflow.

---

## Project Resources

- **GitHub repository:** https://github.com/manohar180/Inventory-management
- **Backend API documentation:** http://localhost:8000/docs (when running locally)
- **Infrastructure configuration:** [`terraform/`](terraform/)
- **Kubernetes Helm chart:** [`helm/stockpilot/`](helm/stockpilot/)
- **CI/CD workflow:** [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml)
- **Monitoring configuration:** [`monitoring/`](monitoring/)
- **Demonstration evidence:** [`demo/screenshots/`](demo/screenshots/)
- **Presentation:** [`demo/presentation.pptx`](demo/presentation.pptx)

---

*StockPilot — Inventory management with automated delivery, cloud-native deployment, and observability.*