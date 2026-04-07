
## Technical Specification: Mentor–Mentee Matchmaker (Django + Postgres + Google OR-Tools)

### 0. Scope and goals

Build a self-hosted internal web application to match mentors and mentees in cohorts.

Hard business intent:

* Prefer **policy-compliant one-to-one matches**.
* If a fully compliant solution is impossible, still produce a **complete one-to-one pairing** using **policy exceptions**, clearly flagged and explained, plus a guided fix loop to reach compliance.

Key constraints:

* Cohort size: 10–30 mentors and 10–30 mentees.
* One-to-one pairing.
* Hard constraint normally: **mentor.org != mentee.org**.
* “No one can be angry”: by default, **both must mark each other acceptable**.
* New stakeholder inputs: mentor slide data, mentee desired mentor attributes, match percentage, ambiguity indication.
* Performance: produce results within 30 seconds.
* Output: export to commonly used format (CSV required; XLSX optional).
* Non-expert usability.

Recommended stack:

* **Django** (server-rendered UI + Django Admin)
* **Postgres**
* **Google OR-Tools (CP-SAT)** for constrained assignment + fallback exceptions

---

## 1. Roles, permissions, and access control

### Roles

* **Admin**: manage cohorts, users, imports, run matching, override matches, export.
* **Mentor**: view/edit profile, organization, intro data, preferences; submit/lock.
* **Mentee**: view/edit profile, organization, desired mentor attributes, preferences; submit/lock.

### Permissions rules

* Mentors/mentees can edit only their own data.
* Admin can view/edit all cohort data.
* Only Admin can:

  * trigger matching runs
  * accept/commit a run as “active”
  * export results
  * perform manual overrides
  * upload CSV imports

---

## 2. Data inputs and domain rules

### Inputs considered

1. Preference list of talents (mentees): ranked acceptable mentors
2. Preference list of mentors: ranked acceptable mentees
3. Data from mentors’ introductory slides (structured fields; imported CSV or manual entry)
4. Important attributes of the desired mentor written by talents (structured checkboxes + tags + free text)
5. Sender organization of talents (mentees)
6. Organization of mentors

### Hard constraints (strict mode)

* One-to-one: each mentor matched to exactly one mentee; each mentee matched to exactly one mentor.
* Org constraint: `mentor.org != mentee.org`
* Mutual acceptability: both sides list each other as acceptable.

### Soft acceptability fallback (exception mode)

If strict mode has no feasible solution:

* Still produce a full one-to-one matching using exceptions.
* Exceptions are allowed in a controlled priority order:

  * E1: allow **one-sided acceptability** (one side accepts, other doesn’t)
  * E2: allow **mutual unacceptability** only if needed
  * E3: allow **same-organization matches** only if needed (last resort)
* Every exception must be:

  * flagged per pair
  * explained (which policy was broken)
  * counted in the run summary

Important: This satisfies the operational requirement “always produce a match table”, while clearly distinguishing compliant vs exception-based outcomes.

---

## 3. UX workflows

### 3.1 Mentor workflow

* Register/login.
* Select cohort (if applicable).
* Set organization (required).
* Fill mentor intro data (slide fields) OR admin imports it.
* Define ranked list of acceptable mentees (excluding same-org shown as blocked).
* Submit/lock preferences.

### 3.2 Mentee workflow

* Register/login.
* Select cohort.
* Set organization (required).
* Fill “desired mentor attributes” (checkboxes/tags/free text).
* Define ranked list of acceptable mentors (excluding same-org shown as blocked).
* Submit/lock.

### 3.3 Admin workflow

* Create cohort.
* Add/import users; assign cohort roles.
* Import mentor slide data CSV (optional).
* Monitor readiness dashboard:

  * counts submitted
  * org distribution
  * option counts after filtering
* Run matching:

  * Strict attempt; if impossible, show diagnostics and offer “Run with exceptions”.
  * Exception run produces complete matching with flagged exceptions.
* Review results:

  * match table includes match %, ambiguity flags, exception flags, explanations
* Commit a run as active.
* Export CSV/XLSX.
* Manual override with validation (and exception flags if admin forces).

---

## 4. Data model (Postgres)

### 4.1 Core tables

**users**

* id (uuid or bigserial)
* email (unique)
* password_hash (or external auth later)
* is_active (bool)
* created_at, last_login

**cohorts**

* id
* name
* status: DRAFT | OPEN | CLOSED | MATCHED
* created_at

**participants**

* id
* cohort_id (FK cohorts)
* user_id (FK users)
* role_in_cohort: MENTOR | MENTEE
* display_name
* organization (string; optionally FK organizations)
* is_submitted (bool)
* submitted_at (timestamp nullable)
* created_at, updated_at
* unique (cohort_id, user_id)
* index (cohort_id, role_in_cohort)

**preferences**

* id
* cohort_id
* from_participant_id (FK participants)
* to_participant_id (FK participants)
* rank (int, 1..N)
* created_at
* unique (cohort_id, from_participant_id, to_participant_id)
* constraint: from.role != to.role

### 4.2 Mentor slide data

**mentor_profiles**

* participant_id (FK participants, unique; role must be MENTOR)
* job_title (text)
* function (text)
* expertise_tags (text)  // comma-separated normalized on write
* languages (text)
* location (text)
* years_experience (int nullable)
* coaching_topics (text)
* bio (text)
* slide_source: MANUAL | CSV_IMPORT
* updated_at

### 4.3 Mentee desired mentor attributes

**mentee_profiles**

* participant_id (FK participants, unique; role must be MENTEE)
* desired_tags (text)
* desired_attributes (jsonb)
* free_text_notes (text)
* updated_at

### 4.4 Scoring transparency (optional but recommended)

**pair_scores**

* id
* cohort_id
* mentor_participant_id (FK participants)
* mentee_participant_id (FK participants)
* score_percent (int 0..100)
* breakdown (jsonb)
* computed_at
* unique (cohort_id, mentor_participant_id, mentee_participant_id)

### 4.5 Matching run history and results

**match_runs**

* id
* cohort_id
* created_by_user_id (FK users)
* created_at
* mode: STRICT | EXCEPTION
* status: SUCCESS | FAILED
* objective_summary (jsonb)  // totals, exception counts, total score
* failure_report (jsonb)
* input_signature (text) // hash of relevant input for traceability

**matches**

* id
* match_run_id (FK match_runs)
* mentor_participant_id (FK participants)
* mentee_participant_id (FK participants)
* score_percent (int 0..100)
* ambiguity_flag (bool)
* ambiguity_reason (text or jsonb)
* exception_flag (bool)
* exception_type (text) // NONE, E1, E2, E3, or combined
* exception_reason (text or jsonb)
* is_manual_override (bool)
* override_reason (text)
* unique (match_run_id, mentor_participant_id)
* unique (match_run_id, mentee_participant_id)

**active_match_runs**

* cohort_id (FK cohorts, unique)
* match_run_id (FK match_runs)
* set_by_user_id
* set_at

### 4.6 Import jobs (mentor slides CSV)

**import_jobs**

* id
* cohort_id
* type: MENTOR_SLIDES_CSV
* uploaded_by_user_id
* uploaded_at
* status: PENDING | SUCCESS | FAILED
* error_report (jsonb)

---

## 5. Readiness checks and feasibility validation

### 5.1 Readiness criteria (STRICT readiness)

A cohort is “Ready (Strict)” if:

* #submitted mentors == #submitted mentees == N
* Every submitted participant has organization set
* Every submitted participant has preference list submitted
* For every mentor i: count of mutually acceptable cross-org mentees >= MIN_OPTIONS
* For every mentee j: count of mutually acceptable cross-org mentors >= MIN_OPTIONS
* Optional: org distribution sanity checks (informational)

Config:

* `MIN_OPTIONS_STRICT` default 3 (tunable)
* If someone has fewer than MIN_OPTIONS_STRICT: show as blocker but allow admin to proceed.

### 5.2 Exception readiness

If strict fails, show:

* who has zero strict options
* how many options exist if relaxing acceptability but keeping org constraint
* how many options exist if relaxing org constraint
  This guides fixes.

### 5.3 Fix loop UX

Admin dashboard includes:

* list of blockers (e.g., “Mentee X has 0 mutually acceptable cross-org mentors”)
* suggested actions:

  * request more preferences from X
  * request mentors to broaden acceptability
  * correct organizations spelling
  * ensure both sides submitted

---

## 6. Match scoring and “match percentage”

### 6.1 Score definition

Each potential pair (mentor i, mentee j) gets `score_percent` (0–100) based on:

* Preference ranks (if present) from both sides
* Tag overlap between mentee desired tags and mentor expertise/coaching topics
* Desired attributes satisfaction (checkboxes)
* Optional: function alignment, language, location

The score must be:

* explainable (store a breakdown)
* deterministic

### 6.2 Default scoring model (configurable weights)

Weights (sum to 100):

* 40: mutual preference rank component
* 30: tag overlap component
* 20: desired attributes component
* 10: language/location/function alignment component

Definitions:

* Rank normalization:

  * If ranked list length = K and partner rank = r (1..K),
  * `rank_score = 1 - (r-1)/max(K-1,1)` in [0,1]
* Mutual rank component:

  * `mutual_rank_score = 0.5*mentor_rank_score + 0.5*mentee_rank_score`
* Tag overlap:

  * Jaccard similarity between normalized tag sets
* Desired attributes:

  * Each boolean requirement satisfied contributes equal share of that 20 points (or weighted by config)
* Language/location/function:

  * simple matching rules from config

Final:

* `score_percent = round( 40*mutual_rank + 30*tag + 20*attr + 10*align )`

Store breakdown:

* rank details, tags matched, attribute satisfaction, etc.

---

## 7. Ambiguity detection

Ambiguity is a reporting feature for admin review.

Rule A (per mentee):

* Let top two scores among feasible candidates be s1 and s2.
* If `(s1 - s2) <= AMBIGUITY_GAP` (default 5), mark the chosen match as ambiguous for that mentee:

  * explanation includes the alternative candidate and scores.

Rule B (per mentor): same.

Store:

* `ambiguity_flag = true`
* `ambiguity_reason` includes top alternative(s)

---

## 8. Matching engine: Google OR-Tools CP-SAT

### 8.1 Decision variables

For N mentors and N mentees (after submission filtering and ensuring equal counts):

* `x[i,j] ∈ {0,1}` for i in mentors, j in mentees

### 8.2 Core constraints (always enforced in both modes)

* Each mentor matched exactly once:

  * ∑_j x[i,j] = 1 for all i
* Each mentee matched exactly once:

  * ∑_i x[i,j] = 1 for all j

### 8.3 Strict mode constraints

For forbidden pairs set x[i,j] = 0 if any:

* same org
* not mutually acceptable (missing preference on either side)

Objective (maximize total score):

* maximize ∑_{i,j} x[i,j] * score[i,j]

If infeasible: strict run fails with diagnostics.

### 8.4 Exception mode constraints and penalties

In exception mode, **no pairs are forbidden**, but policy violations carry large penalties to ensure the solver only uses them if needed.

Define for each pair:

* `viol_org[i,j]` = 1 if same org else 0
* `viol_mutual[i,j]` categories:

  * 0 if mutually acceptable
  * 1 if one-sided acceptable
  * 2 if neither acceptable

Define penalty points:

* `P_org` (very large; default 1,000,000)
* `P_one_sided` (large; default 100,000)
* `P_neither` (larger; default 300,000)

Objective:

* maximize:

  * ∑ x[i,j] * (score[i,j] * SCORE_SCALE)  -  ∑ x[i,j] * penalty(i,j)
    Where:
* `SCORE_SCALE` (e.g., 1000) to keep integers and ensure score differences matter after penalties only within same violation tier.

Penalty(i,j):

* `viol_org * P_org + one_sided * P_one_sided + neither * P_neither`
  (one_sided = 1 when exactly one accepts; neither = 1 when none accept)

Interpretation:

* The solver will prefer:

  1. any solution with zero org violations over any with org violations
  2. within org-compliant solutions, prefer mutual acceptability; only use one-sided if required
  3. avoid “neither accepts” unless absolutely required
  4. within the same violation profile, maximize score

### 8.5 Exception labeling

After solving exception mode, each matched pair gets:

* exception_flag true if any violation occurred
* exception_type:

  * E1 if one-sided acceptability
  * E2 if neither acceptable
  * E3 if same org (can be combined, but treat org as highest severity)
* exception_reason: include acceptability status, org info, and why it was needed:

  * minimal explanation: “Strict mode infeasible; exception mode used. This pair violates: …”

### 8.6 Solver time limit

Set CP-SAT time limit:

* 5 seconds strict
* 10 seconds exception
  This is comfortably within 30 seconds end-to-end at N≤30.

---

## 9. Diagnostics (strict failure reporting)

When strict mode is infeasible, generate a clear failure_report JSON including:

### 9.1 Basic blockers

* counts: mentors submitted, mentees submitted
* list participants missing org
* list participants not submitted preferences

### 9.2 Option counts after filtering

Compute for each mentor:

* mutually acceptable cross-org candidate count
  Compute for each mentee:
* mutually acceptable cross-org candidate count
  Include:
* zero-option participants
* lowest 5 option counts on each side

### 9.3 Org distribution report

* counts of mentors per org
* counts of mentees per org
* highlight orgs with high imbalance (informational)

### 9.4 Suggested actions

Rules:

* If zero mutually acceptable: recommend expanding preference lists on both sides
* If org constraint is primary blocker: recommend ensuring cross-org acceptability or adjusting cohort composition

---

## 10. Manual override rules

Admin can override matches in an active run:

* Must maintain one-to-one uniqueness within that run.
* Must run validation and show:

  * whether the override is strict-compliant
  * if not, mark as exception and require override_reason

Override UI should show:

* current pair score and violations
* proposed pair score and violations

Overrides are stored as changes to matches within a match_run (is_manual_override true).

---

## 11. Export formats

Required:

* CSV: columns:

  * cohort
  * mentor_name, mentor_email, mentor_org
  * mentee_name, mentee_email, mentee_org
  * match_percent
  * ambiguity_flag, ambiguity_reason
  * exception_flag, exception_type, exception_reason
  * manual_override_flag, override_reason

Optional:

* XLSX with same columns.

---

## 12. UI screens (minimal Django server-rendered)

### 12.1 Shared

* Login/Logout
* Cohort selector (if user in multiple cohorts)

### 12.2 Mentor

* Profile: org, display name
* Mentor Intro Data form (fields in mentor_profiles)
* Preferences editor:

  * list of mentees (filtered to other orgs by default, with “show blocked” toggle)
  * ranked ordering UI (simple numeric rank inputs acceptable)
* Submit/lock page

### 12.3 Mentee

* Profile: org, display name
* Desired mentor attributes form:

  * desired_tags (tag input)
  * checkbox attributes
  * free text notes
* Preferences editor (rank mentors)
* Submit/lock

### 12.4 Admin

* Cohort dashboard:

  * submission counts
  * readiness status (strict-ready / exception-only)
  * top blockers
* Import mentor slide CSV:

  * upload
  * preview errors
* Run matching:

  * button “Run strict”
  * if strict fails, show report + button “Run with exceptions”
  * results table
* Match run history:

  * list runs, open details
* Commit run as active
* Manual override page
* Export page

---

## 13. APIs / endpoints (Django views)

Minimal server-rendered endpoints (examples):

* `/cohort/<id>/mentor/profile`
* `/cohort/<id>/mentor/preferences`
* `/cohort/<id>/mentee/profile`
* `/cohort/<id>/mentee/preferences`
* `/admin/cohort/<id>/dashboard`
* `/admin/cohort/<id>/import/mentor-slides`
* `/admin/cohort/<id>/run-matching?mode=strict|exception`
* `/admin/match-runs/<id>`
* `/admin/match-runs/<id>/export.csv`
* `/admin/match-runs/<id>/set-active`
* `/admin/match-runs/<id>/override`

---

## 14. Matching run pseudocode (strict + exception)

```text
function run_match(cohort_id, mode, admin_user_id):

  participants = load submitted mentors/mentees
  if counts mismatch -> create match_run FAILED with report; return

  build preferences maps:
    mentor_accepts[i][j] = true if mentor ranked mentee
    mentee_accepts[j][i] = true if mentee ranked mentor

  build score[i][j] for all i,j (0..100) using scoring model
  persist pair_scores (optional) or compute on fly

  if mode == STRICT:
    allowed[i][j] = (org_diff AND mentor_accepts AND mentee_accepts)
    readiness/diagnostics: option counts
    build CP-SAT:
      x[i,j] bool
      sum_j x[i,j] = 1; sum_i x[i,j] = 1
      for forbidden pairs: x[i,j] = 0 where not allowed
      maximize sum x[i,j] * score[i][j]*SCALE
    solve with timelimit
    if infeasible:
      create match_run FAILED with diagnostics
      return
    else:
      extract solution; compute ambiguity; store matches (exception_flag=false)

  if mode == EXCEPTION:
    build CP-SAT:
      x[i,j] bool
      assignment constraints
      penalty(i,j) computed from org + acceptability status
      maximize sum x*(score*SCALE - penalty)
    solve
    always feasible (complete bipartite assignment)
    extract solution
    compute exception flags/types per match
    compute ambiguity
    store matches

  store match_run SUCCESS summary:
    total_score, avg_score
    exception_counts by type
    ambiguity_count
```

---

## 15. CSV import specification (mentor slides)

### Template

File: `mentor_slide_data_<cohort>.csv`

Required columns:

* `mentor_email`
* `organization`

Optional columns:

* `job_title,function,expertise_tags,languages,location,years_experience,coaching_topics,bio,availability_notes`

Import behavior:

* match row to mentor participant by email in the cohort
* validate organization non-empty
* normalize tags fields by splitting on comma/semicolon, trimming, lowercasing
* store into mentor_profiles; set slide_source=CSV_IMPORT
* produce preview:

  * accepted rows
  * rejected rows with error messages

---

## 16. Deployment plan (Docker Compose)

Services:

* `db`: postgres:16 (volume)
* `app`: Django + gunicorn

Environment variables:

* `DATABASE_URL`
* `DJANGO_SECRET_KEY`
* `DJANGO_ALLOWED_HOSTS`
* `DJANGO_DEBUG=false`
* optional: `CSRF_TRUSTED_ORIGINS`

Operations:

* `docker compose up -d`
* `docker compose exec app python manage.py migrate`
* `docker compose exec app python manage.py createsuperuser`

---

## 17. Testing plan (must-have tests)

### Unit tests

* Score computation:

  * rank scoring boundaries
  * tag overlap cases
  * attribute scoring
* Acceptability logic:

  * mutual, one-sided, neither classification
* Org constraint enforcement (strict)

### Solver tests

* Strict feasible small case: returns no exceptions, perfect one-to-one
* Strict infeasible due to org constraint: strict fails, exception succeeds with E3
* Strict infeasible due to acceptability: strict fails, exception succeeds with E1/E2 as needed
* Ensure exception objective prioritization:

  * if any strict-compliant solution exists, exception mode should also return zero violations (sanity check)

### Integration tests

* Readiness dashboard shows correct blockers
* CSV import validation and error report
* Match run creation and history
* Export CSV contains correct fields and flags
* Manual override validation: one-to-one maintained and flags set correctly

### Performance test

* N=30 with dense preferences: strict solve under time limit; end-to-end under 30 seconds.

---

## 18. Configuration knobs (admin-configurable)

* `MIN_OPTIONS_STRICT` default 3
* `AMBIGUITY_GAP` default 5
* Exception penalties:

  * `P_org`, `P_one_sided`, `P_neither`
* Scoring weights and mapping rules

Store config per cohort in JSON (optional) or global settings.

---

## 19. Implementation notes (to keep minimal)

* Use Django Admin for most data management; add custom admin views for:

  * Cohort dashboard readiness
  * Run matching
  * Import CSV preview
  * Export
* Use integer scores/penalties for CP-SAT.
* Keep exception mode available only to Admin and clearly labeled in UI.
* Always store MatchRun + failure_report/summary for auditability.

---

### Acceptance criteria (what “done” means)

1. Admin can run strict matching; if feasible, produces a complete one-to-one matching with 0 exceptions.
2. If strict is infeasible, system produces a clear failure report and admin can run exception mode to get a complete one-to-one matching with per-pair exception flags and explanations.
3. Results show match percent and ambiguity indicators.
4. CSV export works.
5. End-to-end runtime under 30 seconds for N<=30.
