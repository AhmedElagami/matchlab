# 12 — Deployment

## Option 1: Docker Compose (primary)

### Development

```bash
docker compose -f docker-compose.dev.yml up -d
```

- App runs on **port 8001** with Django dev server (auto-reload enabled).
- PostgreSQL exposed on **port 5434** (host) → 5432 (container).
- Source code is volume-mounted for live editing.
- Uses `Dockerfile.dev` (includes `gcc`, `python3-dev`, `libpq-dev` for building dependencies).

### Production

```bash
docker compose up -d
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
```

- App runs on **port 8000** with `gunicorn`.
- Uses `Dockerfile` (slim image, runs `collectstatic` at build time).
- Static files served by WhiteNoise.
- Includes a `test` service for running Playwright E2E tests.

### Docker Compose services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `db` | `postgres:16` | 5434:5432 | PostgreSQL database |
| `app` | Built from Dockerfile | 8000 (prod) / 8001 (dev) | Django application |
| `test` | Built from Dockerfile | — | Playwright E2E tests (prod compose only) |

### Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | Yes (prod) | Dev key provided | Django secret key |
| `DJANGO_DEBUG` | No | `True` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1,0.0.0.0` | Comma-separated allowed hosts |
| `POSTGRES_DB` | No | `matchlab` | Database name |
| `POSTGRES_USER` | No | `matchlab` | Database user |
| `POSTGRES_PASSWORD` | No | `matchlab` | Database password |
| `POSTGRES_HOST` | No | `localhost` | Database host (`db` in Docker) |
| `POSTGRES_PORT` | No | `5434` | Database port |

### Production checklist

1. Set a strong `DJANGO_SECRET_KEY`.
2. Set `DJANGO_DEBUG=False`.
3. Set `DJANGO_ALLOWED_HOSTS` to your domain.
4. Use strong database credentials.
5. Run `python manage.py migrate` after deployment.
6. Run `python manage.py createsuperuser` for initial admin access.
7. Ensure the PostgreSQL volume is backed up.

## Option 2: Netlify (serverless)

MatchLab can also be deployed on Netlify using serverless functions.

### How it works

- Static files are served from Netlify's CDN (published from `resources/staticfiles`).
- Dynamic requests are routed to a Django serverless function via `awsgi`.
- Configuration is in `netlify.toml`.

### Setup

1. Connect the repository to Netlify.
2. Set environment variables in Netlify site settings:
   - All the same variables as Docker, plus an **external PostgreSQL host** (Netlify doesn't provide managed Postgres — use Supabase, Neon, or AWS RDS).
3. Deploy. Netlify runs `python manage.py collectstatic --noinput` as the build command.
4. Run migrations manually via Netlify CLI or a one-off script.

### Limitations

- No managed database — you need an external PostgreSQL provider.
- Migrations must be run manually.
- Cold starts may add latency to the first request.
- OR-Tools solver may hit serverless function time/memory limits for larger cohorts.

### Configuration (`netlify.toml`)

```toml
[build]
  command = "python manage.py collectstatic --noinput"
  publish = "resources/staticfiles"
  functions = "netlify/functions"

[build.environment]
  PYTHON_VERSION = "3.11"

[[plugins]]
  package = "netlify-plugin-django"
```

## CI/CD

GitHub Actions runs on every push and PR to `main`:

1. Spins up PostgreSQL 16 service.
2. Installs Python 3.12 and dependencies.
3. Runs migrations.
4. Collects static files.
5. Runs `pytest apps/ --tb=short -q`.

See `.github/workflows/ci.yml`.

## Python dependencies

Key production dependencies (`requirements.txt`):

| Package | Version | Purpose |
|---------|---------|---------|
| Django | ≥6.0.1 | Web framework |
| psycopg2-binary | ≥2.9.9 | PostgreSQL adapter |
| python-dotenv | ≥1.0.1 | Environment variable loading |
| gunicorn | ≥23.0.0 | Production WSGI server |
| whitenoise | ≥6.5.0 | Static file serving |
| ortools | ≥9.15.0 | OR-Tools CP-SAT solver |
| openpyxl | ≥3.1.5 | XLSX export |
| awsgi | ≥0.0.5 | Netlify serverless adapter |

Testing dependencies: `pytest`, `pytest-django`, `pytest-playwright`, `playwright`.
