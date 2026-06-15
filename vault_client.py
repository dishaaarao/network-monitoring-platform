"""Load secrets from HashiCorp Vault when enabled."""

import os
import logging

logger = logging.getLogger("network-monitoring")

_vault_cache = {}


def vault_enabled():
    return os.getenv("VAULT_ENABLED", "false").lower() == "true"


def get_vault_secret(path="network-monitoring/app"):
    if not vault_enabled():
        return {}

    if path in _vault_cache:
        return _vault_cache[path]

    try:
        import hvac

        client = hvac.Client(
            url=os.getenv("VAULT_ADDR", "http://vault:8200"),
            token=os.getenv("VAULT_TOKEN", "root"),
        )
        if not client.is_authenticated():
            logger.warning("Vault authentication failed")
            return {}

        secret = client.secrets.kv.v2.read_secret_version(path=path)
        data = secret["data"]["data"]
        _vault_cache[path] = data
        return data
    except Exception as exc:
        logger.warning("Could not read Vault secret: %s", exc)
        return {}


def get_db_config():
    secrets = get_vault_secret()
    return {
        "db_host": secrets.get("db_host") or os.getenv("DB_HOST", "not-configured"),
        "db_user": secrets.get("db_user") or os.getenv("DB_USER", "not-configured"),
        "db_password_set": bool(secrets.get("db_password") or os.getenv("DB_PASSWORD")),
    }
