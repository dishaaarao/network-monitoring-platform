#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
DEVICE_ID="${1:-router-01}"

echo "==> Simulating outage on device: $DEVICE_ID"
curl -s -X POST "$BASE_URL/api/simulate-outage" \
  -H "Content-Type: application/json" \
  -d "{\"device_id\": \"$DEVICE_ID\"}" | python3 -m json.tool

echo
echo "==> Platform status"
curl -s "$BASE_URL/api/status" | python3 -m json.tool

echo
echo "==> Waiting 5 seconds..."
sleep 5

echo "==> Recovering outage"
curl -s -X POST "$BASE_URL/api/recover" | python3 -m json.tool

echo
echo "==> Final status"
curl -s "$BASE_URL/api/status" | python3 -m json.tool
