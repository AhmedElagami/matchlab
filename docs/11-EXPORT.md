# 11 — Export

## Supported formats

| Format | Content-Type | Endpoint |
|--------|-------------|----------|
| CSV | `text/csv` | `/match-run/<id>/export/?format=csv` |
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `/match-run/<id>/export/?format=xlsx` |

Only runs with `status == "SUCCESS"` can be exported.

## Columns

Both formats include the same columns in the same order:

| # | Column | Description |
|---|--------|-------------|
| 1 | `cohort` | Cohort name |
| 2 | `mentor_name` | Mentor display name |
| 3 | `mentor_email` | Mentor user email |
| 4 | `mentor_org` | Mentor organization |
| 5 | `mentee_name` | Mentee display name |
| 6 | `mentee_email` | Mentee user email |
| 7 | `mentee_org` | Mentee organization |
| 8 | `match_percent` | Match score (0–100) |
| 9 | `ambiguity_flag` | `True` if match is ambiguous |
| 10 | `ambiguity_reason` | Score gap explanation |
| 11 | `exception_flag` | `True` if match violates a policy |
| 12 | `exception_type` | `E1`, `E2`, `E3`, or empty |
| 13 | `exception_reason` | Human-readable explanation |
| 14 | `is_manual_override` | `True` if admin overrode this match |
| 15 | `override_reason` | Admin's justification for override |

## XLSX specifics

The XLSX export includes:
- Bold headers with gray background fill.
- Centered header alignment.
- Auto-adjusted column widths (max 50 characters).
- Frozen header row (scroll data while headers stay visible).
- Metadata footer rows with export timestamp, match run ID, cohort name, and mode.

## Implementation

- `export.py:export_match_run_csv()` returns a CSV string.
- `export.py:export_match_run_xlsx()` returns XLSX bytes (using `openpyxl`).
- Both call `service.py:get_match_run_results()` which queries `Match` records with related `mentor` and `mentee` participants.

## Access control

Export is restricted to admin users (`@login_required` + `@user_passes_test(is_admin)`).
