import logging
import os

from flask import Flask, jsonify, request, Response
from prometheus_client import Gauge
from prometheus_flask_exporter import PrometheusMetrics

from fault_data import (
    add_alert,
    get_alerts,
    get_devices,
    platform_status,
    recover_outage,
    simulate_outage,
)
from vault_client import get_db_config, vault_enabled

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("network-monitoring")

app = Flask(__name__)
PrometheusMetrics(app)

DEVICES_DOWN = Gauge(
    "network_devices_down_total",
    "Number of network devices in down state",
)


def update_device_metrics():
    status = platform_status()
    DEVICES_DOWN.set(status["devices_down"])

HOME_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Network Monitoring & Fault Management Platform</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-gradient-start: #0a0f1d;
      --bg-gradient-end: #070a13;
      --card-bg: rgba(16, 22, 42, 0.65);
      --card-border: rgba(255, 255, 255, 0.08);
      --text-main: #f3f4f6;
      --text-secondary: #9ca3af;
      --accent-cyan: #00f2fe;
      --accent-blue: #4facfe;
      --accent-green: #00f5a0;
      --accent-green-glow: rgba(0, 245, 160, 0.2);
      --accent-purple: #7f53ac;
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      background: linear-gradient(135deg, var(--bg-gradient-start), var(--bg-gradient-end));
      color: var(--text-main);
      font-family: 'Outfit', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
      overflow-x: hidden;
    }
    
    /* Background decorative glow elements */
    .glow-sphere {
      position: absolute;
      width: 400px;
      height: 400px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(79, 172, 254, 0.12) 0%, rgba(0, 0, 0, 0) 70%);
      top: -100px;
      left: -100px;
      z-index: 0;
      pointer-events: none;
    }
    .glow-sphere-2 {
      position: absolute;
      width: 500px;
      height: 500px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0, 242, 254, 0.08) 0%, rgba(0, 0, 0, 0) 70%);
      bottom: -100px;
      right: -100px;
      z-index: 0;
      pointer-events: none;
    }
    
    .container {
      max-width: 1000px;
      width: 100%;
      z-index: 1;
    }
    
    header {
      text-align: center;
      margin-bottom: 40px;
      position: relative;
    }
    
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(0, 245, 160, 0.1);
      border: 1px solid var(--accent-green);
      color: var(--accent-green);
      padding: 6px 16px;
      border-radius: 100px;
      font-weight: 500;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 16px;
      box-shadow: 0 0 15px var(--accent-green-glow);
    }
    
    .status-dot {
      width: 8px;
      height: 8px;
      background-color: var(--accent-green);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
      0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(0, 245, 160, 0.7);
      }
      70% {
        transform: scale(1);
        box-shadow: 0 0 0 8px rgba(0, 245, 160, 0);
      }
      100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(0, 245, 160, 0);
      }
    }
    
    h1 {
      font-size: 2.8rem;
      font-weight: 700;
      background: linear-gradient(135deg, #ffffff 30%, var(--accent-cyan) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
      letter-spacing: -0.5px;
    }
    
    .subtitle {
      color: var(--text-secondary);
      font-size: 1.1rem;
      font-weight: 300;
      max-width: 600px;
      margin: 0 auto;
    }
    
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
      gap: 24px;
      margin-top: 20px;
    }
    
    @media (max-width: 768px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
      }
      h1 {
        font-size: 2rem;
      }
    }
    
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-radius: 16px;
      padding: 28px;
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
      position: relative;
      overflow: hidden;
    }
    
    .card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 4px;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
      opacity: 0.8;
    }
    
    .card:hover {
      transform: translateY(-5px);
      border-color: rgba(255, 255, 255, 0.15);
      box-shadow: 0 12px 40px 0 rgba(79, 172, 254, 0.15);
    }
    
    .card-title {
      font-size: 1.4rem;
      font-weight: 600;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #ffffff;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 12px;
    }
    
    .card-title svg {
      width: 20px;
      height: 20px;
      fill: var(--accent-cyan);
    }
    
    .list-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.03);
      border-radius: 8px;
      margin-bottom: 12px;
      transition: all 0.2s ease;
    }
    
    .list-item:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.08);
      transform: translateX(4px);
    }
    
    .item-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    
    .method-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }
    
    .method-get {
      background: rgba(0, 245, 160, 0.15);
      color: var(--accent-green);
      border: 1px solid rgba(0, 245, 160, 0.3);
    }
    
    .method-post {
      background: rgba(79, 172, 254, 0.15);
      color: var(--accent-blue);
      border: 1px solid rgba(79, 172, 254, 0.3);
    }
    
    .endpoint-link {
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-main);
      text-decoration: none;
      font-size: 0.95rem;
      font-weight: 500;
      transition: color 0.2s ease;
    }
    
    .endpoint-link:hover {
      color: var(--accent-cyan);
    }
    
    .item-desc {
      color: var(--text-secondary);
      font-size: 0.85rem;
      font-weight: 300;
    }
    
    .port-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      background: rgba(255, 255, 255, 0.05);
      padding: 2px 6px;
      border-radius: 4px;
      color: var(--text-secondary);
    }
    
    .obs-icon {
      width: 20px;
      height: 20px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 6px;
    }
    
    footer {
      margin-top: 60px;
      text-align: center;
      color: var(--text-secondary);
      font-size: 0.85rem;
      font-weight: 300;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      padding-top: 20px;
      width: 100%;
    }
  </style>
</head>
<body>
  <div class="glow-sphere"></div>
  <div class="glow-sphere-2"></div>
  
  <div class="container">
    <header>
      <div class="status-badge">
        <span class="status-dot"></span>
        Platform Active
      </div>
      <h1>DevOps Monitoring Pipeline</h1>
      <p class="subtitle">Fault Management &amp; Centralized Observability Orchestrator</p>
    </header>
    
    <div class="dashboard-grid">
      <!-- API CARD -->
      <div class="card">
        <h2 class="card-title">
          <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
          REST API Control Center
        </h2>
        
        <div class="list-item">
          <div class="item-left">
            <span class="method-badge method-get">GET</span>
            <a class="endpoint-link" href="/health">/health</a>
          </div>
          <span class="item-desc">API Health Status</span>
        </div>
        
        <div class="list-item">
          <div class="item-left">
            <span class="method-badge method-get">GET</span>
            <a class="endpoint-link" href="/api/status">/api/status</a>
          </div>
          <span class="item-desc">Platform Metrics</span>
        </div>
        
        <div class="list-item">
          <div class="item-left">
            <span class="method-badge method-get">GET</span>
            <a class="endpoint-link" href="/api/devices">/api/devices</a>
          </div>
          <span class="item-desc">Network Topology</span>
        </div>
        
        <div class="list-item">
          <div class="item-left">
            <span class="method-badge method-get">GET</span>
            <a class="endpoint-link" href="/api/alerts">/api/alerts</a>
          </div>
          <span class="item-desc">Active Fault Alerts</span>
        </div>
        
        <div class="list-item">
          <div class="item-left">
            <span class="method-badge method-get">GET</span>
            <a class="endpoint-link" href="/metrics">/metrics</a>
          </div>
          <span class="item-desc">Prometheus Metrics</span>
        </div>
      </div>
      
      <!-- OBSERVABILITY CARD -->
      <div class="card">
        <h2 class="card-title">
          <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
          Telemetry &amp; Access Controls
        </h2>
        
        <div class="list-item">
          <div class="item-left">
            <span class="obs-icon">🔥</span>
            <a class="endpoint-link" href="http://localhost:9091" target="_blank">Prometheus Console</a>
          </div>
          <span class="port-label">PORT 9091</span>
        </div>
        
        <div class="list-item">
          <div class="item-left">
            <span class="obs-icon">📊</span>
            <a class="endpoint-link" href="http://localhost:3001" target="_blank">Grafana Dashboards</a>
          </div>
          <span class="port-label">PORT 3001</span>
        </div>
        
        <div class="list-item">
          <div class="item-left">
            <span class="obs-icon">🔎</span>
            <a class="endpoint-link" href="http://localhost:5601" target="_blank">Kibana Logging (ELK)</a>
          </div>
          <span class="port-label">PORT 5601</span>
        </div>
        
        <div class="list-item">
          <div class="item-left">
            <span class="obs-icon">🔑</span>
            <a class="endpoint-link" href="http://localhost:8200" target="_blank">HashiCorp Vault</a>
          </div>
          <span class="port-label">PORT 8200</span>
        </div>
      </div>
    </div>
    
    <footer>
      Network Monitoring &amp; Fault Management Platform &bull; Production DevOps Pipeline Verified
    </footer>
  </div>
</body>
</html>"""


@app.route("/")
def index():
    return Response(HOME_PAGE, mimetype="text/html; charset=utf-8")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/status")
def status():
    update_device_metrics()
    return jsonify(platform_status())


@app.route("/api/devices")
def devices():
    return jsonify({"devices": get_devices()})


@app.route("/api/alerts", methods=["GET", "POST"])
def alerts():
    if request.method == "GET":
        return jsonify({"alerts": get_alerts()})

    data = request.get_json(silent=True) or {}
    severity = data.get("severity", "warning")
    message = data.get("message")
    device_id = data.get("device_id")

    if not message:
        return jsonify({"error": "message is required"}), 400

    alert = add_alert(severity=severity, message=message, device_id=device_id)
    logger.warning("Alert created: %s", alert)
    return jsonify(alert), 201


@app.route("/api/simulate-outage", methods=["POST"])
def outage():
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id", "router-01")
    result, error = simulate_outage(device_id)

    if error:
        return jsonify({"error": error}), 404

    logger.error("Outage simulated on %s", device_id)
    update_device_metrics()
    return jsonify({"message": "outage simulated", **result}), 201


@app.route("/api/recover", methods=["POST"])
def recover():
    result, error = recover_outage()

    if error:
        return jsonify({"error": error}), 400

    logger.info("Recovery completed: %s", result)
    update_device_metrics()
    return jsonify({"message": "recovery completed", **result})


@app.route("/api/config")
def config():
    db_config = get_db_config()
    return jsonify(
        {
            "environment": os.getenv("APP_ENV", "development"),
            "vault_enabled": vault_enabled(),
            "db_host": db_config["db_host"],
            "db_user": db_config["db_user"],
            "db_password_configured": db_config["db_password_set"],
        }
    )
