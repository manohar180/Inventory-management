# demo/SCREENSHOTS_CHECKLIST.md — Every Screenshot the Rubric Requires

Use this checklist before submission. Save all screenshots in `demo/screenshots/`.
Add them to the README.md screenshots table once captured.

---

## M1 — Application (10 pts)

- [ ] **App running in browser** — `http://localhost:3000` showing the StockPilot dashboard with KPI cards and product table
  - File: `demo/screenshots/app-dashboard.png`

- [ ] **Add/Edit product modal** — open the modal and show a product being created
  - File: `demo/screenshots/app-modal.png`

- [ ] **Stock IN/OUT** — show a stock movement being added
  - File: `demo/screenshots/app-stock-movement.png`

- [ ] **Low-stock badge visible** — filter on `?low_stock=true`, show the badge
  - File: `demo/screenshots/app-low-stock.png`

- [ ] **FastAPI Swagger docs** — `http://localhost:8000/docs` showing all endpoints
  - File: `demo/screenshots/api-swagger.png`

---

## M2 — Version Control / Git (5 pts)

- [ ] **GitHub repository page** — show public repo with all files committed
  - File: `demo/screenshots/github-repo.png`

- [ ] **Commit history** — at least one commit per step
  - File: `demo/screenshots/github-commits.png`

- [ ] **`.gitignore` working** — confirm no `.env`, `*.tfstate`, `node_modules` in repo
  - Verify by checking the repo file tree in GitHub browser

---

## M3 — Testing (10 pts)

- [ ] **pytest passing** — terminal showing `12 passed` (or more) in green
  - Command: `cd backend && pytest -v`
  - File: `demo/screenshots/pytest-pass.png`

- [ ] **Test output detail** — show individual test names scrolled through
  - File: `demo/screenshots/pytest-detail.png`

---

## M4 — Docker (10 pts)

- [ ] **docker compose up** — terminal showing all 3 services started
  - Command: `docker compose up --build`
  - File: `demo/screenshots/docker-compose-up.png`

- [ ] **Docker Desktop or `docker ps`** — 3 containers running
  - File: `demo/screenshots/docker-containers.png`

- [ ] **Multi-stage frontend Dockerfile** — open `frontend/Dockerfile` in editor to show build stages
  - File: `demo/screenshots/dockerfile-frontend.png`

---

## M5 — CI/CD Pipeline (15 pts)

- [ ] **GitHub Actions green run** — all 3 jobs (test, build-scan-publish, gitops-bump) green
  - URL: `https://github.com/manohar180/Inventory-management/actions`
  - File: `demo/screenshots/ci-all-green.png`

- [ ] **Test job detail** — show pytest output inside the Actions log
  - File: `demo/screenshots/ci-test-job.png`

- [ ] **Trivy scan output** — show the scan running inside the build job, "No vulnerabilities found"
  - File: `demo/screenshots/ci-trivy-scan.png`

- [ ] **gitops-bump commit** — show the auto-commit that updated `values-prod.yaml` with `[skip ci]`
  - File: `demo/screenshots/ci-gitops-commit.png`

---

## M6 — Container Registry (5 pts)

- [ ] **GHCR packages page** — `https://github.com/manohar180?tab=packages` showing both images
  - File: `demo/screenshots/ghcr-packages.png`

- [ ] **SHA tag** — click one image, show the SHA tag (not `latest`)
  - File: `demo/screenshots/ghcr-sha-tag.png`

---

## M7 — Terraform / IaC (15 pts)

- [ ] **`terraform plan` output** — full plan output in terminal (all resources to be created)
  - Command: `cd terraform && terraform plan`
  - File: `demo/screenshots/terraform-plan.png`

- [ ] **`terraform apply` success** — final "Apply complete! Resources: X added"
  - File: `demo/screenshots/terraform-apply-complete.png`

- [ ] **AWS Console — VPC** — `ap-south-1` → VPC → `stockpilot-vpc` with subnets visible
  - File: `demo/screenshots/aws-vpc.png`

- [ ] **AWS Console — EKS cluster** — `stockpilot-eks` → Overview tab (Active status)
  - File: `demo/screenshots/aws-eks-cluster.png`

- [ ] **AWS Console — EKS Node Group** — show `stockpilot_nodes` with 2 nodes Running
  - File: `demo/screenshots/aws-eks-nodes.png`

- [ ] **`kubectl get nodes`** — 2 nodes in Ready status
  - Command: `kubectl get nodes`
  - File: `demo/screenshots/kubectl-nodes.png`

- [ ] **`terraform destroy` complete** — "Destroy complete! Resources: X destroyed"
  - File: `demo/screenshots/terraform-destroy.png`

---

## M8 — Kubernetes + Helm (15 pts)

- [ ] **`kubectl get pods -n stockpilot`** — all pods Running (backend×2, frontend×2, postgres×1)
  - File: `demo/screenshots/kubectl-pods.png`

- [ ] **`kubectl get svc -n stockpilot`** — services listed with ClusterIP
  - File: `demo/screenshots/kubectl-services.png`

- [ ] **`kubectl get ingress -n stockpilot`** — Ingress with ADDRESS populated
  - File: `demo/screenshots/kubectl-ingress.png`

- [ ] **`kubectl get hpa -n stockpilot`** — HPA showing TARGETS and MINPODS/MAXPODS
  - File: `demo/screenshots/kubectl-hpa.png`

- [ ] **`helm list -n stockpilot`** — chart showing STATUS=deployed
  - File: `demo/screenshots/helm-list.png`

- [ ] **`helm lint` passing** — no chart failures
  - Command: `helm lint helm/stockpilot`
  - File: `demo/screenshots/helm-lint.png`

---

## M9 — Observability (15 pts)

- [ ] **Prometheus Targets page** — `http://localhost:9090/targets` showing stockpilot backend **UP**
  - File: `demo/screenshots/prometheus-targets-up.png`

- [ ] **Custom metric in Prometheus** — query `stockpilot_low_stock_products` showing a value
  - File: `demo/screenshots/prometheus-custom-metric.png`

- [ ] **Grafana dashboard imported** — `StockPilot — Inventory Observability` dashboard open
  - File: `demo/screenshots/grafana-dashboard.png`

- [ ] **Grafana with live data** — at least 2 panels showing non-zero data (run load-test.sh first)
  - File: `demo/screenshots/grafana-live-panels.png`

- [ ] **HPA scaling event** — `kubectl describe hpa -n stockpilot` showing a ScalingActive event
  - File: `demo/screenshots/hpa-scaling-event.png`

---

## M10 — Documentation & Video (15 pts)

- [ ] **README.md complete** — open in GitHub and show architecture diagram + all sections
  - File: `demo/screenshots/readme-github.png`

- [ ] **`demo/presentation.pptx`** — open slide deck, show at least slide 1 and 2
  - File: `demo/screenshots/pptx-slides.png`

- [ ] **ArgoCD synced** — ArgoCD UI showing `stockpilot` Application as **Synced / Healthy**
  - File: `demo/screenshots/argocd-synced.png`

- [ ] **ArgoCD app tree** — show the resource tree (deployments, services, ingress all green)
  - File: `demo/screenshots/argocd-tree.png`

- [ ] **Presentation video uploaded** — `demo/` folder in GitHub shows the MP4 file
  - OR a GitHub Release link in the README
  - File: N/A (the video IS the evidence)

---

## Quick Summary: Total Screenshots Needed

| Module | Required Screenshots |
|--------|---------------------|
| M1 App | 5 |
| M2 Git | 2 |
| M3 Tests | 2 |
| M4 Docker | 3 |
| M5 CI/CD | 4 |
| M6 Registry | 2 |
| M7 Terraform | 7 |
| M8 Kubernetes | 6 |
| M9 Observability | 5 |
| M10 Documentation | 5 |
| **TOTAL** | **41** |

> Store all screenshots in `demo/screenshots/` and reference them in README.md.
