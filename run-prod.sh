#!/usr/bin/env bash
# Run a command with the production environment loaded.
# Default command: gunicorn.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$PWD/.venv/bin:$PATH"
set -a
. ./prod.env
set +a
if [ "$#" -eq 0 ]; then
  set -- gunicorn -c gunicorn.conf.py wsgi:app
fi
exec "$@"
