from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.core.models import Cohort, Participant


def is_admin(user):
    """Check if user is admin/staff."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Admin dashboard showing all cohorts and quick actions."""
    # Get all cohorts with participant counts
    cohorts = Cohort.objects.all().order_by("-created_at")

    # Annotate with participant counts
    for cohort in cohorts:
        cohort.mentor_count = Participant.objects.filter(
            cohort=cohort, role_in_cohort="MENTOR"
        ).count()
        cohort.mentee_count = Participant.objects.filter(
            cohort=cohort, role_in_cohort="MENTEE"
        ).count()

    return render(
        request,
        "admin_views/admin_dashboard.html",
        {
            "cohorts": cohorts,
        },
    )
