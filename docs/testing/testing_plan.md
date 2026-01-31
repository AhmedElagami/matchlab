# MatchLab — Comprehensive Manual Technical Testing Plan (Docker + MCP-assisted)

This document is a **manual, technical, end-to-end test plan** for the MatchLab Django application (mentor–mentee matchmaker) run in **Docker**, executed by human testers with optional assistance from **MCP tools** (browser automation, DB inspection, filesystem access, and log inspection).  
Assumptions are explicitly documented where the repository does not fully specify behavior.

Sources consulted: repository operational docs, technical spec, and implementation snippets. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1} :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3} :contentReference[oaicite:4]{index=4}

---

## 1. Purpose & Definition of Done

### Purpose
Validate that MatchLab:
- Supports mentors, mentees, organizations, and ranked preferences.
- Normalizes rank-based preference inputs into consistent scoring behavior.
- Computes pair scores deterministically and explainably.
- Produces one-to-one matching via two modes:
  - **STRICT**: forbidden unless cross-org **and** mutually acceptable. :contentReference[oaicite:5]{index=5}
  - **EXCEPTION**: always returns complete pairing; violations are penalized and labeled (E1/E2/E3). :contentReference[oaicite:6]{index=6}
- Detects ambiguity and persists match-run history.
- Exposes correct admin workflows (run matching, export, set active run, overrides) and correct participant workflows (profile, preferences, submission, “my match” view).
- Produces correct CSV (and optional XLSX) exports including auditability fields. :contentReference[oaicite:7]{index=7} :contentReference[oaicite:8]{index=8}

### Definition of “working correctly”
A release is “working correctly” if all of the following are true:
1. **Security & permissions**  
   - No unauthenticated access to cohort-scoped pages.
   - Participants can only edit their own cohort data; no IDOR.
   - Admin-only actions are admin-only (matching, exports, overrides, CSV import, setting active run). :contentReference[oaicite:9]{index=9}
2. **Data integrity**
   - Participants are unique per cohort-user.
   - Preferences are unique per (cohort, from, to) and only across mentor↔mentee roles. :contentReference[oaicite:10]{index=10}
   - Each match run stores its input, status, and results immutably (no destructive overwrite of history).
3. **Matching correctness**
   - Strict mode never violates org constraint or mutual acceptability. :contentReference[oaicite:11]{index=11}
   - Exception mode produces a complete assignment and labels any violations accurately:
     - **E1**: one-sided acceptability
     - **E2**: neither acceptable
     - **E3**: same org (highest severity) :contentReference[oaicite:12]{index=12}
4. **Explainability & auditability**
   - Each match row has match percent, ambiguity flag/reason, exception flag/type/reason, and manual override markers where applicable. :contentReference[oaicite:13]{index=13} :contentReference[oaicite:14]{index=14}
5. **Operational stability**
   - Runs complete within expected bounds for N ≤ 30 with configured OR-Tools time limits. :contentReference[oaicite:15]{index=15}

### Quality gates (acceptance criteria)
A release is acceptable only when:
- All vertical feature slices in Section 5 pass on **Happy-path** dataset and at least one non-happy dataset.
- Strict infeasibility is detected and reported with actionable failure details.
- Exception mode produces results with correct penalty ordering and correct labeling.
- Exports are correct and consistent across UI, DB, and file output.
- No high/critical findings remain in:
  - access control
  - strict-mode constraint enforcement
  - exception labeling correctness
  - audit trail persistence

---

## 2. Testing Strategy

### Manual-first philosophy
- MatchLab’s core risks are in **workflow correctness**, **policy constraints**, **explainability**, and **security boundaries**. These are best validated through direct UI use + DB verification rather than relying on automation alone.
- The plan prioritizes **human inspection** of UI states (messages, tables, forms, toggles) and **data persistence**.

### Vertical feature slices (why)
- The application is workflow-driven: changes in preferences affect scoring, which affects solver outcomes, which affects exports and “my match” views.
- Testing “vertically” validates **full-stack behavior** (UI → DB → solver → exports) and catches integration defects that unit-level checks cannot.

### How MCP assists (but does not replace judgment)
Use MCP tools to:
- Drive repeatable browser steps (login, navigation, form submission) while a tester validates outcomes.
- Inspect DB rows to confirm persisted results (runs, matches, flags).
- Pull and compare exported files from the container/filesystem.
- Review application logs for solver mode, duration, and exception counts.

MCP must **not** be treated as an oracle: testers still evaluate correctness of flags, explanations, and whether results make policy sense.

---

## 3. Environment Setup

### Docker-based setup steps
Use the repository’s Docker Compose setup. :contentReference[oaicite:16]{index=16}
1. Start services:
   - `docker compose up -d` (or repository equivalent)
2. Run migrations:
   - `docker compose exec app python manage.py migrate`
3. Create an admin user (superuser) for admin workflows.
4. Access the app at `http://localhost:8000`. :contentReference[oaicite:17]{index=17}

**Note:** A dev Dockerfile may auto-load a fixture (`fixtures/cohort_3x3.json`). Treat that as the default baseline dataset if present. :contentReference[oaicite:18]{index=18}

### Database reset strategy
Goal: repeatable clean starts per dataset.
- Preferred: remove the Postgres volume and recreate:
  - Stop services → remove volumes → start services → migrate → load dataset.
- Alternative: use Django admin to delete cohort-scoped objects for the cohort under test, but only if you can guarantee no cross-cohort contamination.

**Tester rule:** before each dataset run, confirm the DB contains only the intended cohorts and no residual match_runs/matches for the target cohort.

### Logging and evidence collection
Evidence artifacts required per test session:
- Screenshot(s) of:
  - run-matching screen before and after execution
  - strict failure report (if applicable)
  - results table with flags visible
  - override confirmation (if used)
  - export download action and file presence
- Log capture:
  - app logs around match run start/end and mode used. (The spec expects mode + duration + exception counts to be logged.) :contentReference[oaicite:19]{index=19}
- DB evidence:
  - snapshot of match_run row (mode, status, objective_summary/failure_report)
  - snapshot of matches rows (flags, types, reasons, manual override fields) :contentReference[oaicite:20]{index=20}

---

## 4. Canonical Test Datasets

All datasets must include:
- At least 1 cohort
- Equal number of submitted mentors and mentees (unless explicitly testing mismatch)
- Organizations set
- Preferences set according to the scenario
- PairScore computed (either precomputed by dashboard or computed by system)

### Dataset A — Happy-path (Strict feasible, no exceptions)
**Purpose:** Validate normal operation end-to-end in strict mode:
- strict feasibility
- mutual acceptability
- cross-org enforcement
- deterministic scoring and solver results
- export correctness

**Minimum shape:** 3x3 or 2x2.
- Use the repository’s `cohort_3x3` fixture if available as baseline, then ensure mutual cross-org preferences exist. :contentReference[oaicite:21]{index=21}
- Expected outcome: strict run succeeds, **exception_flag = false** for all matches, ambiguity may or may not occur depending on score gaps.

Validates:
- strict constraints: org != and mutual acceptability. :contentReference[oaicite:22]{index=22}
- match_run SUCCESS persistence.
- CSV export headers and data presence. :contentReference[oaicite:23]{index=23}

### Dataset B — Strict-infeasible (must fail strict, succeed exception)
**Purpose:** Validate strict failure detection/reporting and exception fallback behavior.
Create a cohort where strict constraints make assignment impossible due to either:
- org distribution causing unavoidable same-org pairing, or
- missing mutual acceptability edges.

Example constructions:
1. **Acceptability infeasible**: no mutual acceptability edges exist (e.g., no preferences entered).
2. **Org infeasible**: org assignments make cross-org one-to-one impossible.

Expected:
- STRICT run status = FAILED with meaningful failure_report.
- EXCEPTION run status = SUCCESS with complete matching and exception labeling.

Validates:
- strict infeasible detection. :contentReference[oaicite:24]{index=24}
- “Run with exceptions” behavior and exception labeling. :contentReference[oaicite:25]{index=25}

### Dataset C — Pathological / Edge-case (ambiguity + penalty ordering + override stress)
**Purpose:** Probe correctness under tricky scoring/constraint boundaries:
- Ambiguity detection when top two options are close (gap ≤ threshold). :contentReference[oaicite:26]{index=26}
- Penalty ordering in exception mode: E3 worst, then E2, then E1. :contentReference[oaicite:27]{index=27}
- Determinism (repeat runs yield same results for same inputs).
- Manual override validation and audit persistence. :contentReference[oaicite:28]{index=28}

Construction:
- Dense preferences with near-equal pair scores (e.g., similar tags/attributes) to force small score gaps.
- Create a situation where exception mode must choose between:
  - one same-org violation vs multiple acceptability violations, to confirm org penalty dominates.

Expected:
- ambiguity_flag true for at least one participant with a clear reason naming the near alternative.
- exception matches labeled correctly and consistently with the scenario.
- overrides recorded with is_manual_override and override_reason.

---

## 5. Vertical Feature Slice Test Plan

For each slice below, execute on Dataset A, then rerun the most relevant slices on Dataset B and C.

**DB inspection note:** Use MCP DB inspection to locate and verify rows in:
- `core_cohort`, `core_participant`
- `matching_preference`, `matching_pairscore`
- `matching_matchrun`, `matching_match`
- `matching_activematchrun` (or similarly named table for active runs) :contentReference[oaicite:29]{index=29}

### Slice 5.1 — Authentication & access control

**Preconditions**
- Docker app running.
- Admin user exists.
- At least one mentor and one mentee user exist (fixture or manually created).

**Manual actions**
1. Visit `/auth/login/`.
2. Attempt access to admin-only pages while logged out:
   - admin dashboard
   - run matching
   - export
   - override
3. Log in as a mentee:
   - attempt to access admin pages
4. Log in as admin:
   - access admin pages

**Expected UI behavior**
- Logged out: redirected to login for protected pages.
- Non-admin: blocked from admin-only pages (redirect or error).
- Admin: full access. :contentReference[oaicite:30]{index=30}

**Expected DB state**
- Session authentication created; no domain object changes.

**Expected solver behavior**
- None.

**Expected exports**
- None.

**Negative/edge cases**
- Attempt direct URL access to another cohort’s participant page (“IDOR test”): should be blocked with an error and redirect. :contentReference[oaicite:31]{index=31}
- CSRF: verify all POST actions present CSRF token (visible in page source or by successful POST only via form submission). :contentReference[oaicite:32]{index=32}

---

### Slice 5.2 — Cohort creation & configuration

**Assumption**
- Cohorts are managed primarily via Django Admin or a custom admin dashboard. The spec includes cohort dashboard and readiness diagnostics; configuration knobs may be stored in JSON (`cohort_config`). :contentReference[oaicite:33]{index=33} :contentReference[oaicite:34]{index=34}

**Preconditions**
- Admin access.

**Manual actions**
1. Create a new cohort (via admin interface).
2. Set status transitions (DRAFT → OPEN → CLOSED/MATCHED as supported).
3. Populate `cohort_config` with relevant knobs if UI supports it (min strict options, ambiguity gap, penalties).

**Expected UI behavior**
- Cohort appears on admin dashboard list; participant counts update. :contentReference[oaicite:35]{index=35}
- Cohort dashboard loads and shows readiness elements.

**Expected DB state**
- Cohort row created with status and cohort_config persisted. :contentReference[oaicite:36]{index=36}

**Expected solver behavior**
- None.

**Negative/edge cases**
- Duplicate cohort name should fail (unique constraint).
- Missing required fields should show inline validation errors.

---

### Slice 5.3 — Participant management

**Preconditions**
- Cohort exists and is OPEN.
- Users exist for mentors/mentees.

**Manual actions**
1. As admin, create participants for users in a cohort with roles MENTOR/MENTEE.
2. Verify unique cohort-user constraint: attempt to add same user twice to same cohort.
3. As participant, open profile page and set display name + organization.

**Expected UI behavior**
- Profile form saves and shows confirmation message.
- Organization is required (empty org yields validation error).

**Expected DB state**
- `Participant.organization`, `display_name` updated; uniqueness enforced. :contentReference[oaicite:37]{index=37}

**Negative/edge cases**
- Participant tries to access profile for a cohort they are not part of → blocked. :contentReference[oaicite:38]{index=38}
- Organization strings with extra spaces/case: confirm consistency expectations (document whether the system normalizes orgs; if not, treat as risk).

---

### Slice 5.4 — Preference entry & normalization

**Assumptions**
- Preferences are stored as rank integers; rank normalization is computed in scoring (not necessarily stored). :contentReference[oaicite:39]{index=39}
- Preferences must be cross-role (mentor→mentee, mentee→mentor) and unique per pair. :contentReference[oaicite:40]{index=40}

**Preconditions**
- At least 2 mentors + 2 mentees in a cohort.
- Participants have organization set.

**Manual actions**
1. As a mentor, enter ranked preferences over mentees.
2. As a mentee, enter ranked preferences over mentors.
3. Create mutual rankings for Dataset A.
4. For Dataset B, omit mutuality (only one side ranks).
5. For Dataset B acceptability-infeasible, enter no preferences at all.

**Expected UI behavior**
- Ranks saved; validation prevents illegal rank values if enforced.
- Any “show blocked” toggle should clearly indicate which options are blocked (if implemented).

**Expected DB state**
- `Preference` rows created with correct from/to participants and rank. :contentReference[oaicite:41]{index=41}

**Negative/edge cases**
- Duplicate rank numbers: confirm system behavior (allow but impacts normalization?) and document result.
- Non-integer rank entry: must be rejected with clear message.
- Attempt to rank someone of same role (mentor→mentor): must be rejected at validation/DB constraint. :contentReference[oaicite:42]{index=42}

---

### Slice 5.5 — Pair scoring

**Preconditions**
- Preferences exist.
- Mentor and mentee profile fields exist (mentor slide data / mentee desired attributes), at least for Dataset C.

**Manual actions**
1. Open cohort dashboard (admin readiness dashboard) to trigger/observe score computation.
2. Inspect displayed “top pairs” table (if present).
3. Modify one participant’s preferences (e.g., swap rank order) and re-check pair scores.

**Expected UI behavior**
- Dashboard shows top pair scores and readiness widgets.
- Score changes reflect preference rank changes predictably.

**Expected DB state**
- `PairScore` rows exist for all mentor×mentee pairs or at least those needed; scores are stable and deterministic. :contentReference[oaicite:43]{index=43}

**Expected solver behavior**
- None.

**Negative/edge cases**
- Missing mentee desired attributes or missing mentor slide data should not crash scoring; score breakdown should still exist or scoring should degrade gracefully.

---

### Slice 5.6 — Strict matching execution

**Preconditions**
- Dataset A ready: equal submitted counts, orgs set, mutual cross-org acceptability exists.

**Manual actions**
1. As admin, navigate to Run Matching for the cohort.
2. Select STRICT mode and run.
3. Open results page from success redirect.

**Expected UI behavior**
- Success message: “Strict matching completed successfully!” :contentReference[oaicite:44]{index=44}
- Results table shows all matches, totals, ambiguity count, exception count (should be 0 for Dataset A). :contentReference[oaicite:45]{index=45}

**Expected DB state**
- `MatchRun` created:
  - mode=STRICT
  - status=SUCCESS
  - objective_summary populated (match_count, total_score, etc.).
- `Match` rows created for each mentor and mentee, uniqueness holds. :contentReference[oaicite:46]{index=46}

**Expected solver behavior**
- Enforces forbidden pairs (same org or not mutually acceptable) with x[i,j]=0 semantics. :contentReference[oaicite:47]{index=47}

**Expected exports**
- Export enabled (CSV default, XLSX optional). :contentReference[oaicite:48]{index=48}

**Negative/edge cases**
- Re-run strict without changing inputs: check determinism (should produce same matching unless solver ties are broken nondeterministically; if nondeterministic, log as defect/risk).

---

### Slice 5.7 — Strict failure reporting

**Preconditions**
- Dataset B strict-infeasible.

**Manual actions**
1. Run STRICT.
2. Observe failure response (should not redirect to results success view; should render run page with match_run failure details).

**Expected UI behavior**
- Error message includes failure_report message. :contentReference[oaicite:49]{index=49}
- UI provides clear next steps (at minimum: option to run exception mode if implemented per spec).

**Expected DB state**
- `MatchRun` created:
  - mode=STRICT
  - status=FAILED
  - failure_report populated with reason/diagnostics. :contentReference[oaicite:50]{index=50}

**Expected solver behavior**
- Detect infeasible and return failure without partial matches stored.

**Negative/edge cases**
- Counts mismatch (mentors ≠ mentees): strict must fail with diagnostic. :contentReference[oaicite:51]{index=51}
- Missing organizations: strict readiness should warn; strict may fail or treat as invalid input (document observed behavior).

---

### Slice 5.8 — Exception matching execution

**Preconditions**
- Dataset B or C.
- Strict run either failed or exception is explicitly selected.

**Manual actions**
1. Run EXCEPTION mode for the cohort.
2. Open results view.

**Expected UI behavior**
- Success message: “Exception matching completed successfully!”
- Results show exception_count > 0 where policy violations were required.

**Expected DB state**
- `MatchRun` created mode=EXCEPTION status=SUCCESS.
- Full set of `Match` rows created.

**Expected solver behavior**
- No forbidden pairs; all pairs allowed but penalized. :contentReference[oaicite:52]{index=52}
- Always returns a complete assignment for equal mentor/mentee counts. :contentReference[oaicite:53]{index=53}

**Negative/edge cases**
- If the cohort has zero participants or mismatched counts, exception should still fail gracefully with explicit error (exception mode “always feasible” applies only to valid N×N matching inputs).

---

### Slice 5.9 — Exception labeling correctness (E1/E2/E3)

**Preconditions**
- Dataset B and C crafted to force each exception type.

**Manual actions**
For each matched pair in EXCEPTION results:
1. Determine whether org is same.
2. Determine acceptability status:
   - mutual acceptable (both ranked each other)
   - one-sided (exactly one ranked the other)
   - neither (no ranking between them)

3. Compare to UI’s exception_flag/type/reason.

**Expected UI behavior**
- exception_flag true when any policy is broken.
- exception_type:
  - E3 if same org (highest severity)
  - else E2 if neither acceptable
  - else E1 if one-sided
  - else blank/NONE for compliant pairs :contentReference[oaicite:54]{index=54}

**Expected DB state**
- Match rows store `exception_flag`, `exception_type`, `exception_reason`. :contentReference[oaicite:55]{index=55}

**Expected solver behavior**
- Penalty ordering matches spec:
  - org violation dominates acceptability violations. :contentReference[oaicite:56]{index=56}

**Negative/edge cases**
- Combined violations (same org + neither acceptable): verify system either:
  - labels as E3 with reason including acceptability too, or
  - stores combined type (if supported).  
  The spec allows combined types but treats org as highest severity. :contentReference[oaicite:57]{index=57}

---

### Slice 5.10 — Ambiguity detection

**Preconditions**
- Dataset C with close scores among top alternatives.
- Ambiguity gap threshold default ~5 (or cohort-configured). :contentReference[oaicite:58]{index=58} :contentReference[oaicite:59]{index=59}

**Manual actions**
1. Run matching (strict or exception).
2. In results table, filter or identify ambiguity_flag=true matches.
3. Inspect ambiguity_reason for each flagged row.

**Expected UI behavior**
- ambiguity_flag true for matches where the chosen pairing score is within threshold of the best alternative for that participant (mentor or mentee). :contentReference[oaicite:60]{index=60}
- ambiguity_reason names the alternative candidate and score gap.

**Expected DB state**
- Match rows store ambiguity_flag and ambiguity_reason. :contentReference[oaicite:61]{index=61}

**Negative/edge cases**
- If only one feasible candidate exists, ambiguity should be false (no alternative).
- If threshold is adjusted, verify behavior changes accordingly.

---

### Slice 5.11 — Run history & detail views

**Assumption**
- Admin can view recent runs on run-matching page (and/or dedicated history view). Recent runs are shown. :contentReference[oaicite:62]{index=62}

**Preconditions**
- At least 2 runs exist (strict + exception; or repeated runs).

**Manual actions**
1. Navigate to run-matching page and observe recent runs list.
2. Open results pages for several runs by ID.
3. Confirm older runs remain accessible after new runs.

**Expected UI behavior**
- Runs are ordered newest-first.
- Each run’s results are immutable and consistent with the time it was generated.

**Expected DB state**
- Multiple MatchRun rows exist; matches linked correctly per run.
- No destructive updates to old runs. :contentReference[oaicite:63]{index=63}

**Negative/edge cases**
- Attempt export on failed run: UI must deny export. :contentReference[oaicite:64]{index=64}

---

### Slice 5.12 — CSV export correctness (and XLSX if enabled)

**Preconditions**
- Successful match run exists.

**Manual actions**
1. Click Export CSV on results page.
2. Save file; open locally.
3. Verify columns and row count:
   - expected columns include:
     - mentor_name/email/org
     - mentee_name/email/org
     - match_percent
     - ambiguity_flag/reason
     - exception_flag/type/reason
     - manual override fields (is_manual_override, override_reason) :contentReference[oaicite:65]{index=65} :contentReference[oaicite:66]{index=66}
4. If XLSX enabled, export XLSX and verify same columns.

**Expected UI behavior**
- Export is only available for SUCCESS runs. :contentReference[oaicite:67]{index=67}
- Correct filename includes match_run id.

**Expected DB state**
- No DB changes from exporting.

**Expected exports**
- CSV content must reflect DB matches exactly, including flags/reasons.

**Negative/edge cases**
- Export with no matches (should not happen for SUCCESS); if it occurs, treat as defect.
- CSV encoding and escaping: verify commas/newlines in reasons do not corrupt CSV structure.

---

### Slice 5.13 — Manual override workflow

**Preconditions**
- Admin access.
- Successful run exists.
- Override page accessible for a match_run. :contentReference[oaicite:68]{index=68}

**Manual actions**
1. Open override UI for the run.
2. Select a mentor and a mentee that are not currently matched together.
3. Provide an override reason.
4. Submit override.
5. Verify results table reflects the new pairing.
6. Verify uniqueness: no mentor or mentee is matched twice after override.

**Expected UI behavior**
- If the chosen pairing requires a swap, UI may present a swap suggestion/confirmation.
- On success, a confirmation message appears.
- Override should be visibly marked (manual override flag).

**Expected DB state**
- The affected `Match` row(s) updated/created with:
  - is_manual_override = true
  - override_reason populated :contentReference[oaicite:69]{index=69}
- One-to-one uniqueness constraints are preserved. :contentReference[oaicite:70]{index=70}

**Expected solver behavior**
- No solver call required for manual override; it’s a constrained edit with validation.

**Negative/edge cases**
- Submit override without selecting both mentor and mentee → inline error.
- Attempt override that would create duplicates → must be blocked with a clear validation message.
- Override that is non-strict-compliant: UI should indicate violation and require reason (per spec). :contentReference[oaicite:71]{index=71}

---

### Slice 5.14 — Readonly views vs editable views

**Preconditions**
- Both admin and participant users exist.
- At least one cohort with participants.

**Manual actions**
1. As mentor:
   - open own profile → editable
   - attempt to open another participant’s profile via URL manipulation → must not be editable/accessible
2. As mentee:
   - open desired attributes page → editable for self only
3. As admin:
   - verify read-only vs edit controls behave as expected in admin views (dashboard/results pages are typically read-only display; overrides are editable).

**Expected UI behavior**
- Participants see only their own editable forms.
- Admin sees management actions; participants never see run/export/override controls.

**Expected DB state**
- No unintended edits to other users’ data.

**Negative/edge cases**
- Try POSTing form data to another cohort_id endpoint: must be blocked.

---

### Slice 5.15 — UI consistency across modes

**Preconditions**
- At least one STRICT SUCCESS run and one EXCEPTION SUCCESS run.

**Manual actions**
1. Compare STRICT and EXCEPTION results pages:
   - same table structure
   - same columns
   - consistent meaning of match_percent, ambiguity, and exception fields
2. Export both runs; compare headers and formats.

**Expected UI behavior**
- Only differences are in:
   - mode label
   - exception fields populated in exception mode
   - failure report presence for strict failure

**Expected DB state**
- Strict matches have exception_flag=false unless manually overridden into violation (document observed behavior if overrides allow exceptions in strict runs).

---

## 6. Solver-Specific Validation

### What must NEVER happen in strict mode
1. A match where mentor.org == mentee.org. :contentReference[oaicite:72]{index=72}
2. A match where only one side ranked the other or neither did (i.e., not mutually acceptable). :contentReference[oaicite:73]{index=73}
3. Partial assignment reported as SUCCESS (must be full N matches for N mentors and N mentees).

### What must ALWAYS happen in exception mode
1. If N mentors == N mentees and inputs are otherwise valid, exception mode returns **complete one-to-one matching**. :contentReference[oaicite:74]{index=74}
2. Any policy violation must be:
   - flagged (exception_flag=true)
   - typed (E1/E2/E3)
   - explained (exception_reason contains enough detail to justify). :contentReference[oaicite:75]{index=75}

### Penalty ordering expectations
From spec:
- Org violations (E3) are the worst; solver should prefer any solution with zero org violations over any with org violations, even if scores are higher. :contentReference[oaicite:76]{index=76}
- Within org-compliant solutions:
  - avoid E2 unless required
  - avoid E1 unless required
  - within same violation profile, maximize score.

Manual verification approach:
- Construct Dataset C where there exists:
  - a zero-org-violation but lower-score solution, and
  - a higher-score solution requiring same-org.  
  Confirm solver chooses the zero-org-violation solution.

### Determinism and reproducibility checks
For each dataset:
1. Run matching twice without changes.
2. Compare:
   - match_run objective_summary totals
   - the exact mentor→mentee pairing list
3. If different:
   - capture both runs, flags, and logs
   - classify as defect unless nondeterminism is explicitly accepted (not indicated in spec; scoring is expected deterministic). :contentReference[oaicite:77]{index=77}

---

## 7. Performance & Scalability Checks

### What to measure
- End-to-end runtime from “Run matching” click to results page load.
- Solver runtime and exception counts (from logs). :contentReference[oaicite:78]{index=78}
- DB query patterns that suggest N×N explosion beyond expected O(N²).

Target bounds:
- Recommended maximum N=30. :contentReference[oaicite:79]{index=79}
- Time limits: strict ~5s, exception ~10s (as documented). :contentReference[oaicite:80]{index=80}

### How to detect N×N DB issues (manual)
- Use log timestamps and DB query monitoring if available:
  - Look for repeated per-row queries when rendering results, dashboards, or exports.
- Manual symptom checklist:
  - Results page loads slowly (seconds-to-tens of seconds) for N=30.
  - Export action stalls disproportionately.
  - Dashboard recomputation triggers excessive delay.

### Manual stress scenarios (no load tools)
1. Create N=30 mentors and N=30 mentees with dense preferences.
2. Compute scores; run strict and exception.
3. Rapidly repeat:
   - open results page
   - apply filters (ambiguity/exceptions)
   - export CSV
4. Record observed durations and any timeouts/errors.

---

## 8. Failure Mode & Resilience Testing

### Bad input
- Non-integer ranks
- Duplicate preference edges
- Missing required org fields
- Invalid CSV upload type (non-.csv) should fail validation (admin import). :contentReference[oaicite:81]{index=81}

**Expected:** user-facing validation errors, no partial writes where atomicity is expected.

### Partial data
- Some participants submitted, others not.
- Some have org set; others missing.
- Some have preferences; others missing.

**Expected:** readiness dashboard shows blockers; matching run should either fail with explicit report or run with understood behavior (document observed outcome). :contentReference[oaicite:82]{index=82}

### Timeouts
- Induce by scaling N toward 30 and using dense constraints.
- Confirm:
  - strict run fails gracefully if timeout occurs
  - exception run either completes or fails with explicit timeout report (not a crash)

### Infeasible models
- Strict infeasible scenarios must produce FAILED MatchRun and failure_report. :contentReference[oaicite:83]{index=83}

### Error reporting requirements
When any run fails:
- The UI must show:
  - mode
  - failure reason summary (from failure_report)
  - actionable hint where possible (who has zero options, org blockers). :contentReference[oaicite:84]{index=84}
- The DB must persist the failed run with failure_report.

---

## 9. Auditability & Explainability

### Manual verification that results are explainable
For a selected set of matches (at least 3 per dataset):
1. Confirm match_percent is present and plausible relative to preferences/tags/attributes.
2. Confirm for exception matches:
   - exception_reason explicitly states what policy was violated and why exception mode was used. :contentReference[oaicite:85]{index=85}
3. Confirm ambiguity matches:
   - ambiguity_reason references the alternative option and the gap threshold logic. :contentReference[oaicite:86]{index=86}

### Evidence that must exist for every match decision
For every match row:
- mentor + mentee identifiers (name/email)
- organizations
- score_percent (match_percent)
- exception_flag/type/reason fields
- ambiguity_flag/reason fields
- manual override markers when applicable (is_manual_override, override_reason). :contentReference[oaicite:87]{index=87} :contentReference[oaicite:88]{index=88}

For every match run:
- created_at, created_by, mode, status
- objective_summary (totals, counts, avg score)
- failure_report when FAILED
- input_signature (if stored) for traceability. :contentReference[oaicite:89]{index=89}

---

## 10. Regression Checklist (run before every release)

Run these checks in order (30–60 minutes baseline):
1. Auth:
   - non-admin cannot access admin dashboard/run/export/override
2. Dataset A:
   - strict SUCCESS
   - no exceptions
   - export CSV columns correct
3. Dataset B:
   - strict FAILED with visible report
   - exception SUCCESS, complete matching
   - exception labeling includes at least one E1/E2/E3 as designed
4. Dataset C:
   - ambiguity_flag triggered with sensible reason
   - penalty ordering verified in at least one constructed tradeoff case
   - manual override creates is_manual_override + override_reason and preserves one-to-one
5. Determinism:
   - re-run same mode twice yields same pairing list
6. Export integrity:
   - CSV rows count equals N matches
   - flags and reasons match the results UI

---

## 11. Tester Workflow (3 independent testers in parallel)

### Parallelization plan
Split by dataset + slice emphasis to avoid overlap:

**Tester A — Security + Core Strict Flow**
- Slices: 5.1, 5.2, 5.3, 5.6, 5.11, 5.12, 5.15
- Datasets: A (primary), B (access-control impacts), quick C sanity

**Tester B — Failure + Exception + Labeling**
- Slices: 5.7, 5.8, 5.9, 6, 8
- Datasets: B (primary), C (penalty ordering), A (baseline)

**Tester C — Ambiguity + Override + Auditability**
- Slices: 5.10, 5.13, 9, 7 (performance sampling)
- Datasets: C (primary), A (override in normal), B (override after exception)

**Tester D — Participant UX + CSV Import + UI Non-Functional**
- Focus: Participant user experience, CSV import workflow, UI non-functional qualities
- Goals: Verify full non-admin experience and admin import workflow with Playwright assertions and Postgres validation
- Coverage: Registration/login, profile pages, preferences UI, "my match" page, CSV import, accessibility, cross-browser, responsiveness

**Tester E — Scale + Combinatorial Edge Cases**
- Focus: Very large cohorts, extreme preference patterns, degenerate/adversarial datasets, partial submissions across many cohorts
- Goals: Validate system correctness and UI stability under stress with Playwright MCP UI flows and Postgres MCP assertions
- Coverage: N≤30 cohorts, contention scenarios, sparse preferences, degenerate ranks, multi-cohort partial submissions, performance sampling

### Artifacts each tester must produce
Each tester provides:
1. A short run log with:
   - dataset used
   - match_run IDs tested
   - pass/fail per slice
2. Evidence bundle:
   - screenshots of key UI states (login block, results flags, failure report, override confirmation)
   - exported files (CSV/XLSX) for at least one run
   - captured relevant app logs around each match run
3. DB verification notes:
   - for each tested run: mode/status + one match row sample including flags/reasons fields

### Defect reporting format (required)
For each defect:
- Title: `[Slice] [Dataset] Symptom`
- Steps to reproduce: exact sequence
- Observed vs expected
- Evidence: screenshots/log excerpt + DB snapshot description
- Severity:
  - Critical: access-control bypass, strict constraint violation, data corruption, missing matches on SUCCESS
  - High: incorrect exception labeling, incorrect exports, non-determinism without explanation
  - Medium/Low: UI inconsistencies, minor validation gaps

---
End of plan.
