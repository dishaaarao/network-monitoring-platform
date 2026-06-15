#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing Kubernetes metrics-server (required for HPA)"
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

echo "==> Patching metrics-server for local clusters (Docker Desktop / minikube)"
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' \
  2>/dev/null || true

kubectl rollout status deployment/metrics-server -n kube-system --timeout=120s
echo "metrics-server ready"
