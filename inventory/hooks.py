import re
import time
import uuid

from flask import g, request

# Accept only safe, bounded request IDs from clients (prevents log injection).
_REQUEST_ID_RE = re.compile(r"[A-Za-z0-9-]{1,64}")


def register_request_hooks(app):
    @app.before_request
    def assign_request_id():
        g.start_time = time.perf_counter()
        incoming = request.headers.get("X-Request-ID", "")
        g.request_id = incoming if _REQUEST_ID_RE.fullmatch(incoming) else uuid.uuid4().hex

    @app.after_request
    def add_headers_and_log(response):
        elapsed_ms = (time.perf_counter() - g.get("start_time", time.perf_counter())) * 1000
        request_id = g.get("request_id", "-")
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        app.logger.info(
            "method=%s path=%s status=%s duration_ms=%.1f request_id=%s client=%s",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
            request_id,
            request.remote_addr,
        )
        return response
