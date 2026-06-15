# Network Monitoring & Fault Management Platform

Production-inspired DevOps platform for telecom network monitoring, fault management, CI/CD, Kubernetes deployment, AWS infrastructure, and centralized observability.

## Architecture

```
GitHub -> Jenkins/GitHub Actions -> Docker Registry -> Kubernetes (EKS)
                                              |
                         Prometheus + Grafana + ELK + Vault
```

## Project structure

```
.
├── app.py                  # Flask API + fault management endpoints
├── fault_data.py           # Demo network devices, alerts, outage simulation
├── Dockerfile
├── Jenkinsfile
├── .github/workflows/ci.yml
├── k8s/                    # Kubernetes manifests
├── terraform/              # AWS IaC (VPC, EKS, RDS, S3, IAM, ALB, CloudWatch)
├── monitoring/             # Local Prometheus, Grafana, ELK, Vault stack
├── vault/                  # Vault policies
└── scripts/                # Start, deploy, outage simulation
```

## Quick start (local full stack)

```bash
chmod +x scripts/*.sh
./scripts/start-monitoring.sh
```

| Service    | URL                      | Credentials   |
|-----------|--------------------------|---------------|
| Flask app | http://localhost:8000    | -             |
| Prometheus| http://localhost:9090    | -             |
| Grafana   | http://localhost:3000    | admin / admin |
| Kibana    | http://localhost:5601    | -             |
| Vault     | http://localhost:8200    | token: root   |

## API endpoints

| Method | Endpoint               | Description              |
|--------|------------------------|--------------------------|
| GET    | `/health`              | Health check             |
| GET    | `/api/status`          | Platform status          |
| GET    | `/api/devices`         | Network devices          |
| GET    | `/api/alerts`          | List alerts              |
| POST   | `/api/alerts`          | Create alert             |
| POST   | `/api/simulate-outage` | Simulate device outage   |
| POST   | `/api/recover`         | Recover from outage      |
| GET    | `/metrics`             | Prometheus metrics       |

## Fault simulation

```bash
./scripts/simulate-outage.sh router-01
```

## Kubernetes deployment

```bash
docker build -t network-monitoring-app:latest .
./scripts/deploy-k8s.sh
kubectl port-forward svc/network-monitoring-app -n network-monitoring 8080:80
curl http://localhost:8080/api/status
```

## Terraform (AWS)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Provisions: VPC, EKS, RDS PostgreSQL, S3 logs bucket, IAM roles, ALB, CloudWatch log groups and alarms.

## CI/CD

### GitHub Actions
- Runs on push/PR to `main` and `develop`
- Installs deps, runs API tests, builds Docker image, smoke tests container

### Jenkins
- Build -> Test -> Push (configure registry) -> Deploy to Kubernetes
- Set `DOCKER_REGISTRY` and Jenkins credential `docker-registry-credentials`

### GitHub branch protection (recommended)
1. Settings -> Branches -> Add rule for `main`
2. Require pull request reviews
3. Require status checks: `test-and-build`
4. Require branches to be up to date

## Vault demo

```bash
./scripts/init-vault.sh
vault kv get secret/network-monitoring/app
```

## Portfolio checklist

- [x] Flask monitoring + fault management API
- [x] Docker containerization
- [x] Prometheus + Grafana
- [x] ELK stack (Elasticsearch + Kibana)
- [x] Vault secret management demo
- [x] Jenkins + GitHub Actions CI/CD
- [x] Kubernetes deployment, service, HPA, ingress
- [x] Terraform AWS infrastructure
- [x] Outage simulation and recovery script
- [ ] Push to GitHub and enable branch protection
- [ ] Connect Jenkins to GitHub repo
- [ ] Deploy to real AWS EKS cluster
- [ ] Create Grafana dashboards and Prometheus alert rules

## License

MIT - portfolio/educational use
