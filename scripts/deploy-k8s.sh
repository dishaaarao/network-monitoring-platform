#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if ! kubectl cluster-info >/dev/null 2>&1; then
  echo "ERROR: Kubernetes cluster not reachable. Enable Kubernetes in Docker Desktop or start minikube."
  exit 1
fi

echo "==> Building Docker image"
docker build -t network-monitoring-app:latest .

echo "==> Installing metrics-server (for HPA)"
"$ROOT_DIR/scripts/install-metrics-server.sh" || echo "metrics-server install skipped or failed"

echo "==> Applying Kubernetes manifests"
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/monitoring/prometheus-deployment.yaml
kubectl apply -f k8s/monitoring/grafana.yaml

echo "==> Waiting for rollout"
kubectl rollout status deployment/network-monitoring-app -n network-monitoring --timeout=180s

echo
kubectl get all,hpa -n network-monitoring

echo
echo "Test with:"
echo "  kubectl port-forward svc/network-monitoring-app -n network-monitoring 8080:80"
echo "  curl http://localhost:8080/api/status"
