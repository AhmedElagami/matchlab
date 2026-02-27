# Final Manual Test Plan

This plan enumerates every implemented vertical slice and provides repeatable datasets and scripts to run the application and test manually via the UI.

## Quick start

```bash
bash scripts/start_dev_stack.sh
bash scripts/init_db.sh
bash scripts/seed_cohort_3x3.sh
```

Open the app at `http://localhost:8000/auth/login/`.

## Scripts

- `scripts/start_dev_stack.sh` - build and start the dev stack (`docker-compose.dev.yml`)
- `scripts/init_db.sh` - run migrations and ensure admin user exists
- `scripts/load_fixture.sh <fixture_path>` - flush DB, load fixture, reset passwords
- Seed helpers:
  - `scripts/seed_cohort_3x3.sh`
  - `scripts/seed_cohort_5x5_ready.sh`
  - `scripts/seed_cohort_5x5_not_ready.sh`
  - `scripts/seed_exception_e1e2.sh`
  - `scripts/seed_exception_e3.sh`
  - `scripts/seed_multi_cohort.sh`
  - `scripts/seed_profiles_scoring.sh`

## Credentials

- Admin: `admin` / `admin123`
- Fixture users: `testpass123`

## Dataset catalog

| Dataset | Script | Cohort(s) | Purpose |
| --- | --- | --- | --- |
| `fixtures/cohort_3x3.json` | `scripts/seed_cohort_3x3.sh` | Test Cohort 3x3 | Profile edits, preferences edit + submit, mentee desired attributes |
| `fixtures/cohort_5x5_ready.json` | `scripts/seed_cohort_5x5_ready.sh` | Test Cohort 5x5 Ready | Strict run success, results filters, export, set active, my match |
| `fixtures/cohort_5x5_not_ready.json` | `scripts/seed_cohort_5x5_not_ready.sh` | Test Cohort 5x5 Not Ready | Readiness blockers + diagnostics |
| `fixtures/manual_exception_e1e2.json` | `scripts/seed_exception_e1e2.sh` | Manual Exception E1/E2 | Strict failure + exception run with E1/E2 + ambiguity mix |
| `fixtures/manual_exception_e3.json` | `scripts/seed_exception_e3.sh` | Manual Exception E3 | Exception run with same-org (E3) |
| `fixtures/manual_multi_cohort.json` | `scripts/seed_multi_cohort.sh` | Multi Cohort A/B | Cohort selector UX |
| `fixtures/manual_profiles_scoring.json` | `scripts/seed_profiles_scoring.sh` | Manual Profiles & Scoring | Preferences profile cards + top score breakdowns |

## Vertical slices (E2E manual scripts)

### 1) Authentication: login, logout, registration

**Dataset:** any (use `scripts/seed_multi_cohort.sh` for clean state)

**Steps**
1. Open `http://localhost:8000/auth/login/`.
2. Fill `data-testid="login-username"` and `data-testid="login-password"` with `admin` / `admin123`, click `data-testid="login-button"`.
3. Confirm redirect to the admin dashboard (`/dashboard/`).
4. Verify the cohorts table renders and the "Django Admin" quick action is visible.
5. Click the "Django Admin" button and confirm the Django admin index loads.
6. Click `data-testid="logout-link"` in the navbar and confirm you return to the login page.
7. Go to `http://localhost:8000/register/`, register a new user, and confirm you land on the cohort selection or empty cohort screen.

**Expected**
- Admin login lands on the admin dashboard with cohort list and quick actions.
- Django admin link opens the admin index.
- Logout returns to login.
- Registration succeeds and logs you in.

### 2) Cohort selector (multi-cohort user)

**Dataset:** `scripts/seed_multi_cohort.sh`

**Accounts:** `multi_user` / `testpass123`

**Steps**
1. Login as `multi_user`.
2. Confirm cohort selector shows two cards.
3. Click `data-testid="cohort-select-<cohort_id>"` on Multi Cohort A.
4. Use the back button to return home and select Multi Cohort B.

**Expected**
- Selector lists both cohorts.
- Each selection routes to that cohort's profile page.

### 3) Participant profile (basic info)

**Dataset:** `scripts/seed_cohort_3x3.sh`

**Accounts:** `mentor1`, `mentee1` / `testpass123`

**Steps**
1. Login as `mentor1`.
2. Update `data-testid="display-name-input"` and `data-testid="organization-input"`, click `data-testid="save-profile-button"`.
3. Confirm success alert and refreshed values.
4. Repeat for `mentee1`.

**Expected**
- Profile updates persist and show success alert.

### 4) Mentee desired attributes form

**Dataset:** `scripts/seed_cohort_3x3.sh`

**Accounts:** `mentee1` / `testpass123`

**Steps**
1. Login as `mentee1`.
2. Navigate to `/mentee/<cohort_id>/desired-attributes/` (link from profile or direct URL).
3. Fill `data-testid="desired-tags-input"`, toggle `data-testid="desired-attr-remote_ok"`, add notes, click Save.
4. Refresh the page.

**Expected**
- Success alert appears.
- Checkbox selections persist on reload.
- Notes persist.

### 5) Preferences editor + show blocked + submit

**Dataset:** `scripts/seed_cohort_3x3.sh`

**Accounts:** `mentor1`, `mentee1` / `testpass123`

**Steps**
1. Login as `mentor1`, click "Manage Preferences".
2. Click `data-testid="show-blocked-toggle"` to reveal same-org candidates.
3. Drag candidates to reorder, click `data-testid="save-preferences-btn"`.
4. Click `data-testid="submit-preferences-btn"`, then confirm with `data-testid="confirm-submit-btn"`.
5. Verify you now see the read-only preferences page.
6. Repeat steps 1-5 for `mentee1`.

**Expected**
- Save shows success alert.
- Submit locks preferences and shows read-only list.
- Same-org candidates appear only when "Show Blocked" is enabled.

### 6) Admin cohort dashboard: readiness + blockers + org distribution

**Dataset:** `scripts/seed_cohort_5x5_not_ready.sh`

**Accounts:** `admin` / `admin123`

**Steps**
1. Login as admin and open the cohort dashboard for "Test Cohort 5x5 Not Ready".
2. Confirm `data-testid="readiness-status"` shows NOT READY.
3. Confirm `data-testid="blockers-list"` lists zero-option participants or suggested actions.
4. Confirm `data-testid="org-distribution-table"` renders.

**Expected**
- Readiness is NOT READY with blockers displayed.
- Org distribution table is populated.

### 7) Preferences profile cards + top score breakdowns

**Dataset:** `scripts/seed_profiles_scoring.sh`

**Accounts:** `mentor_prof_1`, `mentee_prof_1` / `testpass123` and `admin` / `admin123`

**Steps**
1. Login as `mentor_prof_1` and open "Manage Preferences".
2. Confirm candidate profile cards show job title, expertise tags, location, etc.
3. Login as `mentee_prof_1` and open "Manage Preferences", confirm mentor profile cards appear.
4. Login as admin and open cohort dashboard for "Manual Profiles & Scoring".
5. In "Top Match Scores", expand a breakdown and verify rank/tag/attribute components render.

**Expected**
- Profile cards render in preferences list.
- Score breakdown details render in the cohort dashboard.

### 8) Strict matching success + results UI filters

**Dataset:** `scripts/seed_cohort_5x5_ready.sh`

**Accounts:** `admin` / `admin123`

**Steps**
1. Login as admin, open "Run Matching" for "Test Cohort 5x5 Ready".
2. Keep `data-testid="mode-strict-radio"` selected, click `data-testid="run-strict-btn"`.
3. Confirm match results page loads and summary appears.
4. Toggle `data-testid="filter-ambiguous-toggle"`, `data-testid="filter-exceptions-toggle"` and verify table count updates in `data-testid="match-count"`.
5. Toggle `data-testid="search-toggle"`, search for a participant in `data-testid="search-input"`.

**Expected**
- Strict run succeeds and results table renders.
- Filters and search update the visible rows and match count.

### 9) Strict failure -> exception matching (E1/E2)

**Dataset:** `scripts/seed_exception_e1e2.sh`

**Accounts:** `admin` / `admin123`

**Steps**
1. Login as admin, open "Run Matching" for "Manual Exception E1/E2".
2. Run strict (`data-testid="run-strict-btn"`) and confirm failure report renders.
3. Click `data-testid="run-exception-btn"` to run exception mode.
4. On results, confirm some rows show exception badges (`data-testid="exception-pill-<id>"`).

**Expected**
- Strict run fails with a failure report.
- Exception run succeeds with E1/E2 exceptions flagged.

### 10) Export CSV/XLSX

**Dataset:** `scripts/seed_cohort_5x5_ready.sh`

**Accounts:** `admin` / `admin123`

**Steps**
1. Run strict matching (Slice 8) and open the results page.
2. Click `data-testid="export-dropdown-btn"`.
3. Download CSV with `data-testid="export-csv-btn"` and XLSX with `data-testid="export-xlsx-btn"`.

**Expected**
- Both files download successfully.

### 11) Set active run + My Match view

**Dataset:** `scripts/seed_cohort_5x5_ready.sh`

**Accounts:** `admin`, `mentor11`, `mentee11` / `testpass123`

**Steps**
1. Login as `mentor11` and click `data-testid="my-match-link"`.
2. Confirm the "No Active Match Found" empty state.
3. Logout, login as admin, run strict matching.
4. Click `data-testid="set-active-btn"` on the results page.
5. Logout, login as `mentor11` and click `data-testid="my-match-link"`.
6. Repeat for `mentee11`.

**Expected**
- My Match shows an empty state before an active run exists.
- After setting active, My Match shows the pairing with match percent and compliance state.

### 12) Manual override with exception requirement (E3)

**Dataset:** `scripts/seed_exception_e3.sh`

**Accounts:** `admin` / `admin123`

**Steps**
1. Run exception matching for "Manual Exception E3".
2. Open "Manual Override" from results.
3. Pick a mentor/mentee pair, enter a reason in `data-testid="override-reason-textarea"`, submit via `data-testid="override-save-btn"`.
4. Verify the current matches table shows "Manual" and "Exception" badges.

**Expected**
- Override succeeds only with a reason.
- Manual + exception indicators appear in the current matches table.

## Developer assignments

### Dev A - Participant flows

- Slice 1: Authentication + registration
- Slice 2: Cohort selector
- Slice 3: Participant profile (basic info)
- Slice 4: Mentee desired attributes
- Slice 5: Preferences edit + submit

**Datasets/scripts:**
- `scripts/seed_multi_cohort.sh`
- `scripts/seed_cohort_3x3.sh`

### Dev B - Admin readiness + strict success

- Slice 6: Cohort dashboard readiness
- Slice 7: Preferences profile cards + score breakdowns
- Slice 8: Strict matching success + filters
- Slice 10: Export CSV/XLSX

**Datasets/scripts:**
- `scripts/seed_cohort_5x5_not_ready.sh`
- `scripts/seed_profiles_scoring.sh`
- `scripts/seed_cohort_5x5_ready.sh`

### Dev C - Exceptions + overrides + my match

- Slice 9: Strict failure -> exception (E1/E2)
- Slice 11: Set active run + My Match
- Slice 12: Manual override (E3)

**Datasets/scripts:**
- `scripts/seed_exception_e1e2.sh`
- `scripts/seed_exception_e3.sh`
- `scripts/seed_cohort_5x5_ready.sh`
