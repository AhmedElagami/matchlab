# Mentor–Mentee Matchmaker

Server-rendered Django app that matches mentors and mentees in cohorts using OR-Tools, with strict and exception modes defined in `docs/design/TECHNICAL_SPEC.md`.

## Start here
- Product and business rules: `docs/design/TECHNICAL_SPEC.md`
- Operations and deployment: `docs/design/OPERATIONAL_DOCS.md`
- Architecture overview: `docs/architecture.md`
- Folder map: `docs/folder-structure.md`

## Entry points
- Django command entry: `manage.py`
- Settings: `config/settings.py`
- Root URL routing: `config/urls.py`
- App routing: `apps/core/urls.py`, `apps/matching/urls.py`, `apps/admin_views/urls.py`

## Top-level layout
- `apps/` Django apps (`core`, `matching`, `admin_views`)
- `config/` Django project settings and URL wiring
- `templates/` Server-rendered HTML templates
- `docs/` Design and implementation documentation
- `fixtures/` Django fixture data for tests and local setup
- `resources/` Static assets and sample CSV data
- `playwright_tests/` E2E tests and Playwright config
- `scripts/` Local utility scripts
- `docker-compose.yml`, `Dockerfile` Production container setup
- `docker-compose.dev.yml`, `Dockerfile.dev` Development container setup

## Matching pipeline (canonical)
- Orchestration: `apps/matching/service.py`
- Data preparation: `apps/matching/data_prep.py`
- Solvers: `apps/matching/solvers/strict.py`, `apps/matching/solvers/exception.py`
- Domain rules: `apps/matching/domain.py`

## Local artifacts
- Local runtime files like `.env`, `db.sqlite3`, `venv/`, and caches should remain uncommitted (see `.gitignore`).

## Full Documentation at https://deepwiki.com/AhmedElagami/matchlab
