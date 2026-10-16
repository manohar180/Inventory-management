# demo/SCREENSHOTS_CHECKLIST.md — Every Screenshot the Rubric Requires


## M1 — Application 

- [x] **App running in browser** — `http://localhost:3000` showing the StockPilot dashboard with KPI cards and product table

  - ![App Dashboard](screenshots/app-dashboard.png)

- [ ] **Add/Edit product modal** — open the modal and show a product being created
  - ![Add/Edit product modal](screenshots/app-modal.png)

- [ ] **Stock IN/OUT** — show a stock movement being added
  - ![Stock IN/OUT](screenshots/app-stock-movement.png)

- [ ] **Low-stock badge visible** — filter on `?low_stock=true`, show the badge
  - ![Low-stock badge visible](screenshots/app-low-stock.png)

- [ ] **FastAPI Swagger docs** — `http://localhost:8000/docs` showing all endpoints
  - ![FastAPI Swagger docs](screenshots/api-swagger.png)

---

## M2 — Version Control / Git

- [ ] **GitHub repository page** — show public repo with all files committed
  - ![GitHub repository page](screenshots/github-repo.png)

- [ ] **Commit history** — at least one commit per step
  - ![Commit history](screenshots/github-commits.png)

- [ ] **`.gitignore` working** — confirm no `.env`, `*.tfstate`, `node_modules` in repo
  - Verify by checking the repo file tree in GitHub browser

---

## M3 — Docker

- [ ] **docker compose up** — terminal showing all 3 services started
  - Command: `docker compose up --build`
  - ![docker compose up](screenshots/docker-compose-up.png)

- [ ] **Multi-stage frontend Dockerfile** — open `frontend/Dockerfile` in editor to show build stages
  - ![Multi-stage frontend Dockerfile](screenshots/dockerfile-frontend.png)

---

## M4 — CI/CD Pipeline

- [ ] **GitHub Actions green run** — all 3 jobs (test, build-scan-publish, gitops-bump) green
  - URL: `https://github.com/manohar180/Inventory-management/actions`
  - ![GitHub Actions green run](screenshots/ci-all-green.png)

- [ ] **Test job detail** — show pytest output inside the Actions log
  - ![Test job detail](screenshots/ci-test-job.png)

- [ ] **Trivy scan output** — show the scan running inside the build job, "No vulnerabilities found"
  - ![Trivy scan output](screenshots/ci-trivy-scan.png)

- [ ] **gitops-bump commit** — show the auto-commit that updated `values-prod.yaml` with `[skip ci]`
  - ![gitops-bump commit](screenshots/ci-gitops-commit.png)

---

## M5 — Container Registry

- [ ] **GHCR packages page** — `https://github.com/manohar180?tab=packages` showing both images
  - ![GHCR packages page](screenshots/packages.png)

---

## M6 — Terraform / IaC

- [ ] **`terraform plan` output** — full plan output in terminal (all resources to be created)
  - Command: `cd terraform && terraform plan`
  - ![terraform plan output](screenshots/terraform-plan.png)

- [ ] **`terraform apply` success** — final "Apply complete! Resources: X added"
  - ![terraform apply success](screenshots/terraform-apply-complete.png)

- [ ] **AWS Console — EKS cluster** — `stockpilot-eks` → Overview tab (Active status)
  - ![AWS Console EKS cluster](screenshots/aws-eks-cluster.png)

- [ ] **AWS Console — EKS Node Group** — show `stockpilot_nodes` with 2 nodes Running
  - ![AWS Console EKS Node Group](screenshots/aws-eks-nodes.png)


- [ ] **`terraform destroy` complete** — "Destroy complete! Resources: X destroyed"
  - ![terraform destroy complete](screenshots/terraform-destroy.png)

---

## M8 — Kubernetes + Helm (15 pts)

- [ ] **`kubectl get pods -n stockpilot`** — all pods Running (backend×2, frontend×2, postgres×1)
  - ![kubectl get pods](screenshots/kubectl-pods.png)

- [ ] **`kubectl get svc -n stockpilot`** — services listed with ClusterIP
  - ![kubectl get svc](screenshots/kubectl-services.png)

- [ ] **`kubectl get ingress -n stockpilot`** — Ingress with ADDRESS populated
  - ![kubectl get ingress](screenshots/kubectl-ingress.png)

- [ ] **`kubectl get hpa -n stockpilot`** — HPA showing TARGETS and MINPODS/MAXPODS
  - ![kubectl get hpa](screenshots/kubectl-hpa.png)

- [ ] **`helm list -n stockpilot`** — chart showing STATUS=deployed
  - ![helm list](screenshots/helm-list.png)

- [ ] **`helm lint` passing** — no chart failures
  - Command: `helm lint helm/stockpilot`
  - ![helm lint](screenshots/helm-lint.png)

---

## M9 — Observability (15 pts)

- [ ] **Prometheus Targets page** — `http://localhost:9090/targets` showing stockpilot backend **UP**
  - ![Prometheus Targets UP](screenshots/prometheus-targets-up.png)

- [ ] **Custom metric in Prometheus** — query `stockpilot_low_stock_products` showing a value
  - ![Custom metric in Prometheus](screenshots/prometheus-custom-metric.png)

- [ ] **Grafana dashboard imported** — `StockPilot — Inventory Observability` dashboard open
  - ![Grafana dashboard imported](screenshots/grafana-dashboard.png)

- [ ] **Grafana with live data** — at least 2 panels showing non-zero data (run load-test.sh first)
  - ![Grafana live panels](screenshots/grafana-live-panels.png)

- [ ] **HPA scaling event** — `kubectl describe hpa -n stockpilot` showing a ScalingActive event
  - ![HPA scaling event](screenshots/hpa-scaling-event.png)

---

## M10 — Documentation & Video (15 pts)

- [ ] **README.md complete** — open in GitHub and show architecture diagram + all sections
  - ![README on GitHub](screenshots/readme-github.png)

- [ ] **`demo/presentation.pptx`** — open slide deck, show at least slide 1 and 2
  - ![PPTX slides](screenshots/pptx-slides.png)

- [ ] **ArgoCD synced** — ArgoCD UI showing `stockpilot` Application as **Synced / Healthy**
  - ![ArgoCD synced](screenshots/argocd-synced.png)

- [ ] **ArgoCD app tree** — show the resource tree (deployments, services, ingress all green)
  - ![ArgoCD app tree](screenshots/argocd-tree.png)

---

