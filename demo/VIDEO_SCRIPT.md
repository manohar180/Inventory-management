# demo/VIDEO_SCRIPT.md — StockPilot Capstone Presentation Video Script

> **Total target duration: 8–12 minutes**
> Record in one continuous take if possible. Use OBS, Loom, or any screen recorder.
> Upload the MP4 to `demo/` in the GitHub repo (or as a GitHub Release if >100 MB).

---

## Required Video Order (from GRADING.md)

1. PPT slides walkthrough
2. Codebase overview
3. CI/CD pipeline — trigger a push and show Actions run
4. Terraform — plan output + AWS Console (VPC + EKS)
5. ArgoCD — synced application + GitOps flow
6. Kubernetes — kubectl pods / services / ingress
7. Prometheus — Targets page showing app UP
8. Grafana — live dashboard panel with data

---

## Timed Script

### [0:00–1:30] — Slide Walkthrough (PPT)

> Open `demo/presentation.pptx` in full screen.

- **Slide 1**: "Hi, I'm presenting StockPilot — a cloud-native inventory management system built as my DevOps final capstone."
- **Slide 2**: "The tech stack is FastAPI on the backend, React + Vite on the frontend, PostgreSQL for storage, and a full DevSecOps pipeline."
- **Slide 3**: "The architecture has an AWS ALB → Nginx Ingress, routing `/api` to the FastAPI backend and `/` to the React frontend. Both run as 2 replicas with HPA."
- **Slide 4**: "The CI/CD pipeline has 3 jobs: test, build+scan, and GitOps bump. Trivy blocks any HIGH or CRITICAL CVE from reaching production."
- **Slide 5**: "Trivy found three real starlette CVEs in our image. I fixed all three by pinning `starlette>=1.3.1` in requirements.txt."
- **Slides 6–9**: Brief walk (30 seconds each) covering Terraform, Kubernetes/Helm, ArgoCD, and Observability.
- **Slide 10**: "The key learning is that GitOps, security scanning, and IaC together create a system where every change is auditable, reproducible, and safe."

---

### [1:30–2:30] — Codebase Overview

> Switch to VS Code / file explorer.

- Show folder structure: `backend/`, `frontend/`, `terraform/`, `helm/stockpilot/`, `k8s/`, `monitoring/`, `argocd/`
- Open `backend/app/main.py` — point to the endpoints, custom Prometheus metrics
- Open `backend/app/models.py` — show `products` and `stock_movements` tables
- Open `frontend/src/App.jsx` — show the dashboard components
- Open `.github/workflows/ci-cd.yml` — show the 3 jobs at a glance

---

### [2:30–4:00] — CI/CD Pipeline

> Open GitHub repository in browser → Actions tab.

- "Watch me trigger the pipeline by making a small change."
- Make a trivial commit (e.g., update a comment) and push to main
- Switch to the GitHub Actions tab and click the running workflow
- Walk through the 3 jobs live:
  - **test**: pytest runs and passes
  - **build-scan-publish**: Trivy scan runs — show the output, confirm no HIGH/CRITICAL
  - **gitops-bump**: show the commit updating `values-prod.yaml`
- "The pipeline took ~X minutes and all jobs are green."
- Show the GHCR packages page with SHA-tagged images

---

### [4:00–5:30] — Terraform (AWS Infrastructure)

> Switch to terminal + AWS Console.

```bash
cd terraform
terraform plan   # Show the output
```

- "This plan would create the VPC, 4 subnets, 1 NAT gateway, and the EKS cluster."
- Switch to AWS Console:
  - VPC → show `stockpilot-vpc` with subnets in 2 AZs
  - EKS → show `stockpilot-eks` cluster, node group with 2 nodes
- "I ran `terraform apply` earlier. After the demo I'll run `terraform destroy` to avoid charges."

---

### [5:30–6:30] — ArgoCD

> Switch to ArgoCD UI (https://localhost:8080 via port-forward).

```bash
kubectl port-forward svc/argocd-server 8080:443 -n argocd
```

- Log in as admin, show the `stockpilot` Application tile
- Click it — show: **Synced / Healthy** status
- Click the app tree — show pods, services, ingress all green
- "ArgoCD detected the values-prod.yaml change from our CI/CD commit and auto-deployed the new image — that's GitOps."

---

### [6:30–7:30] — Kubernetes Verification

> Switch to terminal.

```bash
kubectl get pods    -n stockpilot    # All Running
kubectl get svc     -n stockpilot    # Services with ClusterIP
kubectl get ingress -n stockpilot    # ADDRESS populated
kubectl get hpa     -n stockpilot    # TARGETS: 5%/60%  REPLICAS: 2
helm list           -n stockpilot    # stockpilot chart, DEPLOYED
```

- "Two backend replicas, two frontend replicas, HPA ready to scale to 6."

---

### [7:30–8:30] — Prometheus & Grafana

> Switch to Prometheus UI (http://localhost:9090 via port-forward).

```bash
kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring
```

- Navigate to Status → Targets
- "Here you can see the StockPilot backend ServiceMonitor is UP and being scraped every 15 seconds."
- Query: `stockpilot_low_stock_products` — show the gauge value

> Switch to Grafana (http://localhost:3000).

```bash
kubectl port-forward svc/kube-prometheus-stack-grafana 3000:3000 -n monitoring
```

- Open the **StockPilot — Inventory Observability** dashboard
- Show panels with live data (run load-test.sh in background first):
  - Request rate rising
  - p95 latency
  - Stock movements IN/OUT (custom metric)
  - Low-stock products counter
- "These last two panels use custom metrics I defined in the FastAPI backend — not just the default instrumentator metrics."

---

### [8:30–end] — Wrap Up

- "That completes the StockPilot DevOps capstone walkthrough."
- "We covered: full-stack app, 12+ tests, Trivy security gate, GHCR images, Terraform EKS, Helm chart with HPA and Ingress, ArgoCD GitOps, and Prometheus/Grafana observability."
- Show `demo/SCREENSHOTS_CHECKLIST.md` briefly as evidence all items are captured.
- "Thank you."

---

## Tips for Recording

- Use 1920×1080 resolution
- Close notifications (Do Not Disturb mode)
- Have all terminals and browser tabs open BEFORE recording
- Run `load-test.sh` 5 minutes before recording Grafana so panels are populated
- Save as MP4 (H.264)
- If file > 100 MB: upload to GitHub Releases, link in README
