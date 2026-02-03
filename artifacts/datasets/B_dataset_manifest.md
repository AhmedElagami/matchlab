# Dataset Manifest (Tester B)

- tester: B
- dataset names:
  - Dataset B: Test Cohort 5x5 Not Ready (fixture: `fixtures/cohort_5x5_not_ready.json`)
  - Dataset A (baseline substitute): Test Cohort 5x5 Ready (fixture: `fixtures/cohort_5x5_ready.json`)
  - Dataset C (penalty ordering): manual modifications via Django admin on top of Dataset B/A

## Seed commands
1. Create admin user (if missing):
   `docker compose -f docker-compose.dev.yml exec app python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@example.com','admin123'); print('admin_ready', User.objects.filter(username='admin').exists())"`
2. Load Dataset B fixture:
   `docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_5x5_not_ready.json`
3. Load Dataset A fixture:
   `docker compose -f docker-compose.dev.yml exec app python manage.py loaddata fixtures/cohort_5x5_ready.json`

## Fixture files + paths
- `fixtures/cohort_5x5_not_ready.json`
- `fixtures/cohort_5x5_ready.json`

## Entity counts (post-seed, before additional cohorts)
- cohorts: 2
- participants: 20
- preferences: 52
- users: 21 (includes admin)

## Assumptions / preconditions
- Docker services running via `docker compose -f docker-compose.dev.yml up -d`.
- Dataset C scenarios are created by manual admin edits (org changes and preference tweaks) after seeding.
- Cohort 3 modified via Django admin: set participant "Mentee TwentyFive" (id=30) to `is_submitted=true` with submitted_at set to current time.
- Cohort 3 added one-sided preferences: mentor22->mentee22, mentor23->mentee23, mentor24->mentee24, mentor25->mentee25 (rank 1) to force E1 cases.
- Cohort 3 org edits for E3: mentee21/22/23/24 org changed to OrgA (all mentees now OrgA).
- Baseline dataset referenced as cohort 2 ("Test Cohort 5x5 Ready"); documentation references "Cohort 1" which is not present in fixtures.

## Additional test cohorts created manually
- Cohort 4: Empty Cohort 0x0 B 15f200 (no participants) for zero-participant exception failure validation.
- Cohort 5: Penalty Ordering 2x2 B 15f200 (2 mentors, 2 mentees, all submitted) with manual PairScore values to force cross-org selection despite higher same-org score.
- Cohort 6: Input Validation 1x2 B bb0705 (1 mentor, 2 mentees, not submitted) for preference input validation tests.
- Associated users created with password `test123` for these cohorts.
