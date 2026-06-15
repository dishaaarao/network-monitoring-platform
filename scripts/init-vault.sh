#!/usr/bin/env bash
set -euo pipefail

export VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
export VAULT_TOKEN="${VAULT_TOKEN:-root}"

seed() {
  vault secrets enable -path=secret kv-v2 2>/dev/null || true
  vault kv put secret/network-monitoring/app \
    db_host="postgres-demo" \
    db_user="nmadmin" \
    db_password="demo-password-from-vault"
  vault kv get secret/network-monitoring/app
}

if command -v vault >/dev/null 2>&1; then
  echo "==> Seeding Vault via local CLI"
  seed
elif docker ps --format '{{.Names}}' | grep -q '^vault$'; then
  echo "==> Seeding Vault via Docker container"
  docker exec -e VAULT_TOKEN=root vault vault secrets enable -path=secret kv-v2 2>/dev/null || true
  docker exec -e VAULT_TOKEN=root vault vault kv put secret/network-monitoring/app \
    db_host="postgres-demo" \
    db_user="nmadmin" \
    db_password="demo-password-from-vault"
  docker exec -e VAULT_TOKEN=root vault vault kv get secret/network-monitoring/app
else
  echo "Vault is not running. Start ./scripts/start-monitoring.sh first."
  exit 1
fi
