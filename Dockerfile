# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dedicated unprivileged user with a fixed UID/GID.
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home \
    --home-dir /app --shell /usr/sbin/nologin app

# Dependencies first so this layer is cached when only code changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application code stays owned by root, so the app user cannot modify it.
COPY inventory/ inventory/
COPY wsgi.py gunicorn.conf.py ./

# The only writable location for the app user. Mounted as a volume.
RUN mkdir -p /data && chown app:app /data

ENV APP_ENV=production \
    DATABASE_URL=sqlite:////data/inventory.db \
    GUNICORN_BIND=0.0.0.0:8000 \
    TRUST_PROXY=false

USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import sys, urllib.request; r = urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=2); sys.exit(0 if r.status == 200 else 1)"]

# exec makes gunicorn PID 1 so it receives SIGTERM from `docker stop`.
CMD ["sh", "-c", "flask --app inventory init-db && exec gunicorn -c gunicorn.conf.py wsgi:app"]
