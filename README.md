# Mentor–Mentee Matchmaker

Server-rendered Django app that matches mentors and mentees in cohorts using OR-Tools, with strict and exception modes.

## Documentation

All documentation lives in `docs/` as numbered files. Read them in order:

| # | Document | Topic |
|---|----------|-------|
| 00 | [Index](docs/00-INDEX.md) | Master table of contents |
| 01 | [Overview](docs/01-OVERVIEW.md) | What MatchLab is, features, tech stack |
| 02 | [Getting Started](docs/02-GETTING-STARTED.md) | Developer setup, Docker, first run |
| 03 | [Architecture](docs/03-ARCHITECTURE.md) | Apps, layers, folder structure |
| 04 | [Data Model](docs/04-DATA-MODEL.md) | All models, fields, relationships |
| 05 | [Auth & Roles](docs/05-AUTHENTICATION-AND-ROLES.md) | Identity, permissions, role checks |
| 06 | [User Guide](docs/06-USER-GUIDE.md) | End-to-end walkthrough |
| 07 | [CSV Import](docs/07-CSV-IMPORT.md) | Import format, validation |
| 08 | [Matching Pipeline](docs/08-MATCHING-PIPELINE.md) | Scoring, solvers, readiness |
| 09 | [Data Flow](docs/09-DATA-FLOW.md) | Request lifecycle, contracts |
| 10 | [Results & Overrides](docs/10-RESULTS-AND-OVERRIDES.md) | Match results, manual overrides |
| 11 | [Export](docs/11-EXPORT.md) | CSV/XLSX export |
| 12 | [Deployment](docs/12-DEPLOYMENT.md) | Docker, Netlify, env vars |
| 13 | [Testing](docs/13-TESTING.md) | pytest, Playwright, CI |
| 14 | [Technical Spec](docs/14-TECHNICAL-SPEC.md) | Authoritative requirements |

## Quick start

```bash
git clone <repository-url>
cd matchlab
bash scripts/setup_dev.sh
# App: http://localhost:8001/auth/login/
# Admin: admin / admin123
```

## Entry points

- Django command entry: `manage.py`
- Settings: `config/settings.py`
- Root URL routing: `config/urls.py`
- App routing: `apps/core/urls.py`, `apps/matching/urls.py`, `apps/admin_views/urls.py`

## Top-level layout

- `apps/` — Django apps (`core`, `matching`, `admin_views`)
- `config/` — Django project settings and URL wiring
- `templates/` — Server-rendered HTML templates
- `docs/` — Numbered documentation suite
- `fixtures/` — Django fixture data for tests and local setup
- `resources/` — Static assets and sample CSV data
- `playwright_tests/` — E2E tests and Playwright config
- `scripts/` — Local utility scripts

## Matching pipeline

- Orchestration: `apps/matching/service.py`
- Data preparation: `apps/matching/data_prep.py`
- Solvers: `apps/matching/solvers/strict.py`, `apps/matching/solvers/exception.py`
- Domain rules: `apps/matching/domain.py`
