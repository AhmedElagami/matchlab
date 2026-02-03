# Tester B - Playwright Run Summary

## Flows Executed
- Admin dashboard access: artifacts/ui/B/screenshots/admin_dashboard.png
- Cohort 3 strict run (not-ready dataset) -> failure report: artifacts/ui/B/screenshots/run_matching_cohort3.png, artifacts/ui/B/screenshots/strict_failure_report_cohort3.png
- Cohort 3 exception run after strict failure -> failed due to count mismatch: artifacts/ui/B/screenshots/exception_failure_cohort3.png
- Marked mentee25 submitted (admin): artifacts/ui/B/screenshots/admin_mark_submitted_mentee25.png
- Cohort 3 strict run after submission -> infeasible: artifacts/ui/B/screenshots/strict_infeasible_after_submit.png
- Cohort 3 exception run success (E2 exceptions): artifacts/ui/B/screenshots/exception_success_results_run6.png
- Added one-sided preferences for mentors 22-25: artifacts/ui/B/screenshots/admin_preferences_added.png
- Cohort 3 exception run with E1 labeling: artifacts/ui/B/screenshots/exception_success_results_run8_e1.png
- Updated cohort 3 mentee orgs to force same-org match: artifacts/ui/B/screenshots/admin_mentee_orgs_orgA.png
- Cohort 3 exception run with E3 labeling: artifacts/ui/B/screenshots/exception_success_results_run10_e3.png
- Cohort 2 strict run success (baseline happy path): artifacts/ui/B/screenshots/strict_success_results_run11.png
- Cohort 2 exception run success (determinism baseline): artifacts/ui/B/screenshots/exception_success_results_run13.png
- Empty cohort (0 participants) exception run -> failure report "No submitted participants found": artifacts/ui/B/screenshots/empty_cohort_exception_failure.png
- Penalty ordering cohort exception run (2x2) -> cross-org matches selected despite higher same-org scores: artifacts/ui/B/screenshots/penalty_ordering_exception_results_run15.png
- Preferences invalid input (non-integer rank) -> no inline error shown: artifacts/ui/B/screenshots/bad_input_non_integer_no_error.png
- Preferences duplicate ranks -> warning + success alerts: artifacts/ui/B/screenshots/duplicate_rank_warning.png

## Console/Network Logs
- Console logs: artifacts/ui/B/console_logs/console_log_run1.txt, artifacts/ui/B/console_logs/console_log_run6.txt, artifacts/ui/B/console_logs/console_log_run8.txt, artifacts/ui/B/console_logs/console_log_run10.txt, artifacts/ui/B/console_logs/console_log_run11.txt, artifacts/ui/B/console_logs/console_log_run13.txt
- Network logs: artifacts/ui/B/network_logs/network_run1.txt, artifacts/ui/B/network_logs/network_run6.txt, artifacts/ui/B/network_logs/network_run8.txt, artifacts/ui/B/network_logs/network_run10.txt, artifacts/ui/B/network_logs/network_run11.txt, artifacts/ui/B/network_logs/network_run13.txt

## Automated Playwright Tests
- pytest playwright_tests/ failed with Django async DB error (SynchronousOnlyOperation): artifacts/ui/B/playwright_cli_results.txt
