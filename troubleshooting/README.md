# StockPilot — Kubernetes Troubleshooting Lab

This directory contains intentionally broken manifests and a step-by-step diagnosis guide.
Apply each scenario, diagnose the problem using only `kubectl`, then fix it.

---

## Scenario 1 — ImagePullBackOff (`broken-image.yaml`)

### What is broken
The backend deployment references an image tag that does not exist in GHCR:
`ghcr.io/manohar180/stockpilot-backend:v9.9.9-does-not-exist`

### Apply the broken manifest
```bash
kubectl apply -f troubleshooting/broken-image.yaml -n stockpilot
```

### Symptoms
```bash
kubectl get pods -n stockpilot
# NAME                                   READY   STATUS             RESTARTS
# stockpilot-backend-broken-xxxx         0/1     ImagePullBackOff   0
```

### Diagnose
```bash
# 1. See the pull error message
kubectl describe pod -l app=stockpilot-backend-broken -n stockpilot
# Look for Events section:
#   Warning  Failed  ... Failed to pull image ... tag does not exist

# 2. Confirm the image tag being used
kubectl get deployment stockpilot-backend-broken -n stockpilot \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

### Fix
```bash
# Option A — Update to a valid tag (replace <VALID_SHA> with a real commit SHA)
kubectl set image deployment/stockpilot-backend-broken \
  backend=ghcr.io/manohar180/stockpilot-backend:<VALID_SHA> \
  -n stockpilot

# Option B — Delete the broken deployment entirely
kubectl delete -f troubleshooting/broken-image.yaml -n stockpilot
```

### Verify fix
```bash
kubectl get pods -n stockpilot
# STATUS should change: ImagePullBackOff → ContainerCreating → Running
```

---

## Scenario 2 — Service Selector Mismatch → 503 Errors (`broken-service.yaml`)

### What is broken
A Service uses the selector `component: api` but the backend pods have the label
`app.kubernetes.io/component: backend`. No pods match → Endpoints list is empty
→ every request to the service returns 503 or connection refused.

### Apply the broken manifest
```bash
kubectl apply -f troubleshooting/broken-service.yaml -n stockpilot
```

### Symptoms
```bash
# Test the broken service (via port-forward)
kubectl port-forward svc/stockpilot-backend-broken-svc 9999:8000 -n stockpilot &
curl http://localhost:9999/health
# curl: (7) Failed to connect to localhost port 9999

# OR: check endpoints directly — they will be empty
kubectl get endpoints stockpilot-backend-broken-svc -n stockpilot
# NAME                            ENDPOINTS   AGE
# stockpilot-backend-broken-svc  <none>      10s   ← PROBLEM: no endpoints
```

### Diagnose
```bash
# 1. Confirm endpoints are empty
kubectl get endpoints -n stockpilot

# 2. See what selector the broken service is using
kubectl describe svc stockpilot-backend-broken-svc -n stockpilot
# Selector: component=api   ← WRONG

# 3. See what labels the actual backend pods have
kubectl get pods -n stockpilot --show-labels
# Labels: app.kubernetes.io/component=backend   ← CORRECT label

# 4. Root cause: Service selector ≠ Pod labels → no endpoints
```

### Fix
```bash
# Option A — Patch the service selector to match the real pod labels
kubectl patch svc stockpilot-backend-broken-svc -n stockpilot \
  --type='json' \
  -p='[{"op":"replace","path":"/spec/selector","value":{"app.kubernetes.io/component":"backend","app.kubernetes.io/instance":"stockpilot"}}]'

# Option B — Delete the broken service
kubectl delete -f troubleshooting/broken-service.yaml -n stockpilot
```

### Verify fix
```bash
kubectl get endpoints stockpilot-backend-broken-svc -n stockpilot
# NAME                            ENDPOINTS             AGE
# stockpilot-backend-broken-svc  10.0.x.x:8000, ...    15s   ← endpoints populated

kubectl port-forward svc/stockpilot-backend-broken-svc 9999:8000 -n stockpilot &
curl http://localhost:9999/health
# {"status":"healthy"}   ← working
```

---

## Quick Reference: Common kubectl Troubleshooting Commands

```bash
# ── Pod Issues ────────────────────────────────────────────────────────────────
kubectl get pods -n stockpilot                          # List all pods + status
kubectl describe pod <pod-name> -n stockpilot           # Detailed events + config
kubectl logs <pod-name> -n stockpilot                   # Container stdout logs
kubectl logs <pod-name> -n stockpilot --previous        # Logs from crashed container

# ── Service & Networking ──────────────────────────────────────────────────────
kubectl get svc -n stockpilot                           # List services + ports
kubectl get endpoints -n stockpilot                     # Check endpoint IPs (empty = selector mismatch)
kubectl describe ingress -n stockpilot                  # Ingress rules + backend

# ── Deployment Issues ─────────────────────────────────────────────────────────
kubectl rollout status deployment/<name> -n stockpilot  # Check rollout progress
kubectl rollout history deployment/<name> -n stockpilot # See revision history
kubectl rollout undo deployment/<name> -n stockpilot    # Roll back one version

# ── Resource Usage ────────────────────────────────────────────────────────────
kubectl top pods -n stockpilot                          # CPU/memory per pod
kubectl top nodes                                       # CPU/memory per node
kubectl get hpa -n stockpilot                           # HPA status + current replicas

# ── Events (great for diagnosing failures) ────────────────────────────────────
kubectl get events -n stockpilot --sort-by='.lastTimestamp'
```
