from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from apps.core.models import Cohort, Participant
from .models import Preference
from .forms import PreferencesForm
import logging

logger = logging.getLogger(__name__)


@login_required
def preferences_view(request, cohort_id):
    """View for managing preferences."""
    cohort = get_object_or_404(Cohort, id=cohort_id)

    # Check if user is a participant in this cohort
    try:
        participant = Participant.objects.get(user=request.user, cohort=cohort)
    except Participant.DoesNotExist:
        messages.error(request, "You are not a participant in this cohort.")
        return redirect("core:home")

    # If already submitted, show read-only view
    if participant.is_submitted:
        return _show_readonly_preferences(request, participant, cohort)

    # Determine opposite role
    if participant.role_in_cohort == "MENTOR":
        opposite_role = "MENTEE"
    else:
        opposite_role = "MENTOR"

    # Get candidates (participants in same cohort with opposite role)
    candidates = Participant.objects.filter(
        cohort=cohort, role_in_cohort=opposite_role
    ).order_by("display_name")

    # Handle show_blocked toggle
    show_blocked = request.GET.get("show_blocked", "false") == "true"

    # Filter out same organization unless show_blocked is True
    if not show_blocked:
        candidates = candidates.exclude(organization=participant.organization)
        blocked_candidates = Participant.objects.filter(
            cohort=cohort,
            role_in_cohort=opposite_role,
            organization=participant.organization,
        ).order_by("display_name")
    else:
        blocked_candidates = []

    if request.method == "POST":
        form = PreferencesForm(
            request.POST, participant=participant, candidates=candidates
        )
        if form.is_valid():
            try:
                duplicate_warning, normalized_ranks = form.save()

                if duplicate_warning:
                    # Create a message detailing the changes
                    messages.warning(
                        request,
                        "Duplicate ranks were automatically resolved. Ranks have been renumbered sequentially.",
                    )

                messages.success(request, "Preferences saved successfully.")
                return redirect("matching:preferences", cohort_id=cohort_id)
            except Exception as e:
                logger.error(f"Error saving preferences: {e}")
                messages.error(request, "An error occurred while saving preferences.")
    else:
        # Pre-populate form with existing preferences
        initial_data = {}
        existing_preferences = Preference.objects.filter(from_participant=participant)
        for pref in existing_preferences:
            field_name = f"candidate_{pref.to_participant.id}"
            initial_data[field_name] = pref.rank

        form = PreferencesForm(
            participant=participant, candidates=candidates, initial=initial_data
        )

    return render(
        request,
        "matching/preferences.html",
        {
            "form": form,
            "cohort": cohort,
            "participant": participant,
            "candidates": candidates,
            "blocked_candidates": blocked_candidates,
            "show_blocked": show_blocked,
        },
    )


@login_required
def submit_preferences_view(request, cohort_id):
    """View for submitting preferences."""
    if request.method != "POST":
        return HttpResponseForbidden(b"Only POST requests are allowed.")

    cohort = get_object_or_404(Cohort, id=cohort_id)

    # Check if user is a participant in this cohort
    try:
        participant = Participant.objects.get(user=request.user, cohort=cohort)
    except Participant.DoesNotExist:
        messages.error(request, "You are not a participant in this cohort.")
        return redirect("core:home")

    # If already submitted, don't allow resubmission
    if participant.is_submitted:
        messages.error(request, "Preferences have already been submitted.")
        return redirect("matching:preferences", cohort_id=cohort_id)

    # Mark as submitted
    participant.is_submitted = True
    participant.save(update_fields=["is_submitted"])

    messages.success(request, "Preferences submitted successfully!")
    return redirect("matching:preferences", cohort_id=cohort_id)


def _show_readonly_preferences(request, participant, cohort):
    """Show read-only view of preferences after submission."""
    # Determine opposite role
    if participant.role_in_cohort == "MENTOR":
        opposite_role = "MENTEE"
    else:
        opposite_role = "MENTOR"

    # Get all candidates for display
    candidates = Participant.objects.filter(
        cohort=cohort, role_in_cohort=opposite_role
    ).order_by("display_name")

    # Get existing preferences
    preferences = Preference.objects.filter(
        from_participant=participant
    ).select_related("to_participant")

    # Create a mapping for easy lookup
    preference_dict = {pref.to_participant.id: pref.rank for pref in preferences}

    return render(
        request,
        "matching/preferences_readonly.html",
        {
            "cohort": cohort,
            "participant": participant,
            "candidates": candidates,
            "preference_dict": preference_dict,
        },
    )
