"""Readiness checks for cohort matching feasibility."""

from typing import Dict, List, Tuple, Any
from django.db.models import Count, Q
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, PairScore


# Default configuration values
DEFAULT_MIN_OPTIONS_STRICT = 3


def get_cohort_config(cohort: Cohort) -> Dict[str, Any]:
    """Get cohort configuration with defaults."""
    config = {
        "min_options_strict": DEFAULT_MIN_OPTIONS_STRICT,
    }
    config.update(cohort.cohort_config)
    return config


def check_counts_mismatch(cohort: Cohort) -> Tuple[bool, str]:
    """Check if mentor and mentee counts are balanced."""
    mentor_count = Participant.objects.filter(
        cohort=cohort, role_in_cohort="MENTOR"
    ).count()
    mentee_count = Participant.objects.filter(
        cohort=cohort, role_in_cohort="MENTEE"
    ).count()

    if mentor_count != mentee_count:
        return (
            False,
            f"Counts mismatch: {mentor_count} mentors vs {mentee_count} mentees",
        )

    return True, f"Counts balanced: {mentor_count} mentors and {mentee_count} mentees"


def check_missing_org(cohort: Cohort) -> Tuple[bool, str]:
    """Check if any participants are missing organization."""
    missing_org_count = Participant.objects.filter(
        cohort=cohort, organization=""
    ).count()

    if missing_org_count > 0:
        return False, f"{missing_org_count} participants missing organization"

    return True, "All participants have organization set"


def check_missing_submissions(cohort: Cohort) -> Tuple[bool, str]:
    """Check if any participants haven't submitted preferences."""
    unsubmitted_count = Participant.objects.filter(
        cohort=cohort, is_submitted=False
    ).count()

    if unsubmitted_count > 0:
        return False, f"{unsubmitted_count} participants haven't submitted preferences"

    return True, "All participants have submitted preferences"


def check_mutual_acceptability(cohort: Cohort) -> Tuple[bool, str]:
    """Check if all participants have mutual acceptability with sufficient options."""
    config = get_cohort_config(cohort)
    min_options = config["min_options_strict"]

    # Get all participants
    participants = Participant.objects.filter(cohort=cohort)

    # For each participant, count how many cross-org options they have
    problematic_participants = []

    for participant in participants:
        if participant.role_in_cohort == "MENTOR":
            opposite_role = "MENTEE"
        else:
            opposite_role = "MENTOR"

        # Count cross-org candidates (excluding same org)
        cross_org_candidates = Participant.objects.filter(
            cohort=cohort, role_in_cohort=opposite_role
        ).exclude(organization=participant.organization)

        # Count how many of these candidates have mutual preferences
        mutual_count = 0
        for candidate in cross_org_candidates:
            # Check if both participants have preferences for each other
            mentor_participant = (
                participant if participant.role_in_cohort == "MENTOR" else candidate
            )
            mentee_participant = (
                candidate if participant.role_in_cohort == "MENTOR" else participant
            )

            has_mentor_preference = Preference.objects.filter(
                from_participant=mentor_participant, to_participant=mentee_participant
            ).exists()

            has_mentee_preference = Preference.objects.filter(
                from_participant=mentee_participant, to_participant=mentor_participant
            ).exists()

            if has_mentor_preference and has_mentee_preference:
                mutual_count += 1

        if mutual_count < min_options:
            problematic_participants.append(
                {
                    "participant": participant,
                    "mutual_count": mutual_count,
                    "required": min_options,
                }
            )

    if problematic_participants:
        details = ", ".join(
            [
                f"{p['participant'].display_name} ({p['mutual_count']}/{p['required']} options)"
                for p in problematic_participants
            ]
        )
        return False, f"Participants with insufficient mutual options: {details}"

    return (
        True,
        f"All participants have at least {min_options} mutual cross-org options",
    )


def check_readiness(cohort: Cohort) -> Dict[str, Any]:
    """
    Perform all readiness checks for a cohort.

    Returns:
        Dictionary with readiness status and details.
    """
    checks = [
        ("counts_mismatch", check_counts_mismatch),
        ("missing_org", check_missing_org),
        ("missing_submissions", check_missing_submissions),
        ("mutual_acceptability", check_mutual_acceptability),
    ]

    results = {}
    all_ready = True

    for check_name, check_func in checks:
        is_ready, message = check_func(cohort)
        results[check_name] = {"ready": is_ready, "message": message}
        if not is_ready:
            all_ready = False

    results["overall_ready"] = all_ready

    return results


def get_zero_option_participants(cohort: Cohort) -> List[Dict[str, Any]]:
    """Get participants with zero mutual cross-org options."""
    participants = Participant.objects.filter(cohort=cohort)
    zero_option_participants = []

    for participant in participants:
        if participant.role_in_cohort == "MENTOR":
            opposite_role = "MENTEE"
        else:
            opposite_role = "MENTOR"

        # Count cross-org candidates (excluding same org)
        cross_org_candidates = Participant.objects.filter(
            cohort=cohort, role_in_cohort=opposite_role
        ).exclude(organization=participant.organization)

        # Count how many of these candidates have mutual preferences
        mutual_count = 0
        for candidate in cross_org_candidates:
            # Check if both participants have preferences for each other
            mentor_participant = (
                participant if participant.role_in_cohort == "MENTOR" else candidate
            )
            mentee_participant = (
                candidate if participant.role_in_cohort == "MENTOR" else participant
            )

            has_mentor_preference = Preference.objects.filter(
                from_participant=mentor_participant, to_participant=mentee_participant
            ).exists()

            has_mentee_preference = Preference.objects.filter(
                from_participant=mentee_participant, to_participant=mentor_participant
            ).exists()

            if has_mentor_preference and has_mentee_preference:
                mutual_count += 1

        if mutual_count == 0:
            zero_option_participants.append(
                {
                    "participant": participant,
                    "display_name": participant.display_name,
                    "role": participant.role_in_cohort,
                    "organization": participant.organization,
                    "mutual_count": mutual_count,
                }
            )

    return zero_option_participants


def get_lowest_option_participants(
    cohort: Cohort, limit: int = 5
) -> List[Dict[str, Any]]:
    """Get participants with the lowest mutual cross-org option counts."""
    participants = Participant.objects.filter(cohort=cohort)
    option_counts = []

    for participant in participants:
        if participant.role_in_cohort == "MENTOR":
            opposite_role = "MENTEE"
        else:
            opposite_role = "MENTOR"

        # Count cross-org candidates (excluding same org)
        cross_org_candidates = Participant.objects.filter(
            cohort=cohort, role_in_cohort=opposite_role
        ).exclude(organization=participant.organization)

        # Count how many of these candidates have mutual preferences
        mutual_count = 0
        for candidate in cross_org_candidates:
            # Check if both participants have preferences for each other
            mentor_participant = (
                participant if participant.role_in_cohort == "MENTOR" else candidate
            )
            mentee_participant = (
                candidate if participant.role_in_cohort == "MENTOR" else participant
            )

            has_mentor_preference = Preference.objects.filter(
                from_participant=mentor_participant, to_participant=mentee_participant
            ).exists()

            has_mentee_preference = Preference.objects.filter(
                from_participant=mentee_participant, to_participant=mentor_participant
            ).exists()

            if has_mentor_preference and has_mentee_preference:
                mutual_count += 1

        option_counts.append(
            {
                "participant": participant,
                "display_name": participant.display_name,
                "role": participant.role_in_cohort,
                "organization": participant.organization,
                "mutual_count": mutual_count,
            }
        )

    # Sort by mutual count and return top N
    option_counts.sort(key=lambda x: x["mutual_count"])
    return option_counts[:limit]


def get_org_distribution(cohort: Cohort) -> Dict[str, Dict[str, int]]:
    """Get organization distribution summary."""
    # Count mentors and mentees by organization
    org_stats = {}

    participants = Participant.objects.filter(cohort=cohort)
    for participant in participants:
        org = participant.organization or "No Organization"
        role = participant.role_in_cohort

        if org not in org_stats:
            org_stats[org] = {"MENTOR": 0, "MENTEE": 0, "TOTAL": 0}

        org_stats[org][role] += 1
        org_stats[org]["TOTAL"] += 1

    return org_stats


def get_diagnostics_report(cohort: Cohort) -> Dict[str, Any]:
    """
    Generate a comprehensive diagnostics report for a cohort.

    Returns:
        Dictionary with diagnostics information.
    """
    readiness = check_readiness(cohort)
    zero_options = get_zero_option_participants(cohort)
    lowest_options = get_lowest_option_participants(cohort)
    org_distribution = get_org_distribution(cohort)

    # Generate suggested actions
    suggested_actions = []

    if not readiness["overall_ready"]:
        if not readiness["counts_mismatch"]["ready"]:
            suggested_actions.append("Balance mentor/mentee counts")

        if not readiness["missing_org"]["ready"]:
            suggested_actions.append("Set organization for all participants")

        if not readiness["missing_submissions"]["ready"]:
            suggested_actions.append("Have all participants submit preferences")

        if not readiness["mutual_acceptability"]["ready"]:
            suggested_actions.append(
                "Review participants with insufficient mutual options"
            )

    if zero_options:
        names = [p["display_name"] for p in zero_options]
        suggested_actions.append(
            f"Help participants with zero options: {', '.join(names)}"
        )

    return {
        "readiness": readiness,
        "zero_option_participants": zero_options,
        "lowest_option_participants": lowest_options,
        "org_distribution": org_distribution,
        "suggested_actions": suggested_actions,
    }
