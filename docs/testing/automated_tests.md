# Automated Test Suite

## Overview

Tests are run by **pytest** with the **pytest-django** plugin. Django provides the test infrastructure (test database, transactions, test client), while pytest handles discovery and execution.

Configuration lives in `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
addopts = --tb=short
testpaths = apps playwright_tests
```

## Running Tests

```bash
# All unit/integration tests
pytest apps/ --tb=short -q

# Single app
pytest apps/matching/tests/ -q

# Single test file
pytest apps/matching/tests/test_scoring.py -q

# Single test method
pytest apps/matching/tests/test_scoring.py::ScoringTest::test_compute_rank_score -q
```

## CI

Tests run automatically on every push/PR to `main` via GitHub Actions (`.github/workflows/ci.yml`). The CI workflow:

1. Spins up a Postgres 16 service container
2. Installs Python 3.12 + dependencies
3. Runs migrations
4. Collects static files
5. Runs `pytest apps/`

Playwright E2E tests are excluded from CI (they require a live server + browser).

## Test Breakdown by App

### apps/core/tests/ (12 tests)

| File | Tests | What it covers |
|------|-------|----------------|
| test_models.py | 4 | Cohort/Participant string repr, unique constraints |
| test_forms.py | 3 | ParticipantProfileForm validation (required fields) |
| test_views.py | 5 | Auth redirects, profile display, form validation |

### apps/admin_views/tests/ (9 tests)

| File | Tests | What it covers |
|------|-------|----------------|
| test_dashboard.py | 3 | Cohort dashboard access control, page load, data-testid presence |
| test_forms.py | 2 | MenteeDesiredAttributesForm validation |
| test_matching.py | 4 | Run matching view, results view, export |
| test_views.py | 2 | Login required, mentee desired attributes POST |

### apps/matching/tests/ (42 tests)

| File | Tests | What it covers |
|------|-------|----------------|
| test_scoring.py | 3 | Rank score math, pair scores with/without preferences |
| test_readiness.py | 10 | Count checks, missing orgs/submissions, mutual acceptability, org distribution |
| test_solver.py | 5 | Strict solver, ambiguity detection, matching service, CSV export |
| test_phase6.py | 9 | Exception classification (E1/E2/E3), priority ordering, strict infeasible, exception solver |
| test_phase7.py | 8 | Override validation, manual overrides, active match run management |
| test_models.py | 2 | Preference creation, unique constraints |
| test_forms.py | 2 | Preference form creation, duplicate rank handling |
| test_export.py | 1 | CSV export includes audit fields |

## Notes

- Solver tests use small real datasets (no OR-Tools mocking), so they take ~2 minutes total.
- Each test runs in a database transaction that rolls back after, so tests don't interfere with each other.
- Duplicate key errors in Postgres logs during CI are expected — they come from tests verifying unique constraints.
