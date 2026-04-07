# 13 — Testing

## Test strategy

| Layer | Tool | Location | What it covers |
|-------|------|----------|---------------|
| Unit + Integration | pytest + pytest-django | `apps/*/tests/` | Models, forms, views, scoring, solvers, readiness, export |
| E2E | Playwright (Python) | `playwright_tests/` | Full browser workflows |
| CI | GitHub Actions | `.github/workflows/ci.yml` | Runs unit/integration on every push/PR to main |

## Running tests

### Unit and integration tests

```bash
# All tests
docker compose -f docker-compose.dev.yml exec app pytest apps/ --tb=short -q

# Single app
docker compose -f docker-compose.dev.yml exec app pytest apps/matching/tests/ -q

# Single file
docker compose -f docker-compose.dev.yml exec app pytest apps/matching/tests/test_solver.py -q

# Without Docker (requires local venv + Postgres)
pytest apps/ --tb=short -q
```

### Playwright E2E tests

```bash
# Install browsers first
playwright install

# Run all E2E tests
pytest playwright_tests/

# Run with browser visible
pytest playwright_tests/ --headed

# Single test file
pytest playwright_tests/tests/test_admin_match_results.py
```

Or via Docker Compose (production compose includes a `test` service):

```bash
docker compose run test
```

## pytest configuration

`pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
addopts = --tb=short
testpaths = apps playwright_tests
```

## Test files

### `apps/core/tests/`

| File | What it tests |
|------|--------------|
| `test_models.py` | Cohort and Participant model creation, constraints |
| `test_forms.py` | ParticipantProfileForm validation |
| `test_views.py` | Home, profile, registration views |

### `apps/matching/tests/`

| File | What it tests |
|------|--------------|
| `test_models.py` | Preference, MatchRun, Match model creation |
| `test_forms.py` | PreferencesForm validation and duplicate handling |
| `test_scoring.py` | Rank score computation, pair score calculation |
| `test_solver.py` | Strict and exception solvers with small real datasets |
| `test_readiness.py` | All readiness checks and diagnostics |
| `test_export.py` | CSV and XLSX export content |
| `test_phase6.py` | Phase 6 integration tests |
| `test_phase7.py` | Phase 7 integration tests |

### `apps/admin_views/tests/`

| File | What it tests |
|------|--------------|
| `test_views.py` | Admin view access control and rendering |
| `test_forms.py` | MenteeDesiredAttributesForm |
| `test_dashboard.py` | Cohort dashboard and readiness display |
| `test_matching.py` | Run matching and results views |

### `playwright_tests/`

| File | What it tests |
|------|--------------|
| `conftest.py` | Shared fixtures: admin user, test cohort, mentor/mentee participants |
| `tests/` | E2E test files organized by feature area |

## Fixtures

### Test fixtures (pytest)

Tests use Django's test database — created fresh for each test run. Fixtures are defined in `conftest.py` files and individual test files using `@pytest.fixture`.

Common fixtures in `playwright_tests/conftest.py`:
- `admin_user` — staff/superuser for admin tests.
- `test_cohort` — a basic cohort.
- `mentor_user` / `mentee_user` — participant with user account.

### Data fixtures (JSON)

Located in `fixtures/`. Used for local development and manual testing:

| Fixture | Scenario |
|---------|----------|
| `cohort_5x5_ready.json` | 5 mentors, 5 mentees, all submitted, ready for strict matching |
| `cohort_3x3.json` | 3×3 cohort for profile and preference testing |
| `cohort_5x5_not_ready.json` | Missing submissions, readiness blockers |
| `manual_exception_e1e2.json` | Strict fails, exception produces E1/E2 |
| `manual_exception_e3.json` | Same-org exception scenario (E3) |
| `manual_multi_cohort.json` | User in multiple cohorts |
| `manual_profiles_scoring.json` | Profile cards and score breakdowns |
| `test_3x3_realistic.json` | Realistic 3×3 for automated tests |

Load a fixture:
```bash
docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_5x5_ready.json
```

## Testing rules (from AGENTS.md)

- Solver tests use small real datasets — **do not mock OR-Tools**.
- UI tests use `data-testid` attributes — **do not use CSS selectors**.
- No snapshot testing of HTML.
- No brittle CSS selector tests.
- All critical UI elements must have `data-testid` attributes.

## CI pipeline

`.github/workflows/ci.yml` runs on every push and PR to `main`:

1. Ubuntu runner with Python 3.12.
2. PostgreSQL 16 service container.
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py collectstatic --noinput`
6. `pytest apps/ --tb=short -q`

E2E tests are not run in CI (they require a running app server and browser).
