Table of Contents
Overview
Architecture
Tech Stack
Repository Structure
API Reference
Quick Start (Docker Compose)
Testing
CI/CD Pipeline and DevSecOps
Containers
Infrastructure as Code (Terraform)
Kubernetes and Helm Deployment
GitOps with ArgoCD
Observability (Prometheus and Grafana)
Troubleshooting Lab
Evidence and Screenshots
Known Issues and Limitations
Cleanup


1. Overview

StockPilot is an inventory management system for a small warehouse. It keeps a product catalogue, records every stock IN and OUT movement in a ledger, flags products that fall to their reorder level, and shows live inventory statistics on a dashboard.

The application is intentionally small. The real goal of this project is the delivery platform around it: every change that reaches the cluster is tested, scanned, containerised, versioned by Git commit SHA and rolled out automatically.

Layer	What it does
Application	FastAPI REST API, React dashboard, PostgreSQL with Alembic migrations
Quality gate	20 automated tests on an isolated database, run before anything is built
Security gate	Trivy scans both images and fails the pipeline on HIGH or CRITICAL findings
Packaging	Multi-stage, non-root Docker images pushed to GHCR, tagged with the commit SHA
Infrastructure	Terraform builds the AWS VPC and EKS cluster from code
Deployment	A Helm chart deployed by ArgoCD (GitOps), with probes, autoscaling and an Ingress
Observability	Prometheus scrapes custom and default metrics, Grafana shows a 6-panel dashboard
Key features
Product CRUD with unique SKU enforcement (409 Conflict on duplicates)
Stock IN / OUT ledger. An OUT larger than current stock is rejected with 400
Low-stock detection against a per-product reorder level, with search and filter
Dashboard KPIs: total products, total units, low-stock alerts, total inventory value
Liveness (/health) and readiness (/ready, checks the database) probes
Custom Prometheus metrics: stockpilot_stock_movements_total{type} and stockpilot_low_stock_products
2. Architecture
Runtime view
HTTP
/
/api
scrape /metrics every 15s
queries
User / Browser
AWS Load Balancer
ingress-nginx
FrontendReact + Nginx :80802 replicas
BackendFastAPI :80002 replicas
PostgreSQL 16:5432
Prometheus
Grafana

The Ingress sends /api straight to the backend Service and everything else to the frontend Service. The frontend's Nginx also proxies /api to the backend, which is how the app works when only the frontend is exposed (for example with Docker Compose).

Delivery view (GitOps)
git push to main
Job 1: Testpytest + frontend build
Job 2: Build, Scan, Publishdocker build, Trivy, push toGHCR
Job 3: GitOps bumpwrite new SHA tovalues-prod.yaml
ArgoCD detects the Gitchange
Rolling update on EKS

Why GitOps? Git is the single source of truth. The pipeline never runs kubectl against the cluster. It only changes a file in Git, and ArgoCD makes the cluster match that file. Every deployment is therefore a commit that can be reviewed and rolled back.

3. Tech Stack
Area	Technology
Backend	Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, psycopg 3, Pydantic v2
Frontend	React 18, Vite 6, plain responsive CSS
Database	PostgreSQL 16
Containers	Docker multi-stage builds, Docker Compose, non-root users
CI/CD	GitHub Actions, pytest, GitHub Container Registry (GHCR)
Security	Trivy image scanning (HIGH and CRITICAL gate)
Infrastructure	Terraform, AWS VPC, Amazon EKS (managed node group), NAT gateway
Kubernetes	Helm 3, ingress-nginx, HorizontalPodAutoscaler, metrics-server
GitOps	ArgoCD (automated sync, prune, self-heal)
Observability	kube-prometheus-stack (Prometheus, Grafana), ServiceMonitor
4. Repository Structure
text
Inventory-management/
├── .github/workflows/ci-cd.yml       # test -> build/scan/publish -> gitops bump
├── backend/
│   ├── app/                          # main.py, models.py, schemas.py, db.py, config.py
│   ├── alembic/versions/             # 001_initial_stockpilot_tables.py
│   ├── tests/                        # conftest.py + test_api.py (20 tests)
│   ├── Dockerfile                    # python:3.12-slim, non-root uid 10001
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
│   ├── src/                          # App.jsx, main.jsx, styles.css
│   ├── Dockerfile                    # node build stage -> nginx-unprivileged, uid 101
│   └── nginx.conf                    # serves the SPA, proxies /api
├── terraform/                        # VPC + EKS (main.tf, variables.tf, outputs.tf, ...)
├── helm/stockpilot/                  # Chart.yaml, values*.yaml, templates/
├── k8s/namespace.yaml                # stockpilot namespace
├── argocd/application.yaml           # GitOps Application
├── monitoring/                       # prometheus-values.yaml, grafana-dashboard.json
├── troubleshooting/                  # two intentionally broken manifests + runbook
├── scripts/load-test.sh              # curl-based traffic generator
├── demo/                             # presentation.pptx, video, screenshots
├── docker-compose.yml
└── README.md
5. API Reference

Interactive documentation is available at /docs (Swagger UI) when the backend is running.

Method	Endpoint	Description
GET	/health	Liveness probe
GET	/ready	Readiness probe (runs SELECT 1 against the database)
GET	/metrics	Prometheus metrics
GET	/api/products	List products. Optional ?search= and ?low_stock=true
POST	/api/products	Create a product (409 if the SKU already exists)
GET	/api/products/{id}	Get one product (404 if missing)
PUT	/api/products/{id}	Update a product
DELETE	/api/products/{id}	Delete a product and its movement history
POST	/api/products/{id}/movements	Record stock IN or OUT (400 if OUT exceeds stock)
GET	/api/products/{id}/movements	Movement history, newest first
GET	/api/inventory/stats	Total products, total units, low-stock count, stock value

Data model

Table	Columns
products	id, name, sku (unique), category, price, quantity, reorder_level, created_at
stock_movements	id, product_id (FK, cascade delete), movement_type (IN/OUT), quantity, note, created_at
6. Quick Start (Docker Compose)

Prerequisite: Docker Desktop with Compose v2.

bash
git clone https://github.com/manohar180/Inventory-management.git
cd Inventory-management

docker compose up --build
Service	URL
React dashboard	http://localhost:3000
API docs (Swagger)	http://localhost:8000/docs
Health probe	http://localhost:8000/health
Prometheus metrics	http://localhost:8000/metrics

Startup order is handled for you: postgres starts first and must pass its healthcheck, then backend runs alembic upgrade head and starts Uvicorn, then frontend starts.

Optional: fill the app with demo data and traffic.

bash
BASE_URL=http://localhost:8000 DURATION=30 bash scripts/load-test.sh

Stop everything with docker compose down (add -v to also delete the database volume).

7. Testing

The suite has 20 tests covering health and readiness probes, the metrics endpoint, product CRUD, validation errors, duplicate SKUs, search, the low-stock filter, stock IN and OUT, the insufficient-stock rule, movement history and inventory statistics.

Tests never touch PostgreSQL. tests/conftest.py creates a fresh in-memory SQLite database for every test and swaps it in through FastAPI's dependency override.

bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v                        # expected: 20 passed
8. CI/CD Pipeline and DevSecOps

Workflow file: .github/workflows/ci-cd.yml. It runs on every push to main and on pull requests that target main. Pushes that only change documentation (README.md, demo/**, troubleshooting/**, .gitignore) are skipped on purpose.

Job	Runs on	What it does
1. Test	push and PR	Installs dependencies, runs pytest -v (the build fails if any test fails), then runs npm ci and npm run build
2. Build, Scan and Publish	after job 1	Builds both images tagged with ${{ github.sha }}, scans both with Trivy, logs in to GHCR and pushes only if both scans pass (push to main only)
3. GitOps bump	after job 2, main only	Writes the new commit SHA into helm/stockpilot/values-prod.yaml and commits it with [skip ci] so the pipeline does not loop

Images are published as:

text
ghcr.io/manohar180/stockpilot-backend:<git-sha>
ghcr.io/manohar180/stockpilot-frontend:<git-sha>

latest is never used, so every running pod can be traced back to an exact commit.

Repository settings the pipeline needs

Settings → Actions → General → Workflow permissions → Read and write
Packages → stockpilot-backend / stockpilot-frontend → Package settings → Public, so the cluster can pull the images without credentials
Security scan (Trivy)
bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 <image>

What it scans: the full contents of each built image, meaning the base operating system packages and the Python or Node dependencies installed on top of it.

What the result means: --exit-code 1 makes the step fail when a HIGH or CRITICAL vulnerability is found, so the push to GHCR never runs. An earlier run was blocked by findings in Starlette, the framework FastAPI is built on. One example is CVE-2025-62727 (CVSS 7.5, high): a crafted HTTP Range header can make FileResponse use quadratic CPU time, which allows denial of service. It is fixed in Starlette 0.49.1, so the fix was to upgrade Starlette in requirements.txt, after which both scans pass and the images are published.

--ignore-unfixed hides vulnerabilities that have no patch yet, because the team cannot act on them. This is a deliberate trade-off and is listed under Known Issues.

9. Containers
	Backend	Frontend
Base image	python:3.12-slim-bookworm	build: node:22-alpine, runtime: nginxinc/nginx-unprivileged:alpine-slim
Build style	single stage, dependencies cached by layer	multi-stage: Node builds the bundle, only static files reach the runtime image
User	appuser (uid 10001)	nginx (uid 101)
Port	8000	8080
Start command	alembic upgrade head && uvicorn app.main:app	nginx -g "daemon off;"

Both images run as non-root, and the Helm chart enforces this again with runAsNonRoot: true in each pod's securityContext.

10. Infrastructure as Code (Terraform)

Everything lives in terraform/ and uses two community modules: terraform-aws-modules/vpc/aws (5.8.1) and terraform-aws-modules/eks/aws (20.37.1).

Resource	Details
VPC	10.30.0.0/16 across 2 Availability Zones
Subnets	2 public (10.30.101.0/24, 10.30.102.0/24) and 2 private (10.30.1.0/24, 10.30.2.0/24), tagged for EKS load balancers
Gateways	Internet gateway, plus a single NAT gateway (cost saving) for private-subnet egress
EKS	Kubernetes 1.31, public and private API endpoint, cluster-creator admin access
Node group	stockpilot_nodes: default 2 × t3.medium, scales from 2 to 4, Amazon Linux 2023
Add-ons	CoreDNS, kube-proxy, VPC CNI
Region	ap-southeast-2 by default. Change aws_region and availability_zones in terraform.tfvars

Worker nodes live in the private subnets, so they cannot be reached directly from the internet. Only the load balancer sits in the public subnets.

bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # git ignores this file
terraform init
terraform validate
terraform plan                                 # 59 resources to add
terraform apply                                # roughly 15-25 minutes
aws eks update-kubeconfig --region ap-southeast-2 --name stockpilot-eks
kubectl get nodes

⚠️ Cost warning. An EKS control plane, NAT gateway and worker nodes bill by the hour. Run terraform destroy as soon as you finish (see Cleanup).

Credentials are never stored in the repository. Terraform reads them from the AWS CLI profile (aws configure). *.tfvars, *.tfstate and .terraform/ are git-ignored, and only terraform.tfvars.example is committed.

11. Kubernetes and Helm Deployment

The chart in helm/stockpilot deploys the backend, frontend and PostgreSQL into the stockpilot namespace.

Resource	Details
Backend Deployment	2 replicas, /health liveness probe, /ready readiness probe, rolling update with maxUnavailable: 0, non-root
Frontend Deployment	2 replicas, Nginx on 8080, probes on /, non-root
PostgreSQL	postgres:16-alpine Deployment, credentials in a Kubernetes Secret, emptyDir demo volume
Services	ClusterIP for backend (8000), frontend (8080) and postgres (5432), plus a small alias Service named backend for Nginx
Ingress	/api goes to the backend, / goes to the frontend (ingressClassName: nginx)
HPA	Backend, CPU target 60%, 2 to 6 replicas. Toggle with hpa.enabled
ServiceMonitor	Lets Prometheus scrape /metrics every 15 seconds. Toggle with monitoring.serviceMonitor.enabled

Values files: values.yaml (defaults), values-dev.yaml (single replica, no Ingress) and values-prod.yaml (image tags, updated automatically by the CI pipeline).

Deploy step by step

Order matters. The ServiceMonitor needs the Prometheus CRDs, so the monitoring stack goes in before the application.

bash
# 0. Point kubectl at the cluster
aws eks update-kubeconfig --region ap-southeast-2 --name stockpilot-eks

# 1. metrics-server (needed by the HPA)
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system

# 2. Ingress controller (creates the AWS load balancer)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# 3. Prometheus + Grafana (installs the ServiceMonitor CRD)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --values monitoring/prometheus-values.yaml

# 4. Namespace and application
kubectl apply -f k8s/namespace.yaml
helm upgrade --install stockpilot helm/stockpilot \
  --namespace stockpilot \
  --values helm/stockpilot/values-prod.yaml

# 5. Verify
kubectl get pods    -n stockpilot     # everything Running (2 backend, 2 frontend, 1 postgres)
kubectl get svc     -n stockpilot
kubectl get ingress -n stockpilot
helm list           -n stockpilot     # STATUS: deployed
Open the application
bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
# copy the EXTERNAL-IP hostname and open http://<that-hostname> in a browser

The load balancer takes a few minutes to become reachable. If your values file keeps the default host stockpilot.local, send the header yourself instead: curl -H "Host: stockpilot.local" http://<that-hostname>/health

12. GitOps with ArgoCD

argocd/application.yaml tells ArgoCD to watch helm/stockpilot on the main branch of this repository, using values-prod.yaml, with automated sync, prune and self-heal.

bash
kubectl create namespace argocd
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo
# Windows PowerShell:
# kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | % { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) }

# UI at https://localhost:8080  (user: admin)
kubectl port-forward svc/argocd-server -n argocd 8080:443

Let ArgoCD own the application. If you installed it with helm upgrade --install earlier, remove that release first so the two tools do not fight over the same objects:

bash
helm uninstall stockpilot -n stockpilot
kubectl apply -f argocd/application.yaml

The loop: a push to main runs the pipeline, the pipeline commits a new image SHA to values-prod.yaml, ArgoCD notices the change within a few minutes and performs a rolling update. If someone edits a resource by hand with kubectl, self-heal puts it back to what Git says.

The Application disables the HPA through hpa.enabled=false. Remove that parameter from argocd/application.yaml to let ArgoCD manage autoscaling too.

13. Observability (Prometheus and Grafana)

The backend exposes Prometheus metrics at /metrics:

Metric	Type	Meaning
http_requests_total	counter	Requests by handler, method and status class (2xx, 4xx, 5xx)
http_request_duration_seconds	histogram	Request latency, used for p95
stockpilot_stock_movements_total{type="IN|OUT"}	counter	Custom. Every recorded stock movement
stockpilot_low_stock_products	gauge	Custom. Products at or below their reorder level
bash
# Prometheus: Status > Targets must show the StockPilot backend as UP
kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring
# http://localhost:9090/targets

# Grafana: user admin, demo password is in monitoring/prometheus-values.yaml
kubectl port-forward svc/kube-prometheus-stack-grafana 3000:3000 -n monitoring
# http://localhost:3000  ->  Dashboards -> Import -> upload monitoring/grafana-dashboard.json

# Generate traffic so every panel has live data (use the Ingress hostname or a port-forward)
BASE_URL=http://<ingress-hostname> DURATION=300 bash scripts/load-test.sh

Dashboard: "StockPilot — Inventory Observability" (6 panels)

HTTP request rate (req/s)
p95 request latency (ms)
5xx error rate (%)
Requests by endpoint
Stock movements by type, IN and OUT (custom metric)
Low-stock products (custom metric)

Prometheus discovers the application through the chart's ServiceMonitor. monitoring/prometheus-values.yaml makes Prometheus watch ServiceMonitors in all namespaces, so the one in stockpilot is picked up.

14. Troubleshooting Lab

troubleshooting/ contains two intentionally broken manifests and a runbook:

Scenario	Symptom	Root cause	How to find it
broken-image.yaml	Pod stuck in ImagePullBackOff	The image tag does not exist in GHCR	kubectl describe pod, read the Events section
broken-service.yaml	Service has no endpoints, requests fail	Service selector does not match the pod labels	kubectl get endpoints, then compare with kubectl get pods --show-labels

Quick commands: kubectl get pods, kubectl describe pod <name>, kubectl logs <name> [--previous], kubectl get events --sort-by=.lastTimestamp, kubectl rollout undo deployment/<name>. See troubleshooting/README.md for the full walk-through.

15. Evidence and Screenshots
Application
Dashboard	Add product
Show Image	Show Image
Stock IN / OUT	Low-stock filter
Show Image	Show Image

Show Image

CI/CD and security

Show Image

Show Image

Show Image

Infrastructure

Show Image

Show Image

Show Image

Kubernetes

Show Image

Show Image

All evidence files
Topic	File
pytest passing	pytest-pass.png
Docker Compose running	docker-compose-up.png
Multi-stage frontend Dockerfile	dockerfile-frontend.png
CI test job	ci-test-job.png
GitOps commit by the pipeline	ci-gitops-commit.png
Commit history	github-commits.png
terraform apply	terraform-apply-complete.png
AWS VPC	aws-vpc.png
EKS node group	aws-eks-nodes.png
helm lint	helm-lint.png
Pods running	kubectl-pods.png
Ingress	kubectl-ingress.png
HPA	kubectl-hpa.png
App through the load balancer	app-via-ingress.png
/metrics output	metrics-endpoint.png
Prometheus targets UP	prometheus-targets-up.png
Grafana dashboard	grafana-dashboard.png
ArgoCD synced	argocd-synced.png
Presentation
🎬 Video walkthrough: demo/ (MP4 in the folder, or see the repository's Releases if it exceeded 100 MB)
📊 Slide deck: demo/presentation.pptx (10 slides)
📝 Video script: demo/VIDEO_SCRIPT.md
16. Known Issues and Limitations

These are known and deliberate for a time-boxed capstone. Each one has a clear production fix.

Area	Limitation	Production fix
Database storage	PostgreSQL runs in the cluster on an emptyDir volume, so data is lost if its pod is rescheduled	Amazon RDS, or an EBS CSI driver with a PersistentVolumeClaim
Secrets	Demo database and Grafana passwords sit in values files	External Secrets Operator with AWS Secrets Manager, or Sealed Secrets
TLS	The Ingress serves plain HTTP	cert-manager with a real domain name
Concurrency	Stock OUT checks the quantity without a row lock, so two simultaneous requests could oversell	SELECT ... FOR UPDATE or an atomic conditional UPDATE
Test database	Tests run on SQLite, so PostgreSQL-specific behaviour is not exercised in CI	Run tests against a PostgreSQL service container
Trivy scope	--ignore-unfixed skips vulnerabilities that have no patch yet	Review unfixed findings periodically
Dependency pins	fastapi, starlette and prometheus-fastapi-instrumentator are not pinned to exact versions	Pin all versions, or use a lock file
CORS	The API allows all origins	Restrict to the real frontend origin
NAT gateway	A single NAT gateway is not highly available	One NAT gateway per Availability Zone
CI trigger	Documentation-only pushes do not start the pipeline (by design)	None needed
17. Cleanup

AWS bills by the hour, so tear everything down when you are finished. The order matters: the load balancer created by ingress-nginx must be gone before Terraform can delete the VPC.

bash
# 1. Stop ArgoCD managing the app, then remove the apps and the load balancer
kubectl delete -f argocd/application.yaml
helm uninstall stockpilot -n stockpilot            # skip if ArgoCD already removed it
helm uninstall ingress-nginx -n ingress-nginx
helm uninstall kube-prometheus-stack -n monitoring

# 2. Wait a few minutes until the load balancer disappears
#    (AWS Console -> EC2 -> Load Balancers)

# 3. Destroy the infrastructure
cd terraform
terraform destroy

Afterwards, open the AWS Console and confirm that the EKS cluster, NAT gateway, Elastic IPs and load balancers are really gone.