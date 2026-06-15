# Network Monitoring & Fault Management Platform — Project Explanation

**Subject:** DevOps  
**Industry:** Telecom  
**Project type:** Production-ready DevOps platform for network monitoring and fault management

---

## 1. What is this project?

Telecom networks have thousands of routers, switches, towers, and gateways. When something fails, teams need to:

1. **See** what is healthy and what is down (visibility)
2. **Get alerts** quickly when faults happen
3. **Deploy** monitoring software reliably and at scale
4. **Observe** metrics and logs in one place
5. **Recover** from outages in a controlled way

This project builds a **DevOps platform** that solves those problems using industry-standard tools: GitHub, Docker, Jenkins, Kubernetes, Terraform, AWS, Prometheus, Grafana, ELK, and Vault.

The **Flask application** is a demo monitoring service. It exposes health checks, metrics, network device status, alerts, and outage simulation. The real value for your DevOps subject is the **pipeline and infrastructure around the app**.

---

## 2. How the project maps to your problem statement

### Problem statement challenges

| Challenge | How this project addresses it |
|-----------|--------------------------------|
| Large-scale network visibility | `/api/devices`, `/api/status` show device health across regions |
| Alert processing delays | `/api/alerts`, outage simulation creates and tracks alerts |
| Deployment bottlenecks | Docker + Jenkins + GitHub Actions automate build and deploy |
| Infrastructure inconsistency | Terraform provisions the same AWS resources every time |
| Observability gaps | Prometheus (metrics), Grafana (dashboards), ELK (logs), CloudWatch (AWS logs) |

---

## 3. Architecture (big picture)

```
Developer
   |
   v
GitHub (source code + CI workflow)
   |
   +---> GitHub Actions (automated test + Docker build)
   |
   +---> Jenkins (full CI/CD: build, test, push, deploy)
           |
           v
       Docker Image (network-monitoring-app)
           |
           v
       Kubernetes / AWS EKS (2+ replicas, HPA autoscaling)
           |
           +---> Flask App (monitoring + fault APIs)
           |
           +---> Prometheus (scrapes /metrics)
           +---> Grafana (visualizes metrics)
           +---> ELK (Elasticsearch + Kibana for logs)
           +---> Vault (secrets: DB password, API keys)
           |
           v
       AWS (Terraform): VPC, EKS, RDS, S3, IAM, ALB, CloudWatch
```

**Flow in simple words:**

1. You write code and push to GitHub.
2. CI runs tests and builds a Docker image.
3. Jenkins (or GitHub Actions) can push the image to a registry.
4. Kubernetes runs multiple copies of the app for high availability.
5. Prometheus collects metrics; Grafana shows graphs; Kibana shows logs.
6. Vault stores secrets so passwords are not hard-coded.
7. Terraform creates all AWS cloud resources with code.

---

## 4. Project folder structure explained

| Folder / File | Purpose |
|---------------|---------|
| `app.py` | Main Flask app: health, metrics, devices, alerts, outage APIs |
| `fault_data.py` | Demo data: network devices, alerts, outage simulation logic |
| `wsgi.py` | Entry point for Gunicorn (production server) |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Packages the app into a container image |
| `Jenkinsfile` | Jenkins pipeline: build → test → push → deploy |
| `.github/workflows/ci.yml` | GitHub Actions CI on every push/PR |
| `k8s/` | Kubernetes YAML manifests (deployment, service, HPA, ingress, monitoring) |
| `terraform/` | AWS infrastructure as code |
| `monitoring/` | Local Docker Compose stack (app + Prometheus + Grafana + ELK + Vault) |
| `vault/` | Vault access policies |
| `scripts/` | Helper scripts to start stack, deploy, simulate outages |
| `README.md` | Quick reference commands |

---

## 5. Application APIs explained

| Endpoint | Method | What it does |
|----------|--------|--------------|
| `/` | GET | Home page with links to all services |
| `/health` | GET | Returns `{"status": "ok"}` — used by Kubernetes probes |
| `/metrics` | GET | Prometheus metrics (request count, latency, etc.) |
| `/api/status` | GET | Platform summary: devices up/down, open alerts, outage state |
| `/api/devices` | GET | List of telecom devices (routers, switches, towers) |
| `/api/alerts` | GET | List all alerts |
| `/api/alerts` | POST | Create a new alert manually |
| `/api/simulate-outage` | POST | Simulates a device going down + creates critical alert |
| `/api/recover` | POST | Recovers device and logs recovery alert |
| `/api/config` | GET | Shows non-secret config (secrets come from Vault in production) |

**Outage simulation example:**

```bash
./scripts/simulate-outage.sh router-01
```

This demonstrates **fault detection → alert → recovery validation**, which matches your implementation strategy.

---

## 6. DevOps components explained (for viva / exam)

### GitHub
- Stores all project code
- `.github/workflows/ci.yml` runs automated tests on every push
- Branch protection (to be enabled) prevents broken code on `main`

### Docker
- `Dockerfile` builds a portable image
- Same image runs on your laptop, Jenkins, and Kubernetes
- Fixes "works on my machine" and deployment inconsistency

### Jenkins
- `Jenkinsfile` defines pipeline stages
- Automates: checkout → build image → test → push to registry → deploy to K8s
- Reduces manual deployment errors

### Kubernetes
- Runs the app in containers across multiple nodes
- **Deployment:** 2 replicas for high availability
- **Service:** exposes app on port 80 internally
- **HPA:** auto-scales pods when CPU goes above 50%
- **Ingress:** routes external traffic to the app
- **Probes:** `/health` checks if pods are alive and ready

### Terraform
- Code that creates AWS resources
- Includes: VPC, EKS, RDS, S3, IAM, ALB, CloudWatch
- `terraform apply` creates; `terraform destroy` removes
- Ensures repeatable, version-controlled infrastructure

### AWS services in this project

| AWS Service | Role in project |
|-------------|-----------------|
| **EKS** | Managed Kubernetes cluster in the cloud |
| **RDS** | PostgreSQL database for alerts/devices (future persistence) |
| **S3** | Stores logs and artifacts |
| **IAM** | Roles and permissions for EKS nodes and app |
| **CloudWatch** | Central logging and CPU alarms |
| **ALB** | Load balancer sends traffic to healthy app instances |

### Prometheus
- Scrapes `/metrics` from the Flask app every 15 seconds
- Stores time-series data (CPU, HTTP requests, errors)

### Grafana
- Connects to Prometheus
- Shows dashboards and graphs for monitoring

### ELK Stack
- **Elasticsearch:** stores logs
- **Kibana:** search and visualize logs (port 5601)
- Helps debug faults and audit alert processing

### Vault
- Stores secrets (DB passwords, API keys) securely
- App reads secrets at runtime instead of hard-coding them
- `scripts/init-vault.sh` seeds demo secrets

---

## 7. What is COMPLETED (as of now)

### Implementation strategy checklist

| Step | Status | Evidence in project |
|------|--------|---------------------|
| Configure GitHub workflows | ✅ Done (code) | `.github/workflows/ci.yml` |
| Configure branch protection | ⚠️ Pending (manual) | Must enable in GitHub UI after push |
| Build Docker images | ✅ Done | `Dockerfile`, image `network-monitoring-app` |
| Integrate container registry | ⚠️ Partial | Jenkinsfile has push stage (needs credentials) |
| Configure Jenkins CI/CD | ✅ Done (code) | `Jenkinsfile` |
| Run Jenkins pipeline live | ⚠️ Pending | Needs Jenkins server + GitHub connection |
| Deploy Kubernetes workloads | ✅ Done (manifests) | `k8s/deployment.yaml`, `service.yaml`, etc. |
| Kubernetes autoscaling | ✅ Done | `k8s/hpa.yaml` (2–5 replicas, CPU-based) |
| Deploy to live K8s cluster | ⚠️ Pending | Run `./scripts/deploy-k8s.sh` on your cluster |
| Provision cloud with Terraform | ✅ Done (code) | `terraform/*.tf` |
| Run Terraform on AWS | ⚠️ Pending | Needs AWS account + `terraform apply` |
| Configure monitoring | ✅ Done (local) | Prometheus + Grafana in `monitoring/` and `k8s/monitoring/` |
| Configure logging (ELK) | ✅ Done (local) | Elasticsearch + Kibana in `docker-compose.yml` |
| Configure alerting | ⚠️ Partial | Alerts in app API; Prometheus alert rules not yet added |
| Vault secret management | ✅ Done (demo) | Vault in compose + `vault/policies/` + `init-vault.sh` |
| Simulate outages | ✅ Done | `scripts/simulate-outage.sh`, `/api/simulate-outage`, `/api/recover` |
| Validate recovery | ✅ Done | `/api/recover` + simulation script |

### Technical implementation checklist

| Technology | Code ready | Live / operational |
|------------|-------------|-------------------|
| GitHub | ✅ | ⚠️ Repo not pushed yet |
| Docker | ✅ | ✅ Runs locally |
| Jenkins | ✅ | ⚠️ Not connected |
| Kubernetes | ✅ | ⚠️ Manifests only (unless you deployed) |
| Terraform | ✅ | ⚠️ Not applied to AWS |
| AWS (EKS, RDS, S3, IAM, CloudWatch, ALB) | ✅ in Terraform | ⚠️ Not provisioned |
| Prometheus | ✅ | ✅ Local stack works |
| Grafana | ✅ | ✅ Local stack works |
| ELK | ✅ | ✅ Local stack works |
| Vault | ✅ | ✅ Local dev mode works |

### Overall completion estimate

| Area | Progress |
|------|----------|
| Application + fault management demo | **90%** |
| Docker + local observability stack | **85%** |
| CI/CD configuration (files) | **80%** |
| Kubernetes manifests | **85%** |
| Terraform / AWS IaC | **75%** (code written, not applied) |
| Live end-to-end cloud deployment | **15%** |
| **Total project vs full problem statement** | **~65%** (codebase) / **~35%** (live demo) |

---

## 8. TODO list — what to do next

Use this as your roadmap. Work top to bottom.

### Phase A — GitHub and source control (Priority: HIGH)

- [x] Initialize local git repository and initial commit
- [x] Add GitHub Actions CI workflow (`.github/workflows/ci.yml`)
- [x] Add branch protection template (`.github/branch-protection.yml`)
- [x] Add `scripts/setup-github.sh` with push instructions
- [ ] Create GitHub repository and push code (manual — needs your GitHub account)
- [ ] Enable branch protection on `main` in GitHub UI
- [ ] Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets for image push

### Phase B — Container registry (Priority: HIGH)

- [x] Add `registry.env.example` and `.env.example`
- [x] Add optional Docker Hub push job in GitHub Actions
- [ ] Create Docker Hub repository
- [ ] Add registry credentials to Jenkins
- [ ] Uncomment push commands in `Jenkinsfile` after credentials exist

### Phase C — Jenkins live CI/CD (Priority: HIGH)

- [x] Add local Jenkins via `jenkins/docker-compose.yml`
- [x] Add `scripts/start-jenkins.sh`
- [ ] Start Jenkins: `./scripts/start-jenkins.sh`
- [ ] Complete Jenkins setup wizard at http://localhost:8081
- [ ] Connect Jenkins pipeline to GitHub repo

### Phase D — Kubernetes deployment (Priority: HIGH)

- [x] Enhanced `scripts/deploy-k8s.sh`
- [x] Add `scripts/install-metrics-server.sh` for HPA
- [x] Add `k8s/vault-secret.yaml.example`
- [ ] Enable Kubernetes in Docker Desktop
- [ ] Run `./scripts/deploy-k8s.sh`
- [ ] Verify HPA with metrics-server

### Phase E — AWS + Terraform (Priority: MEDIUM)

- [x] Terraform code for VPC, EKS, RDS, S3, IAM, ALB, CloudWatch
- [ ] Create AWS account and configure `aws configure`
- [ ] Run `terraform init` and `terraform apply`

### Phase F — Monitoring, logging, alerting (Priority: MEDIUM)

- [x] Prometheus alert rules (`monitoring/prometheus-alerts.yml`)
- [x] Grafana dashboard auto-provisioning (`monitoring/grafana-dashboard.json`)
- [x] Custom metric `network_devices_down_total`
- [ ] Create Kibana index pattern after ELK is running
- [ ] Connect CloudWatch after AWS deploy

### Phase G — Security with Vault (Priority: MEDIUM)

- [x] `vault_client.py` reads secrets from Vault via `hvac`
- [x] `/api/config` shows Vault-backed DB config (no password exposed)
- [x] `scripts/init-vault.sh` seeds demo secrets
- [ ] Use production Vault token in K8s (`k8s/vault-secret.yaml`)

### Phase H — One-command setup

- [x] `scripts/setup-all.sh` — starts stack, Vault, outage demo

---

## 9. Commands you should know

### Start full local platform

```bash
./scripts/start-monitoring.sh
```

### Test APIs

```bash
curl http://localhost:8000/api/status
curl http://localhost:8000/api/devices
```

### Simulate outage and recovery

```bash
./scripts/simulate-outage.sh router-01
```

### Deploy to Kubernetes

```bash
docker build -t network-monitoring-app:latest .
./scripts/deploy-k8s.sh
```

### Provision AWS (when ready)

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Initialize Vault secrets

```bash
./scripts/init-vault.sh
```

---

## 10. How to explain this project in an interview (30-second pitch)

> "I built a telecom Network Monitoring and Fault Management Platform using DevOps practices. The Flask service exposes health checks, Prometheus metrics, device status, and fault simulation APIs. I containerized it with Docker, automated CI/CD with Jenkins and GitHub Actions, defined Kubernetes deployments with autoscaling, and wrote Terraform to provision AWS EKS, RDS, S3, IAM, ALB, and CloudWatch. For observability I integrated Prometheus, Grafana, and ELK, and used Vault for secret management. I also scripted outage simulation and recovery to validate fault-handling workflows."

---

## 11. Summary

**What you have:** A complete DevOps project **codebase** covering application, containers, CI/CD configs, Kubernetes, Terraform, monitoring, logging, secrets, and fault simulation.

**What you still need:** Connect everything to **live** services — GitHub repo, Jenkins runs, container registry, Kubernetes cluster, and AWS account — then demo the full pipeline end to end.

**Next recommended step:** Push to GitHub → enable GitHub Actions → deploy locally to Kubernetes with `./scripts/deploy-k8s.sh`.

---

*Last updated: June 2026*
