# StockPilot — Submission Evidence & Screenshots Checklist

> Cross-referenced against `README.md` evidence table and capstone rubric (M1–M10).
> Status is checked `[x]` only when the file is confirmed present in `demo/screenshots/`.

---

## M1 — Application

- [x] **app-dashboard.png** — StockPilot React dashboard running with KPI cards and product catalogue
  - ![App Dashboard](screenshots/app-dashboard.png)

- [x] **app-modal.png** — Add/Edit product modal showing creation form
  - ![Add/Edit Product Modal](screenshots/app-modal.png)

- [x] **app-stock-movement.png** — Stock movement ledger showing IN/OUT adjustments
  - ![Stock IN/OUT](screenshots/app-stock-movement.png)

- [x] **app-low-stock.png** — Low stock badge filter (`?low_stock=true`) showing filtered catalogue
  - ![Low Stock Filter](screenshots/app-low-stock.png)

- [x] **api-swagger.png** — FastAPI interactive Swagger documentation (`/docs`) showing all endpoints
  - ![Swagger UI](screenshots/api-swagger.png)

---

## M2 — Testing & Version Control

- [x] **github-repo.png** — GitHub repository home page showing public repo and committed structure
  - ![GitHub Repo](screenshots/github-repo.png)

- [x] **github-commits.png** — Git commit history showing meaningful commits across development stages
  - ![GitHub Commits](screenshots/github-commits.png)

---

## M3 — Containerisation

- [x] **docker-compose-up.png** — Terminal showing `docker compose up --build` with all 3 services healthy
  - ![Docker Compose](screenshots/docker-compose-up.png)

- [x] **dockerfile-frontend.png** — Multi-stage frontend `Dockerfile` open in editor showing build & runtime stages
  - ![Frontend Dockerfile](screenshots/dockerfile-frontend.png)

---

## M4 — CI/CD Pipeline & DevSecOps

- [x] **ci-all-green.png** — GitHub Actions workflow run with all 3 jobs green (test, build-scan-publish, gitops-bump)
  - ![CI/CD All Green](screenshots/ci-all-green.png)

- [x] **ci-test-job.png** — Actions test job detail log showing automated tests passing
  - ![CI Test Job](screenshots/ci-test-job.png)

- [x] **ci-trivy-scan.png** — Trivy container vulnerability scan log showing 0 HIGH/CRITICAL vulnerabilities
  - ![Trivy Scan](screenshots/ci-trivy-scan.png)

- [x] **ci-gitops-commit.png** — Automated GitOps commit by GitHub Actions updating `values-prod.yaml`
  - ![GitOps Bump Commit](screenshots/ci-gitops-commit.png)

---

## M5 — Container Registry

- [x] **packages.png** — GitHub Packages (GHCR) page showing SHA-tagged backend and frontend images
  - ![GHCR Packages](screenshots/packages.png)

---

## M6 — Infrastructure as Code (Terraform)

- [x] **terraform-plan.png** — Terminal showing `terraform plan` execution for VPC and EKS cluster
  - ![Terraform Plan](screenshots/terraform-plan.png)

- [x] **terraform-apply-complete.png** — Terminal showing `terraform apply` completed successfully
  - ![Terraform Apply](screenshots/terraform-apply-complete.png)


- [x] **aws-eks-cluster.png** — AWS Management Console showing `stockpilot-eks` cluster in Active state
  - ![AWS EKS Cluster](screenshots/aws-eks-cluster.png)

- [x] **aws-eks-nodes.png** — AWS Management Console showing EKS Managed Node Group with active worker nodes
  - ![AWS EKS Nodes](screenshots/aws-eks-nodes.png)

- [x] **terraform-destroy.png** — Terminal showing `terraform destroy` completion
  - ![Terraform Destroy](screenshots/terraform-destroy.png)

---

## M7 — Kubernetes & Helm Deployment

- [x] **kubectl-pods.png** — Terminal showing `kubectl get pods -n stockpilot` with all pods in Running state
  - ![Kubectl Pods](screenshots/kubectl-pods.png)

- [x] **kubectl-services.png** — Terminal showing `kubectl get svc -n stockpilot` with ClusterIP services
  - ![Kubectl Services](screenshots/kubectl-services.png)

- [x] **kubectl-ingress.png** — Terminal showing `kubectl get ingress -n stockpilot`
  - ![Kubectl Ingress](screenshots/kubectl-ingress.png)

- [x] **kubectl-hpa.png** — Terminal showing `kubectl get hpa -n stockpilot` with CPU target and replica limits
  - ![Kubectl HPA](screenshots/kubectl-hpa.png)

- [x] **helm-list.png** — Terminal showing `helm list -n stockpilot` with deployed release
  - ![Helm List](screenshots/helm-list.png)

- [x] **helm-lint.png** — Terminal showing `helm lint helm/stockpilot` with 0 failures
  - ![Helm Lint](screenshots/helm-lint.png)

---

## M8 — Observability (Prometheus & Grafana)

- [x] **prometheus-targets-up.png** — Prometheus Targets page (`/targets`) showing backend ServiceMonitor as UP
  - ![Prometheus Targets UP](screenshots/prometheus-targets-up.png)

- [x] **grafana-dashboard.png** — Grafana dashboard (`StockPilot — Inventory Observability`) imported and active
  - ![Grafana Dashboard](screenshots/grafana-dashboard.png)

---

## M9 — GitOps (ArgoCD)

- [x] **argocd-synced.png** — ArgoCD web UI showing `stockpilot` application in **Synced** & **Healthy** state
  - ![ArgoCD Synced](screenshots/argocd-synced.png)

---

## M10 — Documentation & Video Deliverables

- [x] **README.md** — Complete documentation with architecture, setup, testing, and evidence table
- [x] **demo/presentation.pptx** — 10-slide capstone slide deck
- [x] **demo/VIDEO_SCRIPT.md** — Timed presentation walkthrough script
