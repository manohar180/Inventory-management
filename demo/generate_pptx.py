"""
generate_pptx.py — StockPilot Capstone Presentation Generator
Run this script to create demo/presentation.pptx (10 slides).
Requires: pip install python-pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

# ── Colour Palette ──────────────────────────────────────────────────────────
NAVY    = RGBColor(0x0F, 0x17, 0x2A)   # Dark navy background
TEAL    = RGBColor(0x0D, 0xC5, 0xA5)   # StockPilot accent
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT   = RGBColor(0xE8, 0xF4, 0xF1)
GREY    = RGBColor(0xA0, 0xAE, 0xC0)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

BLANK = prs.slide_layouts[6]  # Completely blank layout

def bg(slide, color=NAVY):
    """Fill slide background with a solid colour."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_text(slide, text, left, top, width, height,
             size=24, bold=False, color=WHITE, align=PP_ALIGN.LEFT, italic=False):
    """Add a text box to a slide."""
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox

def accent_bar(slide, top=0.55):
    """Add a horizontal teal accent bar."""
    bar = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(0), Inches(top), SLIDE_W, Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()

def slide_number(slide, n):
    add_text(slide, f"{n} / 10", 12.2, 7.1, 1.0, 0.35, size=10, color=GREY, align=PP_ALIGN.RIGHT)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Title / Overview
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s, 0.45)

add_text(s, "StockPilot", 0.6, 1.0, 12, 1.2, size=60, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
add_text(s, "Cloud-Native Inventory Management Platform", 0.6, 2.2, 12, 0.7,
         size=26, bold=False, color=WHITE, align=PP_ALIGN.CENTER)
add_text(s,
    "DevOps Final Capstone  ·  FastAPI · React · PostgreSQL · Docker · GitHub Actions\n"
    "Terraform · AWS EKS · Helm · ArgoCD · Prometheus · Grafana",
    0.6, 3.1, 12, 1.1, size=16, color=GREY, align=PP_ALIGN.CENTER)
add_text(s, "github.com/manohar180/Inventory-management", 0.6, 6.5, 12, 0.5,
         size=14, color=TEAL, align=PP_ALIGN.CENTER, italic=True)
slide_number(s, 1)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — Tech Stack
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "Tech Stack", 0.5, 0.7, 12, 0.7, size=36, bold=True, color=TEAL)

cols = [
    ("Backend", "Python 3.12 · FastAPI · SQLAlchemy 2.x\nAlembic · psycopg v3 · Pydantic v2"),
    ("Frontend", "React 18 · Vite · Vanilla CSS\nResponsive dashboard · Glassmorphic UI"),
    ("Database", "PostgreSQL 16\nAlembic migrations\nPVC persistence"),
    ("CI/CD & Security", "GitHub Actions · Trivy (HIGH/CRIT gate)\nGHCR image registry · SHA tags"),
    ("Infrastructure", "Terraform · AWS VPC (2 AZ)\nAWS EKS 1.31 · 2× t3.medium\nNAT Gateway"),
    ("K8s & GitOps", "Helm 3 · ingress-nginx · HPA\nArgoCD automated sync\nServiceMonitor"),
]

for i, (title, body) in enumerate(cols):
    col = i % 3
    row = i // 3
    x = 0.5 + col * 4.25
    y = 1.8 + row * 2.4
    # card background
    card = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(3.9), Inches(2.1))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(0x1A, 0x25, 0x3D)
    card.line.color.rgb = TEAL
    add_text(s, title, x + 0.15, y + 0.1, 3.6, 0.45, size=15, bold=True, color=TEAL)
    add_text(s, body,  x + 0.15, y + 0.55, 3.6, 1.4,  size=12, color=WHITE)

slide_number(s, 2)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — Architecture
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "Architecture", 0.5, 0.7, 12, 0.7, size=36, bold=True, color=TEAL)

arch = """
Internet Users  →  AWS ALB  →  Nginx Ingress Controller
                                    │                  │
                               /api/*              /*  
                                    │                  │
                            FastAPI Backend     React Frontend
                          (2 replicas · HPA)  (2 replicas · Nginx)
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
              PostgreSQL                  Prometheus + Grafana
            (Deployment + PVC)          (kube-prometheus-stack)
                                               ↑
                                       ServiceMonitor scrapes /metrics
"""
add_text(s, arch.strip(), 0.5, 1.6, 12.3, 5.5, size=13, color=WHITE)
slide_number(s, 3)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — CI/CD Pipeline
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "CI/CD Pipeline", 0.5, 0.7, 12, 0.7, size=36, bold=True, color=TEAL)

steps = [
    ("1  Push to main", "Developer pushes code to GitHub main branch"),
    ("2  Test Job", "pytest (12+ tests) + npm run build\nBuild fails if any test fails"),
    ("3  Build & Scan", "docker build backend + frontend\nTrivy scans for HIGH/CRITICAL CVEs\nExit-code 1 if vulnerabilities found"),
    ("4  Publish to GHCR", "docker push with SHA tag (never 'latest')\nOnly after Trivy passes"),
    ("5  GitOps Bump", "Updates values-prod.yaml with new SHA\nCommits back [skip ci]"),
    ("6  ArgoCD Syncs", "Detects Git change → helm upgrade\nRolling deploy → zero downtime"),
]

for i, (title, body) in enumerate(steps):
    x = 0.4 + (i % 3) * 4.25
    y = 1.8 + (i // 3) * 2.5
    card = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(3.9), Inches(2.2))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(0x1A, 0x25, 0x3D)
    card.line.color.rgb = TEAL
    add_text(s, title, x+0.15, y+0.1,  3.6, 0.5,  size=14, bold=True, color=TEAL)
    add_text(s, body,  x+0.15, y+0.65, 3.6, 1.4,  size=12, color=WHITE)

slide_number(s, 4)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — Security (Trivy)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "DevSecOps — Trivy Security Scanning", 0.5, 0.7, 12, 0.7, size=32, bold=True, color=TEAL)

content = """What is Trivy?
  Trivy is an open-source vulnerability scanner by Aqua Security.
  It scans container images for OS packages and language-level CVEs.

How it is used in StockPilot CI/CD:
  • Both backend and frontend images are scanned on every push to main
  • Scan flags: --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
  • The pipeline FAILS if any unfixed HIGH or CRITICAL CVE is found
  • Images are only pushed to GHCR after a clean scan

CVEs encountered & resolved:
  • CVE-2025-62727  (starlette DoS via Range header)  → fixed in 0.49.1
  • CVE-2026-48818  (starlette SSRF via StaticFiles)  → fixed in 1.1.0
  • CVE-2026-54283  (starlette form() limits ignored) → fixed in 1.3.1

  Fix applied: requirements.txt pins starlette>=1.3.1 so all three are patched.
  FastAPI is unpinned to allow pip to resolve a compatible version.

Result: Pipeline runs cleanly. Both images pass the security gate.
"""
add_text(s, content.strip(), 0.5, 1.7, 12.3, 5.5, size=14, color=WHITE)
slide_number(s, 5)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — Terraform Infrastructure
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "Infrastructure — Terraform on AWS", 0.5, 0.7, 12, 0.7, size=32, bold=True, color=TEAL)

infra = [
    ("VPC",           "CIDR 10.30.0.0/16\n2 Public + 2 Private subnets\nSpanning ap-south-1a + ap-south-1b"),
    ("Networking",    "Internet Gateway (public ingress)\nSingle NAT Gateway (private egress)\nProper EKS subnet tags"),
    ("EKS Cluster",   "Kubernetes 1.31\nPublic API endpoint\nCreator admin permissions"),
    ("Node Group",    "2× t3.medium (2 vCPU / 4 GB)\nScales to 4 nodes\nAmazon Linux 2 AMI"),
    ("Add-ons",       "CoreDNS · kube-proxy\nvpc-cni · ebs-csi-driver\nAll managed by EKS"),
    ("Cost Warning",  "~$5–8 per day while running\nRun terraform destroy\nafter evaluation!"),
]

for i, (title, body) in enumerate(infra):
    x = 0.4 + (i % 3) * 4.25
    y = 1.8 + (i // 3) * 2.5
    card = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(3.9), Inches(2.2))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(0x1A, 0x25, 0x3D)
    card.line.color.rgb = TEAL
    add_text(s, title, x+0.15, y+0.1,  3.6, 0.5,  size=14, bold=True, color=TEAL)
    add_text(s, body,  x+0.15, y+0.65, 3.6, 1.4,  size=12, color=WHITE)

slide_number(s, 6)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — Kubernetes & Helm
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "Kubernetes & Helm", 0.5, 0.7, 12, 0.7, size=36, bold=True, color=TEAL)

k8s = """Helm Chart: helm/stockpilot/
  ├── Backend Deployment   2 replicas · /health liveness · /ready readiness · non-root (uid 10001)
  ├── Frontend Deployment  2 replicas · Nginx 8080 · non-root (uid 101)
  ├── PostgreSQL           Deployment + PVC (5Gi) + Kubernetes Secret for credentials
  ├── ClusterIP Services   backend:8000  frontend:8080  postgres:5432
  ├── Ingress              /api → backend  /  → frontend  (ingressClassName: nginx)
  ├── HPA                  CPU-based · min 2 · max 6 replicas (backend only)
  └── ServiceMonitor       Prometheus scrapes /metrics every 15s

Deployment command:
  kubectl apply -f k8s/namespace.yaml
  helm upgrade --install stockpilot helm/stockpilot \\
    --namespace stockpilot --values helm/stockpilot/values-prod.yaml

Verify:
  kubectl get pods -n stockpilot     → All Running
  kubectl get hpa  -n stockpilot     → TARGETS showing CPU %
  kubectl get ingress -n stockpilot  → ADDRESS assigned
"""
add_text(s, k8s.strip(), 0.5, 1.7, 12.3, 5.6, size=13, color=WHITE)
slide_number(s, 7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — ArgoCD / GitOps
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "GitOps with ArgoCD", 0.5, 0.7, 12, 0.7, size=36, bold=True, color=TEAL)

gitops = """GitOps Principle:  Git is the single source of truth.
               No manual kubectl apply in production — ever.

Flow:
  1. Developer pushes code → GitHub main branch
  2. GitHub Actions CI/CD:  test → scan → build → push SHA-tagged image to GHCR
  3. CI/CD commits new SHA into helm/stockpilot/values-prod.yaml  [skip ci]
  4. ArgoCD polls Git every ~3 minutes, detects the values-prod.yaml change
  5. ArgoCD runs: helm upgrade stockpilot helm/stockpilot --values values-prod.yaml
  6. Kubernetes performs a rolling update (zero downtime)
  7. ArgoCD reports: Synced / Healthy

ArgoCD Application settings (argocd/application.yaml):
  • automated.prune: true      → removes resources deleted from Git
  • automated.selfHeal: true   → reverts manual kubectl changes
  • CreateNamespace: true      → creates stockpilot ns automatically
  • targetRevision: main       → always tracks the main branch
"""
add_text(s, gitops.strip(), 0.5, 1.7, 12.3, 5.6, size=13, color=WHITE)
slide_number(s, 8)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — Observability
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "Observability — Prometheus & Grafana", 0.5, 0.7, 12, 0.7, size=30, bold=True, color=TEAL)

obs = [
    ("Metrics Endpoint",  "/metrics\nPrometheus-format output\nScraped every 15s via ServiceMonitor"),
    ("Custom Metrics",    "stockpilot_stock_movements_total\n  {type='IN'|'OUT'}  Counter\n\nstockpilot_low_stock_products\n  Gauge — reorder alerts"),
    ("Grafana Dashboard", "6 panels:\n• Request Rate (req/s)\n• p95 Latency (ms)\n• 5xx Error Rate %\n• Requests by Endpoint\n• Stock Movements IN/OUT\n• Low-Stock Products"),
    ("kube-prometheus-\nstack", "Installed via Helm\nPrometheus Operator\nAlertmanager · node-exporter\nkube-state-metrics"),
    ("Load Test",         "scripts/load-test.sh\nCurl-only, no extra tools\nSeeds products → hits all endpoints\nTriggers HPA scaling"),
    ("HPA Scaling",       "metrics-server provides CPU data\nHPA scales backend pods\n2 → up to 6 replicas\nunder sustained load"),
]

for i, (title, body) in enumerate(obs):
    x = 0.4 + (i % 3) * 4.25
    y = 1.8 + (i // 3) * 2.5
    card = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(3.9), Inches(2.2))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(0x1A, 0x25, 0x3D)
    card.line.color.rgb = TEAL
    add_text(s, title, x+0.15, y+0.1,  3.6, 0.5,  size=13, bold=True, color=TEAL)
    add_text(s, body,  x+0.15, y+0.65, 3.6, 1.4,  size=11, color=WHITE)

slide_number(s, 9)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — Key Learnings
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s)
accent_bar(s)

add_text(s, "Key Learnings", 0.5, 0.7, 12, 0.7, size=36, bold=True, color=TEAL)

learnings = [
    "GitOps eliminates deployment drift — ArgoCD ensures what's in Git always matches the cluster",
    "Security as a gate, not an afterthought — Trivy CVE scanning blocked real vulnerabilities (starlette)",
    "IaC prevents environment inconsistency — Terraform reproduced the exact same VPC + EKS every time",
    "Helm values files are the GitOps control plane — one SHA update triggers the full delivery chain",
    "Observability is only useful if metrics are custom and meaningful — stockpilot_low_stock_products gives real business insight",
    "Non-root containers are the first line of Kubernetes security — enforced at both Dockerfile and securityContext levels",
    "Testing in isolation is essential — SQLite dependency override let CI run 12 tests without a real database",
]

for i, text in enumerate(learnings):
    add_text(s, f"▸  {text}", 0.7, 1.8 + i * 0.77, 11.9, 0.7, size=14, color=WHITE)

slide_number(s, 10)

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs("demo", exist_ok=True)
out = "demo/presentation.pptx"
prs.save(out)
print(f"DONE  Saved: {out}  ({os.path.getsize(out) // 1024} KB)")
print("   Open in PowerPoint or LibreOffice Impress.")
