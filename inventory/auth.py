import hmac
from functools import wraps

from flask import abort, current_app, request


def require_api_key(view):
    """Require a valid X-API-Key header before executing a protected view."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        supplied_key = request.headers.get("X-API-Key", "")
        expected_key = current_app.config.get("API_KEY") or ""

        if not expected_key or not hmac.compare_digest(supplied_key, expected_key):
            abort(401, description="A valid API key is required")

        return view(*args, **kwargs)

    return wrapped
