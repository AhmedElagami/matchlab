# Tester A Defect Tickets

## A-02 [Dataset] Fixtures overwrite admin user created by reset script
- Severity: Medium
- Steps to reproduce:
  1. Run scripts/reset_testing_env.sh (creates admin user)
  2. Load fixtures via loaddata fixtures/cohort_3x3.json
  3. Run scripts/verify_tester_a_env.sh
- Observed: Admin user missing after fixture load (fixtures include auth.user pk=1), requiring manual recreation.
- Expected: Fixtures should not overwrite admin user created by reset script, or reset script should be run after fixtures.
- Evidence: fixtures/cohort_3x3.json (auth.user pk=1), artifacts/datasets/reseed_A.sh (admin recreation step added)

## A-03 [Dataset] mentor1/mentee1 credentials in tester script do not match fixtures
- Severity: Medium
- Steps to reproduce:
  1. Load fixtures/cohort_3x3.json
  2. Attempt login as mentor1 with test123 per tester_a_script.md
- Observed: Fixture password hash does not correspond to documented test123; login fails without manual password reset.
- Expected: Fixtures should set known credentials matching tester script, or script should document required reset step.
- Evidence: docs/testing/tester_a_script.md, fixtures/cohort_3x3.json (password hash), artifacts/datasets/reseed_A.sh (manual reset step)

## A-04 [Slice 5.6][Dataset A] Strict matching fails for "Test Cohort 5x5 Ready"
- Severity: High
- Steps to reproduce:
  1. Login as admin
  2. Navigate to /cohort/2/run-matching/
  3. Click Run Strict Matching
- Observed: Strict run fails as INFEASIBLE with multiple zero-option participants.
- Expected: Dataset labeled "Ready" should pass strict mode without exceptions.
- Evidence: artifacts/ui/A/screenshots/strict_matching_failed.png, artifacts/db/A/results/match_run_summary.txt

## A-05 [Slice 5.6][UI] Strict failure alert shows "Unknown error"
- Severity: Medium
- Steps to reproduce:
  1. Login as admin
  2. Run strict matching for /cohort/2/run-matching/
- Observed: Toast displays "Strict matching failed: Unknown error" despite a detailed failure report shown below.
- Expected: Alert should show the specific failure reason (e.g., INFEASIBLE) or surfaced diagnostics.
- Evidence: artifacts/ui/A/screenshots/strict_matching_failed.png

## A-06 [Slice 5.11][UI] JS TypeError on failed run results page
- Severity: Medium
- Steps to reproduce:
  1. Login as admin
  2. Navigate to /match-run/1/results/
- Observed: Console errors "TypeError: Cannot read properties of null" on page load.
- Expected: Results page should render without JS errors.
- Evidence: artifacts/ui/A/console_logs/page_errors_match_run_1.txt, artifacts/ui/A/screenshots/strict_run_failed_results.png

## A-07 [Slice 5.12][Export] CSV export missing required cohort column
- Severity: High
- Steps to reproduce:
  1. Login as admin
  2. Open /match-run/2/results/
  3. Export CSV
- Observed: CSV headers omit required "cohort" column specified in docs/design/TECHNICAL_SPEC.md.
- Expected: CSV should include cohort column alongside mentor/mentee fields.
- Evidence: artifacts/ui/A/match_results_2.csv, docs/design/TECHNICAL_SPEC.md

## A-08 [Slice 5.1][Auth] Logout endpoint does not support GET
- Severity: Low
- Steps to reproduce:
  1. Navigate to /auth/logout/ via browser GET
- Observed: Server responds 405 (Method Not Allowed) on GET.
- Expected: Logout should be accessible via GET link in UI or provide a clear logout flow for non-admin users.
- Evidence: artifacts/health/A/logout_status.txt
