# DB Assertions (Tester B)

## Step 1: Post-wipe verification
- Query file: `artifacts/db/B/queries.sql`
- Result file: `artifacts/db/B/results/step1_db_counts.txt`
- Result summary: 0 match_runs, 0 matches, 0 cohorts after full wipe + migrations.

## Step 2: Post-seed verification
- Result file: `artifacts/db/B/results/seed_counts.txt`
- Result summary: 2 cohorts, 20 participants, 52 preferences, 21 users (includes admin).

## Step 3: MatchRun after strict/exception attempt (cohort 3)
- Result file: `artifacts/db/B/results/matchrun_latest_after_fail.txt`
- Result summary: latest MatchRun mode=EXCEPTION, status=FAILED, failure_report COUNT_MISMATCH.

## Step 4: MatchRun 6 (cohort 3 exception success)
- Result file: `artifacts/db/B/results/matchrun_6_summary.txt`
- Result summary: mode=EXCEPTION, status=SUCCESS, 5 matches, exception_summary E2=4, E1/E3=0.

## Step 5: MatchRun 8 (cohort 3 exception E1 scenario)
- Result file: `artifacts/db/B/results/matchrun_8_summary.txt`
- Result summary: mode=EXCEPTION, status=SUCCESS, exception_summary E1=4, E2/E3=0; exception_reason indicates "Mentor did not rank mentee" for one-sided preferences.

## Step 6: MatchRun 10 (cohort 3 exception E3 scenario)
- Result file: `artifacts/db/B/results/matchrun_10_summary.txt`
- Result summary: mode=EXCEPTION, status=SUCCESS, exception_summary E3=1, E1=4, E2=0; one same-org match present.

## Step 7: MatchRun 11 (cohort 2 strict success constraints)
- Result file: `artifacts/db/B/results/matchrun_11_strict_checks.txt`
- Result summary: STRICT success, same_org_matches=0, non_mutual_matches=0.

## Step 8: Exception determinism (cohort 2)
- Result file: `artifacts/db/B/results/exception_determinism_cohort2.txt`
- Result summary: last two exception runs (13,12) have identical mentor/mentee pairs.

## Step 9: Empty cohort exception failure (cohort 4)
- Result file: `artifacts/db/B/results/empty_cohort_run_summary.txt`
- Result summary: EXCEPTION run failed with failure_report reason=NO_PARTICIPANTS.

## Step 10: Penalty ordering scenario (cohort 5)
- Result file: `artifacts/db/B/results/penalty_ordering_run15_summary.txt`
- Result summary: EXCEPTION run SUCCESS with cross-org matches selected despite higher same-org score alternatives (score_percent=10 each).

## Step 11: Timeout settings
- Result file: `artifacts/db/B/results/timeout_settings.txt`
- Result summary: strict_time_limit=5s, exception_time_limit=10s from config defaults.
