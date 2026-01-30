"""Manual override functionality for match results."""

from typing import Tuple, Optional
from django.db import transaction
from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant
from apps.matching.models import MatchRun, Match, ActiveMatchRun
from apps.matching.exceptions import classify_exception


def validate_override_pair(
    mentor: Participant, 
    mentee: Participant, 
    cohort: Cohort,
    match_run: MatchRun
) -> Tuple[bool, str]:
    """
    Validate that a manual override pair is valid.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check that both participants are in the same cohort
    if mentor.cohort != cohort or mentee.cohort != cohort:
        return False, "Both participants must be in the same cohort"
    
    # Check that mentor is actually a mentor and mentee is actually a mentee
    if mentor.role_in_cohort != "MENTOR":
        return False, "First participant must be a mentor"
    
    if mentee.role_in_cohort != "MENTEE":
        return False, "Second participant must be a mentee"
    
    # Check that both participants have submitted preferences
    if not mentor.is_submitted or not mentee.is_submitted:
        return False, "Both participants must have submitted their preferences"
    
    return True, ""


def get_swap_suggestion(
    mentor: Participant, 
    mentee: Participant, 
    match_run: MatchRun
) -> Optional[Tuple[Participant, Participant]]:
    """
    Suggest a swap to maintain one-to-one constraint.
    
    Returns:
        Tuple of (existing_mentor, existing_mentee) that would need to be swapped,
        or None if this would create a new pairing without breaking existing ones.
    """
    # Find existing matches for these participants
    try:
        mentor_existing_match = Match.objects.get(
            match_run=match_run, 
            mentor=mentor
        )
        mentor_current_mentee = mentor_existing_match.mentee
    except Match.DoesNotExist:
        mentor_current_mentee = None
    
    try:
        mentee_existing_match = Match.objects.get(
        match_run=match_run, 
        mentee=mentee
    )
        mentee_current_mentor = mentee_existing_match.mentor
    except Match.DoesNotExist:
        mentee_current_mentor = None
    
    # If both participants are already matched to each other, no swap needed
    if mentor_current_mentee == mentee and mentee_current_mentor == mentor:
        return None
    
    # If both have existing matches that are different, suggest a swap
    if mentor_current_mentee and mentee_current_mentor and mentor_current_mentee != mentee:
        return (mentee_current_mentor, mentor_current_mentee)
    
    # If only one has an existing match, we'd be breaking a pairing
    # This is allowed but requires explicit confirmation
    return None


def create_manual_override(
    match_run: MatchRun,
    mentor: Participant,
    mentee: Participant,
    override_reason: str,
    set_by: User
) -> Tuple[bool, str, Optional[Match]]:
    """
    Create a manual override for a match.
    
    Returns:
        Tuple of (success, message, match_object)
    """
    # Validate the pair
    is_valid, error_msg = validate_override_pair(mentor, mentee, match_run.cohort, match_run)
    if not is_valid:
        return False, error_msg, None
    
    # Check if this creates an exception
    exception_type, exception_reason = classify_exception(
        mentor, mentee, 
        list(Participant.objects.filter(cohort=match_run.cohort, role_in_cohort="MENTOR")),
        list(Participant.objects.filter(cohort=match_run.cohort, role_in_cohort="MENTEE"))
    )
    
    # If it's an exception, override reason is required
    if exception_type and not override_reason.strip():
        return False, "Override reason is required when creating an exception match", None
    
    try:
        with transaction.atomic():
            # Look for existing match with this mentor
            try:
                mentor_match = Match.objects.get(match_run=match_run, mentor=mentor)
                # Update existing match
                mentor_match.mentee = mentee
                mentor_match.is_manual_override = True
                mentor_match.override_reason = override_reason
                mentor_match.exception_flag = bool(exception_type)
                mentor_match.exception_type = exception_type
                mentor_match.exception_reason = exception_reason
                mentor_match.save()
                match_obj = mentor_match
            except Match.DoesNotExist:
                # Create new match
                match_obj = Match.objects.create(
                    match_run=match_run,
                    mentor=mentor,
                    mentee=mentee,
                    score_percent=0,  # Manual overrides don't have computed scores
                    is_manual_override=True,
                    override_reason=override_reason,
                    exception_flag=bool(exception_type),
                    exception_type=exception_type,
                    exception_reason=exception_reason,
                )
            
            # Also ensure the mentee isn't matched to someone else
            Match.objects.filter(match_run=match_run, mentee=mentee).exclude(mentor=mentor).delete()
            
    except Exception as e:
        return False, f"Error creating override: {str(e)}", None
    
    return True, "Override created successfully", match_obj


def set_active_match_run(cohort: Cohort, match_run: MatchRun, set_by: User) -> Tuple[bool, str]:
    """
    Set a match run as the active run for a cohort.
    
    Returns:
        Tuple of (success, message)
    """
    if match_run.cohort != cohort:
        return False, "Match run must belong to the specified cohort"
    
    if match_run.status != "SUCCESS":
        return False, "Only successful match runs can be set as active"
    
    try:
        active_run, created = ActiveMatchRun.objects.update_or_create(
            cohort=cohort,
            defaults={
                'match_run': match_run,
                'set_by': set_by
            }
        )
        if created:
            return True, "Active match run set successfully"
        else:
            return True, "Active match run updated successfully"
    except Exception as e:
        return False, f"Error setting active match run: {str(e)}"


def get_active_match_for_participant(participant: Participant) -> Optional[Match]:
    """
    Get the active match for a participant.
    
    Returns:
        Match object or None if no active match exists
    """
    try:
        active_run = ActiveMatchRun.objects.get(cohort=participant.cohort)
        if participant.role_in_cohort == "MENTOR":
            match = Match.objects.get(
                match_run=active_run.match_run,
                mentor=participant
            )
        else:  # MENTEE
            match = Match.objects.get(
                match_run=active_run.match_run,
                mentee=participant
            )
        return match
    except (ActiveMatchRun.DoesNotExist, Match.DoesNotExist):
        return None