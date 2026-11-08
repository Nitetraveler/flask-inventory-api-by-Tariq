#!/usr/bin/env bash
# usage: ./wait-healthy.sh <container-name-or-id> [...]
set -euo pipefail
for c in "$@"; do
  for i in $(seq 1 40); do
    s=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$c")
    if [ "$s" = "healthy" ]; then echo "$c healthy"; break; fi
    if [ "$i" -eq 40 ]; then echo "$c NOT healthy (last status: $s)" >&2; exit 1; fi
    sleep 2
  done
done
