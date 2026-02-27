# Architecture Overview

## System boundaries
- Django monolith with server-rendered HTML templates and Bootstrap 5 UI
- Three primary apps: `apps/core/`, `apps/matching/`, `apps/admin_views/`
- OR-Tools used for strict and exception matching

## Request routing
- Root routing and authentication live in `config/urls.py`
- App routes are defined in `apps/core/urls.py`, `apps/matching/urls.py`, `apps/admin_views/urls.py`
- Templates are organized under `templates/` per app

## Matching pipeline (canonical)
1. ORM data collection and normalization: `apps/matching/data_prep.py`
2. Solver execution:
   - Strict solver: `apps/matching/solvers/strict.py`
   - Exception solver: `apps/matching/solvers/exception.py`
3. Business rules and ambiguity detection: `apps/matching/domain.py`
4. Orchestration and persistence: `apps/matching/service.py`

## Admin workflows
- Admin dashboards and readiness: `apps/admin_views/admin_dashboard.py`
- Imports and CSV flows: `apps/admin_views/views.py`
- Run matching and results: `apps/admin_views/run_matching.py`
- Overrides and active run selection: `apps/admin_views/override_views.py`

## Data model
- Core models live in `apps/core/models.py`
- Matching models live in `apps/matching/models.py`
- Authoritative schema and rules are specified in `docs/design/TECHNICAL_SPEC.md`
