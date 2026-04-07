# 05 — Authentication & Roles

## Identity system

MatchLab uses Django's built-in `django.contrib.auth` with the standard `User` model. There is no custom user model.

Authentication is session-based (Django sessions middleware + `AuthenticationMiddleware`).

### Login / Logout

| URL | View | Template |
|-----|------|----------|
| `/auth/login/` | `django.contrib.auth.views.LoginView` | `templates/auth/login.html` |
| `/auth/logout/` | `core.views.logout_view` | Redirects to `/auth/login/` |
| `/register/` | `core.views.register_view` | `templates/registration/register.html` |

Settings:
```python
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"
LOGIN_URL = "/auth/login/"
```

### Registration

`RegistrationForm` extends Django's `UserCreationForm` and collects:
- Username, email, first name, last name, password
- Role choice: `MENTOR` or `MENTEE`

After registration the user is logged in and redirected to `/` (home).

Note: Registration creates a `User` but does **not** automatically create a `Participant`. Participants are created separately (via Django Admin or CSV import) and linked to a User + Cohort.

## Roles

There are three effective roles, determined by model fields — not by Django groups or custom permissions.

### Admin

Identified by: `user.is_staff == True` or `user.is_superuser == True`.

Can:
- Access the admin dashboard (`/dashboard/`)
- View cohort dashboards with readiness diagnostics
- Manage organizations (create, activate/deactivate via Django Admin)
- Run matching (strict, exception, incremental)
- View match results
- Export results (CSV, XLSX)
- Create manual overrides
- Set a match run as active
- Access Django Admin (`/admin/`)
- Manage all cohort data

### Mentor

Identified by: `Participant.role_in_cohort == "MENTOR"` for a given cohort.

Can:
- View and edit their own profile (display name, organization — selected from admin-managed dropdown)
- Fill out mentor intro data (job title, function, expertise tags, years experience, bio)
- View and rank mentee candidates
- Submit/lock preferences

### Mentee

Identified by: `Participant.role_in_cohort == "MENTEE"` for a given cohort.

Can:
- View and edit their own profile (display name, organization — selected from admin-managed dropdown)
- Fill out desired mentor attributes (tags, bio)
- View and rank mentor candidates
- Submit/lock preferences

## Permission enforcement

### View-level decorators

All protected views use Django decorators:

```python
@login_required                    # Requires authenticated user
@user_passes_test(is_admin)        # Requires is_staff or is_superuser
```

The `is_admin` check is defined identically in each admin view module:
```python
def is_admin(user):
    return user.is_staff or user.is_superuser
```

### Cohort membership checks

Participant-facing views verify cohort membership explicitly:

```python
participant = Participant.objects.get(user=request.user, cohort=cohort)
```

If the user is not a participant in the requested cohort, they get an error message and are redirected to home.

### CSRF protection

All POST forms include `{% csrf_token %}`. Django's `CsrfViewMiddleware` is active.

### One-to-one enforcement

The `Match` model has `unique_together` constraints on `(match_run, mentor)` and `(match_run, mentee)`, enforcing one-to-one at the database level.

## Home page routing

The home view (`/`) routes users based on role:

1. **Admin** → redirected to `/dashboard/` (admin dashboard).
2. **Participant in one cohort** → redirected to `/cohorts/<id>/profile/`.
3. **Participant in multiple cohorts** → shown a cohort selector page.

## Summary of protected URLs

| URL pattern | Required role |
|-------------|--------------|
| `/dashboard/` | Admin |
| `/cohort/<id>/dashboard/` | Admin |
| `/cohort/<id>/run-matching/` | Admin |
| `/match-run/<id>/results/` | Admin |
| `/match-run/<id>/export/` | Admin |
| `/match-run/<id>/override/` | Admin |
| `/cohort/<id>/match-run/<id>/set-active/` | Admin |
| `/cohorts/<id>/profile/` | Authenticated + cohort member |
| `/cohorts/<id>/preferences/` | Authenticated + cohort member |
| `/cohorts/<id>/preferences/submit/` | Authenticated + cohort member |
| `/cohort/<id>/my-match/` | Authenticated + cohort member |
| `/register/` | Public |
| `/auth/login/` | Public |
