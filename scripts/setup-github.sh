#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .git ]]; then
  git init
  git branch -M main
fi

git add .
git status

if git diff --cached --quiet; then
  echo "Nothing to commit."
else
  git commit -m "$(cat <<'EOF'
Add Network Monitoring & Fault Management Platform

Flask monitoring app, Docker, Jenkins/GitHub CI, Kubernetes manifests,
Terraform AWS IaC, Prometheus/Grafana/ELK/Vault stack, and outage simulation.
EOF
)"
fi

echo
echo "==> Next: create GitHub repo and push"
echo
cat <<'INSTRUCTIONS'
1. Create repo on GitHub: network-monitoring-platform
2. Run:
   git remote add origin https://github.com/YOUR_USERNAME/network-monitoring-platform.git
   git push -u origin main

3. Enable branch protection (GitHub UI):
   Settings -> Branches -> Add rule for main
   - Require pull request before merging
   - Require status checks: test-and-build

4. Add GitHub secrets for Docker push (optional):
   DOCKERHUB_USERNAME
   DOCKERHUB_TOKEN
INSTRUCTIONS
