from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import MenteeDesiredAttributesForm
from apps.core.models import Cohort, Participant
from apps.matching.models import MenteeProfile, PairScore


def is_admin(user):
    """Check if user is admin/staff."""
    return user.is_staff or user.is_superuser


@login_required
def mentee_desired_attributes_view(request, cohort_id):
    """View for mentees to set their desired mentor attributes."""
    cohort = get_object_or_404(Cohort, id=cohort_id)

    # Check if user is a participant in this cohort
    try:
        participant = Participant.objects.get(
            user=request.user, cohort=cohort, role_in_cohort="MENTEE"
        )
    except Participant.DoesNotExist:
        messages.error(request, "You are not a mentee in this cohort.")
        return redirect("core:home")

    # Get or create mentee profile
    mentee_profile, created = MenteeProfile.objects.get_or_create(
        participant=participant
    )

    if request.method == "POST":
        form = MenteeDesiredAttributesForm(request.POST, participant=participant)
        if form.is_valid():
            mentee_profile.desired_attributes = {}
            mentee_profile.bio = form.cleaned_data.get("bio", "")
            mentee_profile.save()

            messages.success(request, "Your preferences have been saved.")
            return redirect(
                "admin_views:mentee_desired_attributes", cohort_id=cohort_id
            )
    else:
        initial_data = {
            "bio": mentee_profile.bio,
        }

        form = MenteeDesiredAttributesForm(
            initial=initial_data, participant=participant
        )

    return render(
        request,
        "admin_views/mentee_desired_attributes.html",
        {
            "form": form,
            "cohort": cohort,
            "participant": participant,
        },
    )


@login_required
@user_passes_test(is_admin)
def cohort_dashboard_view(request, cohort_id):
    """View for cohort readiness dashboard and diagnostics."""
    cohort = get_object_or_404(Cohort, id=cohort_id)

    # Compute scores if not already computed
    if not PairScore.objects.filter(cohort=cohort).exists():
        from apps.matching.scoring import compute_all_pair_scores

        compute_all_pair_scores(cohort)

    # Get diagnostics report
    from apps.matching.readiness import get_diagnostics_report

    diagnostics = get_diagnostics_report(cohort)

    # Get top pair scores for display
    top_pairs = PairScore.objects.filter(cohort=cohort).order_by("-score")[:10]

    return render(
        request,
        "admin_views/cohort_dashboard.html",
        {
            "cohort": cohort,
            "diagnostics": diagnostics,
            "top_pairs": top_pairs,
        },
    )
