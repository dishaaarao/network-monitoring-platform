#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=============================================="
echo " Network Monitoring Platform - Full Setup"
echo "=============================================="

chmod +x "$ROOT_DIR"/scripts/*.sh

echo
echo "[1/4] Starting monitoring stack..."
"$ROOT_DIR/scripts/start-monitoring.sh"

sleep 5

echo
echo "[2/4] Initializing Vault secrets..."
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
if command -v vault >/dev/null 2>&1; then
  "$ROOT_DIR/scripts/init-vault.sh"
else
  echo "Vault CLI not installed. Seed secrets manually or use Vault UI at http://localhost:8200"
  docker exec vault vault secrets enable -path=secret kv-v2 2>/dev/null || true
  docker exec -e VAULT_TOKEN=root vault vault kv put secret/network-monitoring/app \
    db_host=postgres-demo db_user=nmadmin db_password=demo-password-from-vault 2>/dev/null || true
fi

echo
echo "[3/4] Running outage simulation demo..."
"$ROOT_DIR/scripts/simulate-outage.sh" router-01

echo
echo "[4/4] Optional next steps:"
echo "  Kubernetes:  ./scripts/deploy-k8s.sh"
echo "  Jenkins:     ./scripts/start-jenkins.sh"
echo "  GitHub:      ./scripts/setup-github.sh"
echo "  Terraform:   cd terraform && terraform init && terraform plan"
