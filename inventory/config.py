import os


def _env_bool(name, default="false"):
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Base settings shared by every environment. Values come from env vars."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key")
    API_KEY = os.environ.get("API_KEY")
    # Relative SQLite paths are placed in the app's instance/ folder by Flask-SQLAlchemy.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///inventory.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_VERSION = os.environ.get("APP_VERSION", "1.1.0")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    # Only trust X-Forwarded-* headers when running behind a proxy you control.
    TRUST_PROXY = _env_bool("TRUST_PROXY")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    API_KEY = "test-api-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "WARNING"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
