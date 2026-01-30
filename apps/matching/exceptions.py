"""Exception classification for match results."""

from typing import Dict, List, Tuple
from apps.core.models import Participant
from apps.matching.models import Preference


def classify_exception(
    mentor: Participant,
    mentee: Participant,
    mentors: List[Participant],
    mentees: List[Participant],
) -> Tuple[str, str]:
    """
    Classify a match as an exception and provide reason.

    Returns:
        Tuple of (exception_type, exception_reason)
        exception_type: 'E1', 'E2', or 'E3'
        exception_reason: Human-readable explanation
    """
    # Check for E3: Same organization (highest severity)
    if mentor.organization == mentee.organization:
        return ("E3", f"Same organization: {mentor.organization}")

    # Check preferences for mutual acceptability
    mentor_accepts = set()
    mentee_accepts = set()

    # Get mentor's preferences
    mentor_prefs = Preference.objects.filter(from_participant=mentor)
    for pref in mentor_prefs:
        mentor_accepts.add(pref.to_participant.id)

    # Get mentee's preferences
    mentee_prefs = Preference.objects.filter(from_participant=mentee)
    for pref in mentee_prefs:
        mentee_accepts.add(pref.to_participant.id)

    # Check for E2: Neither accepts (large penalty)
    if (mentee.id not in mentor_accepts) and (mentor.id not in mentee_accepts):
        return ("E2", "Neither participant ranked the other")

    # Check for E1: One-sided acceptance (medium penalty)
    if (mentee.id not in mentor_accepts) or (mentor.id not in mentee_accepts):
        if mentee.id not in mentor_accepts:
            return ("E1", "Mentor did not rank mentee")
        else:
            return ("E1", "Mentee did not rank mentor")

    # Should not reach here for exception matches, but just in case
    return ("", "No exception")


def get_exception_priority(exception_type: str) -> int:
    """
    Get priority level for exception type (higher = more severe).

    Returns:
        3 for E3 (same org - highest)
        2 for E2 (neither accepts - large)
        1 for E1 (one-sided - medium)
        0 for no exception
    """
    if exception_type == "E3":
        return 3
    elif exception_type == "E2":
        return 2
    elif exception_type == "E1":
        return 1
    return 0
