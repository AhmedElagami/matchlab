# Organization Field Migration Study

**Date:** 2026-02-27  
**Author:** AI Agent (opencode)  
**Goal:** Investigate current organization field usage and plan migration to fixed list managed via Django admin dashboard.

## 1. Current State Analysis

### 1.1. Data Model
- `Participant.organization` is a `CharField(max_length=200, blank=True)`.
- No separate `Organization` model exists.
- Organization values are free‑form text entered by participants during profile editing.

### 1.2. UI & Forms
- **Participant profile form** (`ParticipantProfileForm` in `core/forms.py`):
  - Uses a plain text input (`TextInput`) with `data‑testid="organization‑input"`.
  - Validation: field is required (raises `ValidationError` if empty).
- **Admin interface** (`ParticipantAdmin`):
  - Lists `organization` as a column and includes it in search fields.
  - No dedicated management UI for organization values.

### 1.3. Business Logic & Constraints
- **Strict matching** (`solvers/strict.py`):
  - A pair is **infeasible** if both participants have the same organization string.
  - Comparison: `mentor.organization == mentee.organization`.
- **Exception classification** (`domain.py`):
  - Same organization → **E3** (highest severity penalty).
  - Organization name retrieved via `participant_orgs` lookup.
- **Readiness checks** (`readiness.py`):
  - Detects participants with empty organization strings.
  - Generates organization distribution summary (counts by organization string).
- **Data preparation** (`data_prep.py`):
  - `_build_same_org_matrix` compares strings.
  - `_build_participant_orgs` creates a lookup `{participant_id: organization_string}`.
- **CSV import/export**:
  - Export includes organization as a column (string).
  - Import logic (if implemented) presumably expects a free‑text column.

### 1.4. Existing Data
- Migration `core/migrations/0001_initial.py` created the field with `blank=True`.
- Existing fixtures (e.g., `fixtures/cohort_3x3.json`) contain organization strings like `"Org A"`, `"Org B"`.
- No referential integrity; duplicate strings represent the same organization.

## 2. Requirements

From the issue description:
1. **Admin‑managed fixed list**: Admins should be able to define a fixed list of organizations via the Django admin dashboard.
2. **Participant selection**: Participants must choose from that list (dropdown) instead of typing free‑form text.
3. **Backward compatibility**: Existing data must be migrated gracefully.
4. **All existing constraints** (same‑org prohibition, E3 penalty, readiness checks, distribution summaries) must continue to work.

## 3. Proposed Solution

### 3.1. New Model: `Organization`
```python
class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
- Registered in `core/admin.py` for CRUD management.
- `active` flag allows soft‑deletion (existing participants keep the reference).

### 3.2. Migrate `Participant.organization` to ForeignKey
- Change field to `ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)`.
- **Data migration steps**:
  1. Create `Organization` instances for each distinct non‑empty `organization` string currently in `Participant`.
  2. Map each participant’s organization string to the corresponding `Organization` instance.
  3. Participants with empty string become `NULL` (no organization).
- **Migration safety**: Use a two‑step migration (add new FK, migrate data, remove old CharField) to avoid data loss.

### 3.3. Update Forms
- `ParticipantProfileForm`:
  - Replace `TextInput` with `Select` widget.
  - Queryset: `Organization.objects.filter(active=True).order_by('name')`.
  - Keep “required” validation (can’t be `NULL` unless `blank=True` is kept).
- Admin: `ParticipantAdmin` can show `organization__name` in list display.

### 3.4. Update Business Logic
- **Same‑org detection**: Compare `mentor.organization_id == mentee.organization_id` (both non‑null).
- **Missing org detection**: Check `organization_id__isnull=True` (instead of empty string).
- **Organization distribution**: Group by `organization__name` (or “No Organization” for nulls).
- **Export**: Include `organization.name` (or empty string).
- **Import** (future): Validate column values against existing `Organization` names; reject unknown values in preview.

### 3.5. Update Fixtures & Tests
- All fixture files need to reference `Organization` primary keys.
- Tests that create `Participant` instances must either create an `Organization` first or use a fixture.
- Update test assertions that rely on organization strings.

## 4. Detailed Changes List

### 4.1. Model Changes (`apps/core/models.py`)
- Add `Organization` class.
- Modify `Participant.organization` to `ForeignKey`.
- Possibly add a property `organization_name` for backward compatibility in templates.

### 4.2. Migrations
1. `core/migrations/0003_organization.py` – create `Organization` model.
2. `core/migrations/0004_add_organization_fk.py` – add nullable FK, data migration, remove old CharField, rename FK.

### 4.3. Forms (`apps/core/forms.py`)
- Update `ParticipantProfileForm.Meta.fields` (still `"organization"`).
- Change widget to `forms.Select`.
- Adjust `clean_organization` to validate FK presence.

### 4.4. Admin (`apps/core/admin.py`)
- Register `OrganizationAdmin`.
- Update `ParticipantAdmin.list_display` and `search_fields` to use `organization__name`.

### 4.5. Business Logic
- `apps/matching/data_prep.py`:
  - `_build_same_org_matrix`: compare IDs.
  - `_build_participant_orgs`: return name (or empty string) from FK.
- `apps/matching/readiness.py`:
  - `check_missing_org`: look for `organization__isnull=True`.
  - `get_organization_distribution`: group by `organization__name`.
- `apps/matching/domain.py`:
  - `_get_org_name`: retrieve name via FK.
- `apps/matching/solvers/strict.py`:
  - `_get_strict_feasible_pairs`: use same‑org matrix (already updated via data_prep).

### 4.6. Templates
- Any template that directly outputs `{{ participant.organization }}` will now output an `Organization` object; need to change to `{{ participant.organization.name }}` (or use a property).
- Search for `organization` in `.html` files.

### 4.7. Tests
- Update all test fixtures.
- Adjust test helpers that create participants.
- Update assertions that check organization strings.

### 4.8. CSV Import/Export (future)
- Export: include `organization.name`.
- Import: validate column against `Organization.objects.values_list('name', flat=True)`.

## 5. Tradeoffs & Considerations

### 5.1. ForeignKey vs CharField with Choices
- **ForeignKey**:
  - ✅ Referential integrity, easy admin CRUD, scalable.
  - ⚠️ Adds join overhead (negligible for ≤30 participants).
- **CharField with choices**:
  - ✅ Simpler migration, no extra table.
  - ❌ Cannot add metadata (description, active flag) without JSON field.
  - ❌ Harder to manage dynamic list via admin.

**Recommendation**: ForeignKey is more maintainable and aligns with “admin‑managed list” requirement.

### 5.2. Null vs Empty String for “No Organization”
- Current: empty string `""` is a valid value (treated as a distinct organization).
- Proposed: `NULL` represents “no organization”.
- **Impact**: Two participants with empty strings are currently considered same org; after migration they’ll both be `NULL` and still considered same org (if we treat `NULL` as a value). This preserves existing behavior.
- **Decision**: Treat `NULL` as a distinct “No Organization” bucket for same‑org detection.

### 5.3. Migration Strategy
- **Option A**: Direct field alteration with data migration in one migration.
  - Risk: If migration fails, rollback is harder.
- **Option B**: Add new FK field, migrate data, drop old field, rename FK.
  - Safer, allows backward rollback.
- **Recommendation**: Option B, following Django’s recommended pattern for changing field type.

### 5.4. Performance
- Additional join in participant queries (admin list, readiness checks). Acceptable given small cohort sizes.
- Index on `organization_id` will be added automatically.

### 5.5. Backward Compatibility
- Templates that assume `organization` is a string will break. Must audit all templates.
- Can add a `@property` `organization_name` that returns `self.organization.name if self.organization else ""`.

## 6. Impact on Testing & Manual Test Plan

### 6.1. Automated Tests
- All tests that create `Participant` instances must be updated to either:
  - Create an `Organization` fixture first.
  - Use a factory that creates an `Organization` on the fly.
- Test assertions checking organization strings must use `organization.name`.
- **Files to update**:
  - `apps/core/tests/test_models.py`
  - `apps/core/tests/test_forms.py`
  - `apps/core/tests/test_views.py`
  - `apps/matching/tests/` (multiple files)

### 6.2. Manual Test Plan (`docs/testing/final_manual_test_plan.md`)
- **Slice 3 (Participant profile)**: Verify dropdown appears, selection persists.
- **Slice 5 (Preferences editor)**: “Show blocked” toggle still works (same‑org detection uses FK).
- **Slice 6 (Admin dashboard readiness)**: Missing‑org detection works with null FK; org distribution table shows organization names.
- **Slice 8 (Strict matching)**: Same‑org constraint still prevents matching.
- **Slice 9 (Exception matching)**: E3 classification still triggers for same organization.
- **Slice 12 (Manual override)**: No change.

**Action**: Update the manual test plan to include verification of the organization dropdown and admin organization management.

### 6.3. Fixtures & Seed Scripts
- All seed scripts (`scripts/seed_*.sh`) load JSON fixtures.
- Fixtures must be regenerated to include `Organization` records and reference their PKs in `Participant` entries.
- This is a **breaking change** for existing fixture files; must be coordinated with any ongoing development.

## 7. Recommendations & Next Steps

1. **Phase 1 – Create Organization model and admin** (non‑breaking).
   - Add `Organization` model, register in admin.
   - Create migration, deploy.

2. **Phase 2 – Data migration**.
   - Write data migration that creates `Organization` instances from existing distinct strings.
   - Add nullable FK to `Participant`, run migration.
   - Update code to use FK where possible while keeping CharField for fallback.

3. **Phase 3 – Update UI and business logic**.
   - Change `ParticipantProfileForm` to use dropdown.
   - Update `data_prep.py`, `readiness.py`, `domain.py`, `strict.py` to use FK.
   - Update templates.

4. **Phase 4 – Remove old CharField**.
   - After verifying everything works, drop the old `organization` CharField.
   - Rename FK field to `organization`.

5. **Phase 5 – Update fixtures and tests**.
   - Regenerate fixtures with `Organization` references.
   - Update all test files.

6. **Phase 6 – Manual validation**.
   - Follow the updated manual test plan to verify all slices work.
   - Only after validation passes, write automated tests for new organization management.

### 7.1. Critical Dependencies
- No other phase can be considered complete until manual validation passes (per AGENTS.md).
- Must update `AGENTS.md` if any new lint/typecheck commands are needed (none anticipated).

### 7.2. Risks
- **Data migration errors**: Ensure backup before running migrations.
- **Template breakage**: Thorough search for `organization` in templates.
- **Fixture breakage**: Coordinate with team to regenerate fixtures.

### 7.3. Estimated Effort
- Model & migration: 1–2 hours.
- Business logic updates: 2–3 hours.
- UI updates: 1–2 hours.
- Test updates: 2–3 hours.
- Manual validation: 1 hour.

**Total**: ~8–11 hours of focused development.

## 8. Conclusion

Migrating the organization field from free‑text to a fixed admin‑managed list is feasible with a clear ForeignKey‑based approach. The proposed plan maintains backward compatibility, preserves all existing matching constraints, and aligns with the requirement of giving admins full control over the organization list.

The largest effort will be updating the test suite and fixtures, but this can be phased to minimize disruption. Following the phase discipline and manual validation gates will ensure a smooth transition.

---

*This document serves as a planning reference for the implementation. All changes must adhere to the phase discipline and validation rules outlined in `AGENTS.md`.*