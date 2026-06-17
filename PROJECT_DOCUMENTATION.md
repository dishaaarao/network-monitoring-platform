# Telecom Network Monitoring & Fault Management Platform

## 📋 Executive Summary
Modern telecommunication networks experience massive traffic loads, demanding 99.999% availability. Any outage in routing hardware, switches, or firewalls translates directly to loss of service and revenue. 

This project implements a production-ready, automated **Network Monitoring & Fault Management Platform**. It leverages a robust DevOps tooling pipeline to automate application containerization, local Kubernetes orchestration, real-time telemetry ingestion, and Infrastructure-as-Code definitions.

---

## 🏗️ System Architecture

The following diagram illustrates the deployment topology, CI/CD pipeline, and telemetry collection flows:

```mermaid
flowchart TD
    subgraph Local Developer Environment
        Code[Developer Code] -->|Git Commit & Push| GitHub[GitHub Repo]
    end

    subgraph CI/CD Orchestration (Docker Compose)
        GitHub -->|Webhook / Polling| Jenkins[Jenkins CI/CD]
        Jenkins -->|1. Build Image| Docker[Docker Daemon]
        Jenkins -->|2. Run Unit Tests| PyTest[PyTest Namespace]
        Jenkins -->|3. Load Image| Kind[Kind Control Plane]
        Jenkins -->|4. Rollout Apply| K8s[Kubernetes Cluster]
    end

    subgraph Kubernetes Production Namespace (Kind)
        K8s -->|Manages| Pods[App Pods - Replicas]
        K8s -->|Exposes| Ingress[Kubernetes Ingress]
        K8s -->|Monitors| HPA[Horizontal Pod Autoscaler]
        
        Pods -->|Export Metrics| Prom[Prometheus Pod]
        Prom -->|Data Feed| Grafana[Grafana Pod]
    end
    
    subgraph Observability Outlets
        Grafana -->|Visualization| Browser[Admin UI / Grafana Portal]
    end
```

---

## 🛠️ Technical Stack & Implementation Details

### 1. Source Control (GitHub)
*   **Role**: Code custody, governance, and CI/CD triggers.
*   **Location**: `https://github.com/dishaaarao/network-monitoring-platform.git`

### 2. Containerization (Docker)
*   **Role**: Creating a standardized, lightweight, and isolated packaging runtime for the Flask-based alerting API.
*   **Manifest**: [Dockerfile](file:///Users/disharao/Desktop/devopsexternal/Dockerfile) uses multi-stage builds to optimize image layer footprint.

### 3. CI/CD Orchestration (Jenkins)
*   **Role**: Automated execution of the build, integration test, and deployment phases.
*   **Configuration**: [Jenkinsfile](file:///Users/disharao/Desktop/devopsexternal/Jenkinsfile) triggers:
    1.  **Checkout**: Pulls code updates.
    2.  **Build**: Compiles the OCI-compliant docker image.
    3.  **Test**: Spins up a container inside the Jenkins network namespace to execute endpoint queries.
    4.  **Deploy**: Loads the updated image directly into the Kind control plane and runs a rolling update on the deployment.

### 5. Container Orchestration (Kubernetes)
*   **Role**: Declarative self-healing deployments, load balancing, and autoscaling.
*   **Manifests**:
    *   `namespace.yaml`: Configures the isolated `network-monitoring` namespace.
    *   `deployment.yaml`: Defines a replica count of 2 with production-grade liveness/readiness probes.
    *   `hpa.yaml`: Horizontal Pod Autoscaler targeting CPU limits to auto-scale replicas during high traffic.

### 6. Centralized Observability (Prometheus & Grafana)
*   **Prometheus**: Ingests custom application gauge metrics (`network_devices_down_total`, `flask_http_request_total`) via pull-based scraping at 15s intervals.
*   **Grafana**: Pre-provisioned with the Prometheus data source, allowing real-time visualization of outage duration, severity levels, and recovery times.

### 7. Cloud Infrastructure as Code (Terraform)
*   **Role**: Provisioning production-ready cloud architectures on AWS.
*   **Modules**:
    *   `vpc.tf`: Multi-AZ subnets, NAT gateways, and routing tables.
    *   `eks.tf`: AWS Elastic Kubernetes Service cluster and managed node groups.
    *   `rds.tf` & `s3.tf`: Database and persistence backends.
    *   `alb.tf`: Application Load Balancers.

---

## 🔄 Outage Simulation & Verification Guide

To demonstrate the self-healing and alert telemetry pipeline:

1.  **Run Outage Simulation**:
    ```bash
    cd /Users/disharao/Desktop/devopsexternal
    BASE_URL=http://localhost:8080 bash scripts/simulate-outage.sh
    ```
2.  **Telemetry Flow**:
    *   The API marks `router-01` as `down`.
    *   A critical alert is created inside the application memory.
    *   Prometheus scrapes the `/metrics` endpoint and records `network_devices_down_total = 1`.
    *   Grafana queries Prometheus and plots a visual spike on the graph.
    *   The script completes recovery, setting the metric back to `0`.
