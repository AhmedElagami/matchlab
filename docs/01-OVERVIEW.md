# 01 — Overview

## What is MatchLab?

MatchLab is a self-hosted web application that matches mentors and mentees within cohorts. An admin creates a cohort, participants register and rank each other, and the system produces an optimal one-to-one pairing using Google OR-Tools (CP-SAT solver).

## Who uses it?

- **Admins** — create cohorts, import data, run matching, review results, export, override.
- **Mentors** — fill out a profile, rank acceptable mentees, submit preferences.
- **Mentees** — fill out a profile, describe desired mentor attributes, rank acceptable mentors, submit preferences.

## Key features

| Feature | Description |
|---------|-------------|
| Cohort management | Create cohorts, assign participants, track status (Draft → Open → Closed → Matched) |
| Preference ranking | Participants rank candidates from the opposite role; same-org candidates are hidden by default |
| Strict matching | OR-Tools CP-SAT solver enforces hard constraints: different orgs, mutual acceptability |
| Exception matching | When strict is infeasible, produces a complete pairing with flagged policy exceptions (E1/E2/E3) |
| Incremental matching | Builds on a previous run to match only remaining unmatched participants |
| Readiness dashboard | Shows submission counts, org distribution, option counts, blockers, suggested fixes |
| Ambiguity detection | Flags matches where the score gap to the next-best alternative is within a configurable threshold |
| Manual overrides | Admin can reassign pairs with validation and mandatory reason for exception matches |
| Active run | Admin commits a specific run as the "active" result; participants see their match |
| Export | CSV and XLSX with full match details including exception flags and override reasons |
| Scoring transparency | Pair scores stored with breakdowns; currently rank-based (spec allows future tag/attribute weights) |

## Tech stack

| Layer | Technology |
|-------|------------|
| Framework | Django 6.x (server-rendered, no SPA) |
| Database | PostgreSQL 16 |
| Solver | Google OR-Tools CP-SAT |
| UI | Bootstrap 5, Django templates |
| Static files | WhiteNoise |
| Export | openpyxl (XLSX), csv (CSV) |
| Testing | pytest + pytest-django, Playwright |
| CI | GitHub Actions |
| Deployment | Docker Compose (primary), Netlify serverless (optional) |

## Constraints

- Cohort size: 10–30 mentors and 10–30 mentees.
- One-to-one pairing only.
- End-to-end matching must complete within 30 seconds.
- OR-Tools time limits: 5s strict, 10s exception.
