# Developer Guide

One-stop guide for setting up, running, and working with MatchLab locally.

## Prerequisites

- Docker and Docker Compose
- Git
- At least 2GB RAM available

## Quick Start

```bash
git clone <repository-url>
cd matchlab
bash scripts/setup_dev.sh
```

This single command starts Docker services, runs migrations, creates the admin user, and loads a default fixture. When it finishes you'll see:

```
App:   http://localhost:8001/auth/login/
Admin: admin / admin123
Users: testpass123 (all fixture users)
```

To load a different fixture:

```bash
bash scripts/setup_dev.sh fixtures/cohort_3x3.json
```

## Available Fixtures

| Fixture | Purpose |
|---------|---------|
| `fixtures/cohort_5x5_ready.json` (default) | Strict matching, results, filters, export |
| `fixtures/cohort_3x3.json` | Profile edits, preferences, mentee attributes |
| `fixtures/cohort_5x5_not_ready.json` | Readiness blockers and diagnostics |
| `fixtures/manual_exception_e1e2.json` | Strict failure + exception run (E1/E2) |
| `fixtures/manual_exception_e3.json` | Same-org exception (E3) |
| `fixtures/manual_multi_cohort.json` | Multi-cohort selector UX |
| `fixtures/manual_profiles_scoring.json` | Profile cards + score breakdowns |

## Environment Variables

Set via `docker-compose.dev.yml` (no `.env` file needed for local dev):

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | dev key | Django secret key |
| `DJANGO_DEBUG` | `True` | Debug mode |
| `POSTGRES_DB` | `matchlab` | Database name |
| `POSTGRES_USER` | `matchlab` | Database user |
| `POSTGRES_PASSWORD` | `matchlab` | Database password |
| `POSTGRES_HOST` | `db` | Database host (Docker service) |
| `POSTGRES_PORT` | `5432` | Database port (internal) |

The database is exposed on `localhost:5434` if you need direct access.

## Running Tests

```bash
# All unit/integration tests
docker compose -f docker-compose.dev.yml exec app pytest apps/ --tb=short -q

# Single app
docker compose -f docker-compose.dev.yml exec app pytest apps/matching/tests/ -q
```

Tests run against a separate test database — they don't affect your dev data. See `docs/testing/automated_tests.md` for the full test breakdown.

## Common Tasks

### Restart the app after code changes

The dev server auto-reloads on file changes. If it crashes:

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

## CI

GitHub Actions runs the full test suite on every push and PR to `main`. See `.github/workflows/ci.yml`. The workflow spins up a Postgres service, runs migrations, and runs `pytest apps/`.

## Project Structure

```
apps/           Django apps (core, matching, admin_views)
config/         Settings, URL routing, WSGI
templates/      Server-rendered HTML templates
fixtures/       Demo and test data
scripts/        Dev utility scripts
docs/           Design and implementation docs
```

Key files:
- `config/settings.py` — all Django settings
- `apps/matching/service.py` — matching orchestration
- `apps/matching/solvers/` — strict and exception solvers
- `docs/design/TECHNICAL_SPEC.md` — business rules and requirements

## Performance Notes

- Cohort size assumed ≤ 30 participants
- OR-Tools time limits: 5s strict, 10s exception mode
