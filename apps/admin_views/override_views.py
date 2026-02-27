"""Admin views for manual override functionality."""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from apps.core.models import Cohort, Participant
from apps.matching.models import MatchRun, Match
from apps.matching import override

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is admin/staff."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def override_view(request, match_run_id):
    """View for manual override of matches."""
    match_run = get_object_or_404(MatchRun, id=match_run_id)
    
    # Verify user has access to this cohort
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect("core:home")
    
    # Get all participants in this cohort
    mentors = Participant.objects.filter(
        cohort=match_run.cohort, 
        role_in_cohort="MENTOR",
        is_submitted=True
    ).order_by("display_name")
    
    mentees = Participant.objects.filter(
        cohort=match_run.cohort, 
        role_in_cohort="MENTEE",
        is_submitted=True
    ).order_by("display_name")
    
    # Get existing matches for this run
    matches = match_run.matches.select_related("mentor", "mentee").all()
    
    if request.method == "POST":
        # Handle override form submission
        mentor_id = request.POST.get("mentor")
        mentee_id = request.POST.get("mentee")
        override_reason = request.POST.get("override_reason", "").strip()
        
        if not mentor_id or not mentee_id:
            messages.error(request, "Please select both a mentor and a mentee.")
            return render(
                request,
                "admin_views/override.html",
                {
                    "match_run": match_run,
                    "mentors": mentors,
                    "mentees": mentees,
                    "matches": matches,
                    "selected_mentor": mentor_id,
                    "selected_mentee": mentee_id,
                    "override_reason": override_reason,
                },
            )
        
        try:
            mentor = Participant.objects.get(id=mentor_id, cohort=match_run.cohort)
            mentee = Participant.objects.get(id=mentee_id, cohort=match_run.cohort)
        except Participant.DoesNotExist:
            messages.error(request, "Invalid mentor or mentee selected.")
            return render(
                request,
                "admin_views/override.html",
                {
                    "match_run": match_run,
                    "mentors": mentors,
                    "mentees": mentees,
                    "matches": matches,
                    "selected_mentor": mentor_id,
                    "selected_mentee": mentee_id,
                    "override_reason": override_reason,
                },
            )
        
        # Check for suggested swap
        swap_suggestion = override.get_swap_suggestion(mentor, mentee, match_run)
        
        # If there's a swap suggestion and user hasn't confirmed, show confirmation
        confirm_swap = request.POST.get("confirm_swap")
        if swap_suggestion and not confirm_swap:
            return render(
                request,
                "admin_views/override.html",
                {
                    "match_run": match_run,
                    "mentors": mentors,
                    "mentees": mentees,
                    "matches": matches,
                    "selected_mentor": mentor_id,
                    "selected_mentee": mentee_id,
                    "override_reason": override_reason,
                    "swap_suggestion": swap_suggestion,
                },
            )
        
        # Create the override
        success, message, match_obj = override.create_manual_override(
            match_run, mentor, mentee, override_reason, request.user
        )
        
        if success:
            messages.success(request, message)
            return redirect("admin_views:override", match_run_id=match_run.id)
        else:
            messages.error(request, message)
    
    return render(
        request,
        "admin_views/override.html",
        {
            "match_run": match_run,
            "mentors": mentors,
            "mentees": mentees,
            "matches": matches,
        },
    )


@login_required
@user_passes_test(is_admin)
def set_active_run_view(request, cohort_id, match_run_id):
    """View for setting a match run as active."""
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("admin_views:run_matching", cohort_id=cohort_id)
    
    cohort = get_object_or_404(Cohort, id=cohort_id)
    match_run = get_object_or_404(MatchRun, id=match_run_id, cohort=cohort)
    
    success, message = override.set_active_match_run(cohort, match_run, request.user)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect("admin_views:match_results", match_run_id=match_run_id)


@login_required
def my_match_view(request, cohort_id):
    """View for participants to see their active match."""
    cohort = get_object_or_404(Cohort, id=cohort_id)
    
    # Check if user is a participant in this cohort
    try:
        participant = Participant.objects.get(user=request.user, cohort=cohort)
    except Participant.DoesNotExist:
        messages.error(request, "You are not a participant in this cohort.")
        return redirect("core:home")
    
    # Get active match
    match = override.get_active_match_for_participant(participant)
    
    return render(
        request,
        "participant/my_match.html",
        {
            "cohort": cohort,
            "participant": participant,
            "match": match,
        },
    )