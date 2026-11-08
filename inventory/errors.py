import json

from flask import current_app
from werkzeug.exceptions import HTTPException

from .extensions import db


def _json_body(status, error, message):
    return json.dumps({"error": error, "message": message, "status": status})


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc):
        response = exc.get_response()  # keeps headers such as Allow / Location
        response.data = _json_body(exc.code, exc.name, exc.description)
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc):
        db.session.rollback()
        current_app.logger.exception("Unhandled exception: %s", exc)
        # Never leak internal details (stack traces, SQL) to clients.
        return current_app.response_class(
            _json_body(500, "Internal Server Error", "An unexpected error occurred"),
            status=500,
            mimetype="application/json",
        )
