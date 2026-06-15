#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting Jenkins (http://localhost:8081)"
cd "$(dirname "$0")/../jenkins"
docker compose up -d

echo
echo "Get initial admin password:"
echo "  docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"
echo
echo "Jenkins setup:"
echo "  1. Open http://localhost:8081"
echo "  2. Install suggested plugins"
echo "  3. Create admin user"
echo "  4. Install Docker Pipeline plugin"
echo "  5. Add credentials: docker-registry-credentials (Docker Hub user/pass)"
echo "  6. Create Pipeline job -> Pipeline script from SCM -> Git -> point to your repo"
echo "  7. Set DOCKER_REGISTRY environment in job or Jenkins global env"
