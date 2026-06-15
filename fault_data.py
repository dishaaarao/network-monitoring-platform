"""In-memory demo data for network devices, alerts, and outage simulation."""

from datetime import datetime, timezone
from copy import deepcopy

DEVICES = [
    {"id": "router-01", "type": "router", "region": "us-east-1", "status": "healthy"},
    {"id": "switch-02", "type": "switch", "region": "us-east-1", "status": "healthy"},
    {"id": "tower-03", "type": "cell-tower", "region": "us-west-2", "status": "healthy"},
    {"id": "gateway-04", "type": "gateway", "region": "eu-west-1", "status": "healthy"},
]

ALERTS = []
OUTAGE_ACTIVE = False
OUTAGE_DEVICE_ID = None


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_devices():
    return deepcopy(DEVICES)


def get_alerts():
    return deepcopy(ALERTS)


def add_alert(severity, message, device_id=None):
    alert = {
        "id": len(ALERTS) + 1,
        "severity": severity,
        "message": message,
        "device_id": device_id,
        "status": "open",
        "created_at": utc_now(),
    }
    ALERTS.append(alert)
    return alert


def simulate_outage(device_id):
    global OUTAGE_ACTIVE, OUTAGE_DEVICE_ID

    device = next((d for d in DEVICES if d["id"] == device_id), None)
    if not device:
        return None, "device not found"

    OUTAGE_ACTIVE = True
    OUTAGE_DEVICE_ID = device_id
    device["status"] = "down"

    alert = add_alert(
        severity="critical",
        message=f"Simulated outage on {device_id}",
        device_id=device_id,
    )
    return {"device": deepcopy(device), "alert": alert}, None


def recover_outage():
    global OUTAGE_ACTIVE, OUTAGE_DEVICE_ID

    if not OUTAGE_ACTIVE:
        return None, "no active outage"

    for device in DEVICES:
        if device["id"] == OUTAGE_DEVICE_ID:
            device["status"] = "healthy"

    alert = add_alert(
        severity="info",
        message=f"Recovery completed for {OUTAGE_DEVICE_ID}",
        device_id=OUTAGE_DEVICE_ID,
    )

    OUTAGE_ACTIVE = False
    recovered_device = OUTAGE_DEVICE_ID
    OUTAGE_DEVICE_ID = None

    return {"recovered_device": recovered_device, "alert": alert}, None


def platform_status():
    healthy = sum(1 for d in DEVICES if d["status"] == "healthy")
    return {
        "platform": "Network Monitoring & Fault Management Platform",
        "devices_total": len(DEVICES),
        "devices_healthy": healthy,
        "devices_down": len(DEVICES) - healthy,
        "open_alerts": sum(1 for a in ALERTS if a["status"] == "open"),
        "outage_active": OUTAGE_ACTIVE,
        "timestamp": utc_now(),
    }
