import os

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
worker_class = "gthread"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "30"))
graceful_timeout = 20
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm"
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(M)sms rid=%({x-request-id}o)s'
pidfile = os.environ.get("GUNICORN_PIDFILE") or None
