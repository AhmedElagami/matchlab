# 10 — Results & Overrides

## Match results

After a successful matching run, results are displayed at `/match-run/<id>/results/`.

### What's shown

Each match row includes:

| Column | Source |
|--------|--------|
| Mentor name | `match.mentor.display_name` |
| Mentee name | `match.mentee.display_name` |
| Match % | `match.score_percent` (0–100) |
| Ambiguity flag | ⚠️ if `match.ambiguity_flag == True` |
| Ambiguity reason | Score gap explanation |
| Exception flag | 🚩 if `match.exception_flag == True` |
| Exception type | `E1`, `E2`, or `E3` |
| Exception reason | Human-readable explanation |
| Manual override | ✋ if `match.is_manual_override == True` |
| Override reason | Admin-provided justification |

### Summary stats

The results page also shows:
- Total matches
- Ambiguous matches count
- Exception matches count

### Objective summary (stored in MatchRun)

```json
{
    "total_score": 285.0,
    "avg_score": 57.0,
    "match_count": 5,
    "ambiguity_count": 1,
    "solve_time": 0.02,
    "total_duration": 0.15,
    "exception_count": 2,
    "exception_summary": {"E1": 1, "E2": 1, "E3": 0}
}
```

## Match run history

All runs are persisted and never deleted. The run matching page (`/cohort/<id>/run-matching/`) shows the 10 most recent runs with mode, status, and timestamp.

Each `MatchRun` stores:
- `input_signature`: SHA-256 hash of all inputs at run time, for traceability.
- `failure_report`: diagnostics JSON when status is FAILED.

## Manual overrides

### When to use

Admin uses overrides to manually reassign pairs after reviewing results. Common reasons:
- Business relationship that the algorithm can't account for.
- Participant request.
- Correcting a known data issue.

### How it works

1. Admin navigates to `/match-run/<id>/override/`.
2. Selects a mentor and mentee from dropdowns (only submitted participants shown).
3. System validates:
   - Both are in the same cohort.
   - Mentor has role `MENTOR`, mentee has role `MENTEE`.
   - Both have submitted preferences.
4. System checks if the new pair creates an exception:
   - Runs `classify_exception()` against current data.
   - If it's an exception, override reason is **required**.
5. System checks for swap implications:
   - `get_swap_suggestion()` finds existing matches for both participants.
   - If both are already matched to different people, shows a swap suggestion.
   - Admin must confirm before proceeding.
6. On confirmation:
   - Existing matches for both the mentor and mentee are deleted.
   - A new `Match` is created with `is_manual_override=True`.
   - `score_percent` is set to 0 (manual overrides don't have computed scores).
   - Exception flags are set based on the classification.

### Override validation rules

| Check | Error message |
|-------|--------------|
| Different cohorts | "Both participants must be in the same cohort" |
| Wrong role | "First participant must be a mentor" / "Second participant must be a mentee" |
| Not submitted | "Both participants must have submitted their preferences" |
| Exception without reason | "Override reason is required when creating an exception match" |

### Audit trail

Every override is permanently recorded:
- `Match.is_manual_override = True`
- `Match.override_reason` contains the admin's justification.
- The original matches are deleted from the run, but the `MatchRun` itself is preserved.

## Active match run

### Purpose

The "active" run is the official result that participants see. Only one run can be active per cohort at a time.

### Setting active

1. Admin clicks "Set as Active" on a results page.
2. POST to `/cohort/<id>/match-run/<id>/set-active/`.
3. `override.set_active_match_run()` creates or updates the `ActiveMatchRun` record.
4. Only runs with `status == "SUCCESS"` can be set as active.

### Participant view

Once an active run is set, participants can view their match at `/cohort/<id>/my-match/`.

`get_active_match_for_participant()`:
1. Looks up `ActiveMatchRun` for the participant's cohort.
2. Queries the `Match` in that run where the participant is either mentor or mentee.
3. Returns the match or `None` if no active run exists.

### Changing the active run

Setting a new active run replaces the previous one (via `update_or_create`). The previous run's data is not affected — only the pointer changes.
