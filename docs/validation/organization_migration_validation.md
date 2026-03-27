# Manual Validation Script — Organization Field Migration

## Prerequisites
```bash
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
docker compose -f docker-compose.dev.yml exec web python manage.py loaddata fixtures/cohort_3x3.json
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser --username admin --email admin@example.com
```

---

## 1. Django Admin — Organization CRUD

1. Go to **http://localhost:8000/admin/**
2. Log in as `admin`
3. Verify **Organizations** appears in the admin sidebar under CORE
4. Click **Organizations** → confirm 3 orgs loaded from fixture: Cloud & Edge Solutions, Mobile Networks, Network Infrastructure
5. Click **Add Organization** → enter "Test Org" → Save
6. Verify it appears in the list sorted alphabetically
7. Try adding a duplicate name → confirm unique constraint error
8. Delete "Test Org"

**Pass criteria:** CRUD works, unique constraint enforced, alphabetical ordering.

---

## 2. Django Admin — Participant Organization Display

1. Go to **Admin → Participants**
2. Verify the **Organization** column shows org names (not IDs)
3. Use the search box → type "Cloud" → confirm participants from "Cloud & Edge Solutions" appear
4. Click a participant → verify organization shows as a dropdown with all organizations

**Pass criteria:** Org names display correctly, search by org name works, dropdown in edit form.

---

## 3. Participant Profile Form — Dropdown

1. Log in as a participant user (e.g., `mentor1`)
2. Go to the profile edit page
3. Verify **Organization** is a `<select>` dropdown (not a text input)
4. Verify all admin-created organizations appear as options
5. Select an organization → Save → confirm it persists
6. Try submitting with no organization selected → confirm validation error "Organization is required."

**Pass criteria:** Dropdown renders, options match admin-managed list, validation works.

---

## 4. Matching — Same-Org Constraint

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py loaddata fixtures/cohort_3x3.json
```

1. Go to **Admin → Run Matching** for the 3x3 cohort
2. Run **Strict mode**
3. Verify no same-org pairs are matched (Balázs/Kenji both Network Infrastructure, Erik/Eszter both Cloud & Edge, Priya/Astrid both Mobile Networks — none should be paired together)

**Pass criteria:** Same-org prohibition still works with FK comparison.

---

## 5. Exception Mode — E3 Classification

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py loaddata fixtures/manual_exception_e3.json
```

1. Run **Exception mode** for this cohort
2. Verify same-org matches are flagged as **E3** exceptions
3. Verify the exception reason shows the organization name (e.g., "Same organization: Mobile Networks"), not an ID or object repr

**Pass criteria:** E3 exceptions display org name correctly.

---

## 6. Readiness Dashboard

1. Load the 5x5_not_ready fixture
2. Go to the cohort readiness/dashboard page
3. Verify **Organization Distribution** shows org names with correct mentor/mentee counts
4. Verify **Zero Option Participants** shows org names (not IDs or object reprs)

**Pass criteria:** Org names render correctly in all readiness views.

---

## 7. CSV/XLSX Export

1. After a successful match run, export as CSV
2. Verify `mentor_org` and `mentee_org` columns contain org names (not IDs)
3. Export as XLSX → verify same

**Pass criteria:** Export contains human-readable org names.

---

## 8. Template Rendering Spot-Check

Visit these pages and confirm organization displays as a name string:
- Preferences page (candidate list shows org)
- Candidate profile modal
- Match results page (admin)
- My Match page (participant)
- Override page (admin)

**Pass criteria:** No `Organization object (N)` or raw IDs visible anywhere.

---

## 9. PROTECT Constraint

1. In admin, try to delete an Organization that has participants assigned
2. Confirm Django prevents deletion with a ProtectedError

**Pass criteria:** Cannot delete an org that's in use.
