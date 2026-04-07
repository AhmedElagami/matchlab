# 02 — Getting Started

## Prerequisites

- Docker and Docker Compose
- Git
- At least 2 GB RAM available

## Quick start

```bash
git clone <repository-url>
cd matchlab
bash scripts/setup_dev.sh
```

This single command:
1. Starts PostgreSQL and the Django dev server via Docker Compose.
2. Waits for the database to be ready.
3. Runs migrations.
4. Creates an admin user (`admin` / `admin123`).
5. Loads the default fixture (`fixtures/cohort_5x5_ready.json`).
6. Sets all fixture user passwords to `testpass123`.

When it finishes:

```
App:   http://localhost:8001/auth/login/
Admin: admin / admin123
Users: testpass123 (all fixture users)
```

## Loading a different fixture

```bash
bash scripts/setup_dev.sh fixtures/cohort_3x3.json
```

## Available fixtures

| Fixture | Purpose |
|---------|---------|
| `cohort_5x5_ready.json` (default) | Strict matching, results, filters, export |
| `cohort_3x3.json` | Profile edits, preferences, mentee attributes |
| `cohort_5x5_not_ready.json` | Readiness blockers and diagnostics |
| `manual_exception_e1e2.json` | Strict failure → exception run (E1/E2) |
| `manual_exception_e3.json` | Same-org exception (E3) |
| `manual_multi_cohort.json` | Multi-cohort selector UX |
| `manual_profiles_scoring.json` | Profile cards and score breakdowns |

## Environment variables

Set automatically by `docker-compose.dev.yml` — no `.env` file needed for local dev.

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | dev key | Django secret key |
| `DJANGO_DEBUG` | `True` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,0.0.0.0` | Allowed hosts |
| `POSTGRES_DB` | `matchlab` | Database name |
| `POSTGRES_USER` | `matchlab` | Database user |
| `POSTGRES_PASSWORD` | `matchlab` | Database password |
| `POSTGRES_HOST` | `db` | Database host (Docker service name) |
| `POSTGRES_PORT` | `5432` | Database port (internal) |

The database is exposed on `localhost:5434` for direct access.

## Common tasks

### Restart after code changes

The dev server auto-reloads. If it crashes:

```bash
docker compose -f docker-compose.dev.yml restart app
```

### View logs

```bash
docker compose -f docker-compose.dev.yml logs app -f
docker compose -f docker-compose.dev.yml logs db -f
```

### Reset everything

```bash
docker compose -f docker-compose.dev.yml down -v
bash scripts/setup_dev.sh
```

### Run migrations after model changes

```bash
docker compose -f docker-compose.dev.yml exec app python manage.py makemigrations
docker compose -f docker-compose.dev.yml exec app python manage.py migrate
```

### Database backup / restore

```bash
# Backup
docker compose -f docker-compose.dev.yml exec db pg_dump -U matchlab matchlab > backup.sql

# Restore
docker compose -f docker-compose.dev.yml exec -T db psql -U matchlab matchlab < backup.sql
```

## Running tests

```bash
# All unit/integration tests
docker compose -f docker-compose.dev.yml exec app pytest apps/ --tb=short -q

# Single app
docker compose -f docker-compose.dev.yml exec app pytest apps/matching/tests/ -q
```

Tests use a separate test database and don't affect dev data. See [13-TESTING.md](13-TESTING.md) for the full test strategy.
