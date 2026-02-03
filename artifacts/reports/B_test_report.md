# Tester B Test Report

Date: 2026-02-03
Tester: B
Scope: Slices 5.7, 5.8, 5.9, Section 6, Section 8
Datasets: B (cohort 3 not-ready), C (penalty-ordering cohort 5), baseline cohort 2 (5x5 ready), empty cohort 4 (0x0), input validation cohort 6 (1x2)

## Environment & Data
- Services healthy: artifacts/health/B/service_status.txt
- Environment verification: artifacts/health/B/verify_env.txt
- Data seeded via fixtures + manual edits (mentee25 submission, preferences, org changes) and additional test cohorts: artifacts/datasets/B_dataset_manifest.md

## Validation Summary
- Strict failure reporting validated on cohort 3 with failure report screenshots and DB evidence (count mismatch then INFEASIBLE).
- Exception matching execution validated on cohort 3 after submission; results table populated and match runs persisted.
- Exception labeling validated across types:
  - E2 observed in run 6 (DB summary + UI).
  - E1 observed in run 8 after one-sided preferences (DB summary + UI).
  - E3 observed in run 10 after same-org forcing (DB summary + UI).
- Strict mode constraint enforcement validated on cohort 2 strict run (no same-org or non-mutual matches).
- Determinism validated by comparing consecutive exception runs on cohort 2 (runs 12/13 identical).
- Partial submission scenario captured (cohort 3 exception failed when submitted counts mismatched, consistent with readiness requirements).
- Zero-participant exception run fails with explicit error ("No submitted participants found").
- Duplicate preference ranks resolved with warning + save success.
- Non-integer rank submission via form tampering shows no inline validation error (defect).
- Timeout configuration documented (strict=5s, exception=10s).
- Penalty ordering validated with 2x2 cohort; solver selected cross-org matches despite higher same-org scores.

## DB Assertions
- Match run summaries and exception counts: artifacts/db/B/results/matchrun_6_summary.txt, artifacts/db/B/results/matchrun_8_summary.txt, artifacts/db/B/results/matchrun_10_summary.txt
- Penalty ordering run summary and matches: artifacts/db/B/results/penalty_ordering_run15_summary.txt
- Input validation setup and timeout settings: artifacts/db/B/results/input_validation_setup.txt, artifacts/db/B/results/timeout_settings.txt
- Empty cohort failure report: artifacts/db/B/results/empty_cohort_run_summary.txt
- Strict constraint checks: artifacts/db/B/results/matchrun_11_strict_checks.txt
- Determinism comparison: artifacts/db/B/results/exception_determinism_cohort2.txt
- Latest run after strict failure: artifacts/db/B/results/matchrun_latest_after_fail.txt

## Automated Playwright Tests
- pytest playwright_tests/ failed with Django async DB error: artifacts/ui/B/playwright_cli_results.txt

## Defects
- B-01, B-02 (see artifacts/tickets/B_tickets.md)

## Release Recommendation
- Release-blocking: NO
- Rationale:
  - Core strict/exception behavior and exception labeling are consistent with spec; penalty ordering validated.
  - Automated Playwright suite still fails (B-01) and inline validation missing for non-integer rank input (B-02); release decision should consider these alongside Tester A findings.
