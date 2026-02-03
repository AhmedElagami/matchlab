# Tester A - Playwright Run Summary

## Flows Executed
- Unauthenticated access redirects:
  - /dashboard/ (login redirect) - artifacts/ui/A/screenshots/unauth_dashboard_redirect.png
  - /cohort/1/run-matching/ (login redirect) - artifacts/ui/A/screenshots/unauth_run_matching_redirect.png
  - /match-run/1/results/ (login redirect) - artifacts/ui/A/screenshots/unauth_results_redirect.png
- Non-admin access (mentor1/test123):
  - Admin pages redirect to login (blocked):
    - /dashboard/ - artifacts/ui/A/screenshots/non_admin_dashboard_blocked.png
    - /cohort/1/run-matching/ - artifacts/ui/A/screenshots/non_admin_run_matching_blocked.png
    - /import/mentor-csv/ - artifacts/ui/A/screenshots/non_admin_import_blocked.png
  - IDOR attempt /cohorts/2/profile/ blocked with alert - artifacts/ui/A/screenshots/non_admin_idor_blocked.png
  - Profile validation (organization required) - artifacts/ui/A/screenshots/profile_validation_error.png
- Admin access (admin/admin123):
  - Admin dashboard - artifacts/ui/A/screenshots/admin_dashboard.png
  - Cohort creation (Test Cohort A) - artifacts/ui/A/screenshots/cohort_created_admin.png
  - Cohort status transitions to Open/Closed - artifacts/ui/A/screenshots/cohort_status_open.png, artifacts/ui/A/screenshots/cohort_status_closed.png
  - Participant creation (Mentor Eleven QA in Test Cohort A) - artifacts/ui/A/screenshots/participant_created_admin.png
  - Run matching (cohort 2):
    - Pre-run page - artifacts/ui/A/screenshots/run_matching_ready_before.png
    - Strict run failed - artifacts/ui/A/screenshots/strict_matching_failed.png
    - Exception run success + results table - artifacts/ui/A/screenshots/exception_results.png
  - Failed strict results view - artifacts/ui/A/screenshots/strict_run_failed_results.png
  - Run history list - artifacts/ui/A/screenshots/run_history.png
  - Admin IDOR non-existent cohort 999 -> 404 - artifacts/ui/A/screenshots/admin_idor_404.png

## Exports
- CSV export saved to artifacts/ui/A/match_results_2.csv
- XLSX export saved to artifacts/ui/A/match_results_2.xlsx

## CSRF Evidence
- Hidden CSRF token present on run-matching form (view-source blocked by Playwright protocol restrictions): artifacts/ui/A/csrf_token_snippet.txt

## Console/Network Logs
- Console log collection via Playwright MCP returned no entries: artifacts/ui/A/console_logs/console_messages.txt
- Network log collection via Playwright MCP returned no entries: artifacts/ui/A/network_logs/network_requests.txt
- Playwright event stream surfaced errors during navigation:
  - favicon 404
  - TypeError on /match-run/1/results/ (details captured in test report)
