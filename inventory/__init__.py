import logging
import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import config_by_name
from .extensions import db


def _configure_logging(app):
    """Log to stderr (12-factor). Docker / systemd collect the stream."""
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config["LOG_LEVEL"])
    app.logger.propagate = False


def create_app(config_name=None):
    config_name = config_name or os.environ.get("APP_ENV", "development")
    if config_name not in config_by_name:
        raise ValueError(
            f"Unknown APP_ENV '{config_name}', expected one of {sorted(config_by_name)}"
        )

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config["APP_ENV"] = config_name

    if config_name == "production" and app.config["SECRET_KEY"] == "dev-insecure-key":
        raise RuntimeError("SECRET_KEY must be set in production")

    if config_name == "production" and not app.config["API_KEY"]:
        raise RuntimeError("API_KEY must be set in production")

    _configure_logging(app)

    if app.config["TRUST_PROXY"]:
        # Trust exactly one proxy hop for client IP, scheme and host.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)

    from . import models  # noqa: F401
    from .api import api_bp
    from .cli import register_cli
    from .errors import register_error_handlers
    from .health import health_bp
    from .hooks import register_request_hooks

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    register_error_handlers(app)
    register_request_hooks(app)
    register_cli(app)

    app.logger.info(
        "Application created (env=%s, version=%s)", config_name, app.config["APP_VERSION"]
    )
    return app
