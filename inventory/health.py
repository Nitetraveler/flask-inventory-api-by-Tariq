from flask import Blueprint, current_app
from sqlalchemy import text

from .extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/live")
def live():
    """Liveness: the process is up and can serve HTTP."""
    return {"status": "ok"}


@health_bp.get("/ready")
def ready():
    """Readiness: dependencies (the database) are usable."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - report any DB failure as not ready
        current_app.logger.error("Readiness check failed: %s", exc)
        return {"status": "unavailable", "database": "error"}, 503
    return {"status": "ready", "database": "ok"}
