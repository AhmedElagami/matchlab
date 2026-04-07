# 07 — CSV Import

## Mentor slide data import

MatchLab supports importing mentor profile data from CSV files. This populates `MentorProfile` records for mentors already registered in a cohort.

### Template

Sample template at `resources/sample_data/sample_mentor_template.csv`:

```csv
mentor_email,organization,job_title,function,expertise_tags,languages,location,years_experience,coaching_topics,bio
```

### Required columns

| Column | Description |
|--------|-------------|
| `mentor_email` | Must match an existing User email linked to a Mentor Participant in the cohort |
| `organization` | Must be non-empty |

### Optional columns

| Column | Description |
|--------|-------------|
| `job_title` | Mentor's job title |
| `function` | Business function (e.g., Engineering, Finance) |
| `expertise_tags` | Comma-separated tags, normalized on import (trimmed, lowercased) |
| `languages` | Comma-separated language codes |
| `location` | City or region |
| `years_experience` | Integer; invalid values are rejected |
| `coaching_topics` | Comma-separated topics |
| `bio` | Free text |

### Mentee template

Sample at `resources/sample_data/sample_mentee_template.csv`:

```csv
email,first_name,last_name,display_name,organization,preferred_expertise,preferred_location,preferred_languages,notes
```

### Import behavior

1. Each row is matched to a mentor participant by email within the cohort.
2. Organization is validated as non-empty.
3. Tag fields (`expertise_tags`, `coaching_topics`) are normalized: split on comma/semicolon, trimmed, lowercased.
4. `years_experience` must be a valid integer or blank.
5. Results are stored in `MentorProfile` with `slide_source = CSV_IMPORT`.

### Validation and error handling

The import produces a preview with:
- **Accepted rows**: matched to a participant, all validations passed.
- **Rejected rows**: with specific error messages per row.

Rejected rows do not affect the database. The admin reviews the preview before confirming.

The `ImportJob` model tracks each import:
- Status progression: `PENDING` → `PROCESSING` → `PREVIEW` → `COMPLETED` or `FAILED`.
- `error_message` stores any global errors.
- `total_rows` and `processed_rows` track progress.

### Rules

- Import does **not** partially apply unless the admin confirms.
- No silent auto-fix behavior — all issues are surfaced in the preview.
- Emails are matched case-insensitively.
- Rows with unknown emails are rejected with a clear message.
