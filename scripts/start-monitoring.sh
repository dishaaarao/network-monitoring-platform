#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/monitoring"

echo "==> Checking Docker..."
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running. Start Docker Desktop first."
  exit 1
fi

echo "==> Starting full platform stack..."
docker compose down >/dev/null 2>&1 || true
docker compose up -d --build

echo "==> Waiting for services..."
for i in {1..40}; do
  OK=0
  curl -sf http://localhost:8000/health >/dev/null 2>&1 && OK=$((OK+1))
  curl -sf http://localhost:9090/-/healthy >/dev/null 2>&1 && OK=$((OK+1))
  curl -sf http://localhost:3000/api/health >/dev/null 2>&1 && OK=$((OK+1))
  curl -sf http://localhost:9200 >/dev/null 2>&1 && OK=$((OK+1))
  curl -sf http://localhost:8200/v1/sys/health >/dev/null 2>&1 && OK=$((OK+1))
  if [[ "$OK" -ge 4 ]]; then
    break
  fi
  sleep 3
done

docker compose ps

echo
echo "Platform URLs (use Chrome or Safari):"
echo "  App:         http://localhost:8000"
echo "  Prometheus:  http://localhost:9090"
echo "  Grafana:     http://localhost:3000  (admin/admin)"
echo "  Kibana:      http://localhost:5601"
echo "  Vault:       http://localhost:8200  (token: root)"
echo
echo "Fault simulation:"
echo "  ./scripts/simulate-outage.sh router-01"
