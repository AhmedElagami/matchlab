# 06 — User Guide

This is an end-to-end walkthrough of how MatchLab is used, from cohort creation to final export.

## Part 1: Admin workflow

### 1.1 Create a cohort

1. Log in as admin at `/auth/login/`.
2. Go to Django Admin (`/admin/`).
3. Under **Core → Cohorts**, click "Add Cohort".
4. Enter a name (e.g., "Spring 2026 Cohort") and set status to `OPEN`.
5. Optionally set `cohort_config` JSON for custom scoring weights/thresholds.
6. Save.

### 1.2 Manage organizations

Organizations are admin-managed. Before participants can set their organization, an admin must create the entries:

1. In Django Admin (`/admin/`), go to **Core → Organizations**.
2. Add organizations (e.g., "Acme Corp", "Nokia Networks").
3. Set `is_active = True` for organizations that should appear in participant dropdowns.
4. Inactive organizations are hidden from the dropdown but preserved in existing data.

### 1.3 Add participants

In Django Admin under **Core → Participants**, create entries linking each User to the cohort with a role (`MENTOR` or `MENTEE`), display name, and organization.

Alternatively, use CSV import or fixture loading (see [07-CSV-IMPORT.md](07-CSV-IMPORT.md)).

### 1.4 Monitor readiness

1. From the admin dashboard (`/dashboard/`), click a cohort name.
2. The cohort dashboard (`/cohort/<id>/dashboard/`) shows:
   - **Readiness checks**: counts balanced? All orgs set? All submitted? Sufficient mutual options?
   - **Organization distribution**: mentor/mentee counts per org.
   - **Lowest-option participants**: who has the fewest mutual cross-org options.
   - **Zero-option participants**: who has no feasible matches at all.
   - **Suggested actions**: what to fix before matching.
   - **Top pair scores**: highest-scoring potential pairs.

### 1.5 Run matching

1. Navigate to `/cohort/<id>/run-matching/`.
2. Choose a mode:
   - **Strict** — enforces all hard constraints (different org, mutual acceptability). Fails if no feasible solution exists.
   - **Exception** — allows policy violations with penalties. Always produces a complete pairing.
   - **Incremental** — requires selecting a base run. Matches only participants not already matched in the base run.
3. Click "Run".
4. On success, you're redirected to the results page.
5. On failure (strict mode), you see the failure report with diagnostics. You can then run with exceptions.

### 1.6 Review results

The results page (`/match-run/<id>/results/`) shows:
- Each mentor-mentee pair with match percentage.
- Ambiguity flags (⚠️) for close alternatives.
- Exception flags with type (E1/E2/E3) and explanation.
- Manual override indicators.
- Summary stats: total matches, ambiguous count, exception count.

### 1.7 Manual overrides

1. From the results page, click "Override".
2. Select a mentor and mentee to pair.
3. The system validates the pair and shows:
   - Whether it creates an exception.
   - A swap suggestion if both participants are already matched to others.
4. Provide an override reason (required for exception matches).
5. Confirm. The existing matches for both participants are removed and the new pair is created.

### 1.8 Set active run

1. On the results page, click "Set as Active".
2. This makes the run the official result for the cohort.
3. Participants can now see their match at `/cohort/<id>/my-match/`.

### 1.9 Export

1. From the results page, click "Export CSV" or "Export XLSX".
2. The file includes all match details — see [11-EXPORT.md](11-EXPORT.md) for column details.

---

## Part 2: Mentor workflow

### 2.1 Register and log in

1. Go to `/register/`.
2. Fill in username, email, name, password, and select role "Mentor".
3. After registration, you're logged in and redirected to home.

### 2.2 Edit profile

1. Navigate to your cohort profile (`/cohorts/<id>/profile/`).
2. Set your display name and organization (required — select from admin-managed dropdown).
3. Fill in detailed profile: job title, function, expertise tags, years of experience, bio.
4. Save.

### 2.3 Rank preferences

1. Go to `/cohorts/<id>/preferences/`.
2. You see a list of mentee candidates from other organizations.
   - Same-org mentees are hidden by default. Toggle "Show blocked" to see them (they can't be matched in strict mode).
3. Enter a numeric rank for each candidate you find acceptable (1 = top choice).
4. Duplicate ranks are automatically resolved by renumbering sequentially.
5. Click "Save Preferences".

### 2.4 Submit

1. When satisfied with your rankings, click "Submit Preferences".
2. This locks your preferences — you can no longer edit them.
3. You see a read-only view of your submitted rankings.

### 2.5 View your match

Once the admin sets an active run, visit `/cohort/<id>/my-match/` to see your assigned mentee.

---

## Part 3: Mentee workflow

### 3.1 Register and log in

Same as mentor — select role "Mentee" during registration.

### 3.2 Edit profile

1. Navigate to your cohort profile.
2. Set display name and organization (required — select from admin-managed dropdown).
3. Fill in detailed profile: job title, function, years of experience, preferred expertise, bio.
4. Optionally fill in desired mentor attributes at `/mentee/<id>/desired-attributes/`.

### 3.3 Rank preferences

Same as mentor workflow — rank mentor candidates from other organizations.

### 3.4 Submit

Same as mentor — submit locks your preferences.

### 3.5 View your match

Same as mentor — visit `/cohort/<id>/my-match/` after the admin sets an active run.
