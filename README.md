# Flask Inventory API

A production-oriented Flask REST API lab demonstrating application factories,
configuration management, SQLAlchemy, CRUD endpoints, request logging,
health checks, pytest, Gunicorn, Docker, Docker Compose, Nginx, persistence,
API-key authentication, and pagination.

## Features

- Flask application factory and environment-based configuration
- SQLAlchemy inventory model and CRUD API
- JSON error responses and input validation
- Request IDs, structured logging, and security response headers
- Liveness and database-readiness endpoints
- Pytest suite with coverage enforcement
- Gunicorn production WSGI server
- Non-root Docker image and container health check
- Docker Compose deployment behind Nginx
- Persistent named Docker volume
- API-key protection for POST, PATCH, and DELETE
- Paginated item listing

## Requirements

- Python 3.12
- Docker Engine and Docker Compose plugin

## Local development

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    pip install -r requirements-dev.txt

Run tests with coverage:

    python -m pytest --cov=inventory --cov-report=term-missing --cov-fail-under=90

The completed challenge test run passed all 43 tests with 98.17% coverage.

## Docker Compose deployment

Create a local environment file:

    cp .env.example .env
    chmod 600 .env

Replace the placeholder SECRET_KEY and API_KEY values with unique,
strong random secrets. Never commit .env.

Build and start the services:

    docker compose up -d --build
    ./wait-healthy.sh
    docker compose ps

The API is exposed through Nginx on port 8080:

- API: http://localhost:8080/api/v1
- Liveness: http://localhost:8080/health/live
- Readiness: http://localhost:8080/health/ready
- Application information: http://localhost:8080/api/v1/info

Stop services without deleting persistent data:

    docker compose down

Do not use docker compose down -v if you want to retain the named database volume.

## API endpoints

| Method | Endpoint | Authentication |
|---|---|---|
| GET | /api/v1/items | Public |
| GET | /api/v1/items/<id> | Public |
| POST | /api/v1/items | X-API-Key required |
| PATCH | /api/v1/items/<id> | X-API-Key required |
| DELETE | /api/v1/items/<id> | X-API-Key required |
| GET | /health/live | Public |
| GET | /health/ready | Public |
| GET | /api/v1/info | Public |

### Create an item

    curl -X POST http://localhost:8080/api/v1/items \
      -H "Content-Type: application/json" \
      -H "X-API-Key: YOUR_API_KEY" \
      -d '{"sku":"WID-101","name":"Example Widget","quantity":10}'

### List items with pagination

    curl "http://localhost:8080/api/v1/items?page=1&per_page=20"

Pagination defaults to page 1 and 20 items per page. The maximum page size
is 100. The response includes count, items, page, per_page, and total.

## Production environment

A production environment template is provided as prod.env.example.
Copy it to prod.env, replace the placeholder secrets, and set DATABASE_URL
to the absolute path of the production SQLite database.

    cp prod.env.example prod.env
    chmod 600 prod.env

The actual prod.env file is intentionally excluded from version control.

## Database files

The repository retains the lab database files:

- instance/inventory.db — development database
- instance/prod.db — production database

The Compose deployment uses a separate persistent Docker named volume
mounted at /data.

## Security

- Never commit .env, prod.env, or real credentials.
- Use unique strong values for SECRET_KEY and API_KEY.
- Example environment files contain placeholders only.
- The Docker application runs as a non-root user.
