
# AGENTS.md — Mentor–Mentee Matchmaker

## Purpose

This document defines **how AI coding agents must operate** in this repository.
It is binding for all automated and human-assisted changes.

This project is implemented in **strict phases** based on an approved Technical Specification.
Agents must follow phase discipline, manual validation gates, and quality rules.

This file defines **process and behavior**, not business logic.

---

## Source of Truth

The following documents are authoritative:

1. **TECHNICAL_SPEC.md**

   * System requirements
   * Data model
   * Matching rules
   * Exception policies
   * UI and workflow requirements

1. **AGENTS.md** (this file)

   * How agents must work

If there is any conflict:
**TECHNICAL_SPEC.md > AGENTS.md > Agent assumptions**

Agents must not invent requirements.

---

## Phase Discipline (MANDATORY)

### One phase at a time

* Agents must implement **ONLY the currently assigned phase**.
* Do NOT implement features from future phases.
* Do NOT refactor unrelated code.

### Vertical slice requirement

Each phase must result in:

* A runnable UI feature
* Real browser-based manual validation
* Persisted data changes (if applicable)

No phase is considered complete without manual validation.

---

## Manual Validation Gate (CRITICAL)

### Rule

> No automated tests may be written until manual validation passes.

Agents must:

1. Implement features
2. Provide a **step-by-step manual validation script**
3. Wait for confirmation that validation passed
4. Only then implement tests

If manual validation fails:

* Fix only the reported issues
* Do NOT add tests

---

## Testing Rules

### Test strategy

* Unit + integration: `pytest` + `pytest-django`
* E2E: `playwright` (Python)
* BDD: `pytest-bdd` only for 2–5 critical business scenarios

### What NOT to do

* Do NOT snapshot-test HTML
* Do NOT write brittle CSS selector tests
* Do NOT mock OR-Tools for solver tests (use small real datasets)

### data-testid

All critical UI elements MUST include stable `data-testid` attributes:

* Buttons
* Form inputs
* Run matching actions
* Filters
* Export actions

Playwright tests must use `data-testid`, not CSS classes.

---

## UI Quality Rules

All UI must:

* Use **Bootstrap 5**
* Extend a single base layout
* Have inline validation errors
* Mark required fields
* Use consistent cards, tables, and alerts

Forbidden:

* Inline styles
* Custom CSS frameworks
* Inconsistent layouts per page

---

## Solver & Business Logic Rules

* OR-Tools CP-SAT is required for matching.
* Strict mode and Exception mode must be separate code paths.
* Penalty priorities must follow:

  1. Org violation (worst)
  2. Neither acceptable
  3. One-sided acceptable
* All exceptions must be:

  * Flagged
  * Explained
  * Exported

Agents must not simplify solver logic.

---

## Data & Migrations

* All model changes must include migrations.
* No manual DB changes.
* No squashed migrations unless explicitly instructed.
* Data integrity constraints must be enforced at model + DB level where appropriate.

---

## Auditability & History

* All match runs must be persisted.
* Overrides must be persisted with:

  * is_manual_override
  * override_reason
* Active run must be explicitly set.

No destructive updates to historical runs.

---

## CSV Import Rules

* CSV import must:

  * Preview errors
  * Not partially apply unless admin confirms
  * Normalize tags
  * Validate emails and organizations

Agents must not add silent auto-fix behavior.

---

## Security & Permissions

* All admin views require admin role checks.
* All cohort-scoped views must verify cohort membership.
* No IDOR vulnerabilities.
* CSRF protection on all POST forms.

---

## Logging & Observability

Agents must:

* Log match run start/end
* Log strict vs exception mode
* Log solver duration
* Log number of exceptions

Logs must not include PII beyond participant IDs/emails already in DB.

---

## Performance Rules

* N ≤ 30 is assumed.
* OR-Tools time limits must be enforced.
* Any loop over pairs must be O(N²) at worst.

---

## Git Hygiene

* Small, focused commits per phase.
* Clear commit messages:

  * `phase-3: add mentor CSV import`
  * `phase-5: strict solver + results UI`

---

## What Agents Must NOT Do

* Do NOT redesign architecture
* Do NOT replace Django
* Do NOT add React/Vue
* Do NOT remove Bootstrap
* Do NOT remove audit/history
* Do NOT collapse strict + exception logic
* Do NOT skip manual validation

---

## Required Agent Output Format

For each phase, agents must output:

1. Phase-specific implementation plan
2. Code changes
3. Manual validation script
4. Wait for validation confirmation
5. Then tests

---
