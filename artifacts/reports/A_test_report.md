# Tester A Test Report

Date: 2026-02-03
Tester: A
Scope: Slices 5.1, 5.2, 5.3, 5.6, 5.11, 5.12, 5.15
Datasets: A (5x5 ready), B (3x3 access-control), C (5x5 not-ready)

## Environment & Data
- Environment reset: scripts/reset_testing_env.sh (artifacts/health/A/reset_env_output.txt)
- Services healthy: artifacts/health/A/service_status.txt
- Data seeded via fixtures + post-seed fixes: artifacts/datasets/A_dataset_manifest.md

## Validation Summary
- Slice 5.1 Authentication & Access Control
  - Unauthenticated redirects confirmed (screenshots in artifacts/ui/A/screenshots)
  - Non-admin blocked from admin pages (redirects to login) and IDOR blocked with alert
  - Logout endpoint GET returns 405 (A-08)
- Slice 5.2 Cohort Creation & Configuration
  - Cohort creation and status transitions verified in Django admin (screenshots)
- Slice 5.3 Participant Management
  - Participant created in Django admin (screenshots)
  - Profile validation error for required organization confirmed (screenshots)
- Slice 5.6 Strict Matching Execution
  - Strict run for "Test Cohort 5x5 Ready" fails (A-04)
  - Exception run succeeds and results table populated (screenshots + DB evidence)
- Slice 5.11 Run History & Detail Views
  - Run history list shows recent runs (screenshots)
  - Failed run detail page renders but logs JS errors (A-06)
- Slice 5.12 CSV Export Correctness
  - CSV and XLSX export downloads confirmed
  - CSV missing required cohort column (A-07)
- Slice 5.15 UI Consistency Across Modes
  - Strict success results not available due to strict failure (blocked by A-04)

## DB Assertions
- Match runs and matches verified via psql (artifacts/db/A/db_assertions.md)
- Match run summary and match details captured (artifacts/db/A/results)

## Automated Playwright Tests
- pytest playwright_tests/ failed: pytest not installed (artifacts/ui/A/playwright_cli_results.txt)

## Defects
- A-01, A-02, A-03, A-04, A-05, A-06, A-07, A-08 (see artifacts/tickets/A_tickets.md)

## Release Recommendation
- Release-blocking: YES
- Rationale:
  - Strict matching fails on "ready" dataset (A-04)
  - CSV export missing required cohort column (A-07)
  - JavaScript errors on failed run results page (A-06)
  - Documentation/data inconsistencies affecting testability (A-01, A-02, A-03)
