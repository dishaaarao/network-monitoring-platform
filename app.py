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
  <title>Network Monitoring Platform</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 20px; line-height: 1.5; }
    h1 { color: #1a73e8; }
    h2 { font-size: 1.1rem; margin-top: 28px; }
    a { color: #1a73e8; }
    .card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 12px 0; background: #fafafa; }
    code { background: #eee; padding: 2px 6px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Network Monitoring &amp; Fault Management Platform</h1>
  <p>Telecom network visibility, alerting, and fault simulation demo.</p>
  <h2>API</h2>
  <div class="card">
    <p><a href="/health">/health</a> - health check</p>
    <p><a href="/api/status">/api/status</a> - platform status</p>
    <p><a href="/api/devices">/api/devices</a> - network devices</p>
    <p><a href="/api/alerts">/api/alerts</a> - alerts</p>
    <p><a href="/metrics">/metrics</a> - Prometheus metrics</p>
  </div>
  <h2>Observability</h2>
  <div class="card">
    <p><a href="http://localhost:9090">Prometheus</a> - :9090</p>
    <p><a href="http://localhost:3000">Grafana</a> - :3000 (admin/admin)</p>
    <p><a href="http://localhost:5601">Kibana</a> - :5601</p>
    <p><a href="http://localhost:8200">Vault</a> - :8200 (token: root)</p>
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
