# Folder Structure

This repo is a Django project with three main apps and a server-rendered UI.

## Top-level map
- `apps/` Django apps grouped by domain
- `config/` Django settings and root URL routing
- `templates/` Server-rendered HTML templates
- `docs/` Design and implementation docs
- `fixtures/` Django fixtures for tests and local data
- `resources/` Static assets and sample CSVs
- `playwright_tests/` Playwright E2E tests
- `scripts/` Local maintenance scripts
- `Dockerfile`, `docker-compose.yml` Production containers
- `Dockerfile.dev`, `docker-compose.dev.yml` Development containers

## Apps
- `apps/core/` Authentication, cohort selection, participant profile
- `apps/matching/` Matching domain: data prep, scoring, solvers, exports
- `apps/admin_views/` Admin dashboards, imports, run matching, overrides

## Templates
- `templates/base.html` Shared layout
- `templates/core/`, `templates/matching/`, `templates/admin_views/` App-specific pages
- `templates/participant/` Participant-facing views like `templates/participant/my_match.html`

## Data and assets
- `fixtures/` Django fixtures used by tests and local setup
- `resources/sample_data/` Sample CSV templates and test data
- `resources/assets/` Front-end static assets
- `resources/staticfiles/` Collected static output (generated)

## Matching code paths
- Canonical pipeline: `apps/matching/service.py` + `apps/matching/solvers/`

## Tests
- Unit/integration tests live under each app in `apps/*/tests/`
- End-to-end tests live in `playwright_tests/`
