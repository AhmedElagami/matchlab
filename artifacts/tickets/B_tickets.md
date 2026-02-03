# Tester B Defect Tickets

## B-01 [Automation] Playwright pytest fails with Django async DB error
- Severity: Medium
- Steps to reproduce:
  1. Run `docker compose -f docker-compose.dev.yml exec app env DJANGO_SETTINGS_MODULE=config.settings pytest playwright_tests/`
- Observed: Tests error in fixture when creating admin user with `SynchronousOnlyOperation: You cannot call this from an async context`.
- Expected: Playwright pytest suite should create Django users without async DB errors (configure sync DB access in async tests or allow async-unsafe DB access).
- Evidence: artifacts/ui/B/playwright_cli_results.txt

## B-02 [Validation][Slice 8] Non-integer rank input shows no inline error
- Severity: Medium
- Steps to reproduce:
  1. Log in as `input_mentor_bb0705` (password `test123`).
  2. Open `/cohorts/6/preferences/`.
  3. Use browser devtools to modify a hidden rank input (`#rank_<candidate_id>`) to a non-integer value (e.g., `abc`).
  4. Click Save Preferences.
- Observed: No inline validation error or alert message is shown; page re-renders silently.
- Expected: Server-side validation should reject non-integer ranks and show an inline error or alert message.
- Evidence: artifacts/ui/B/screenshots/bad_input_non_integer_no_error.png
