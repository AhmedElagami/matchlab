"""Domain logic layer - pure functions for business rules."""

from typing import Dict, Tuple, NamedTuple
from .data_prep import PreparedInputs


class ExceptionClassification(NamedTuple):
    """Result of exception classification."""

    exception_type: str  # "E1", "E2", "E3", or "" for no exception
    reason: str  # Human-readable explanation


class PenaltyInfo(NamedTuple):
    """Information about penalties for a pair."""

    penalty_value: int
    penalty_type: str  # "E1", "E2", "E3", or "" for no penalty


def classify_exception(
    mentor_id: int, mentee_id: int, inputs: PreparedInputs
) -> ExceptionClassification:
    """
    Classify a match as an exception based on prepared inputs.

    This is a pure function that operates only on in-memory data.

    Returns:
        ExceptionClassification with type and reason
    """
    # Check for E3: Same organization (highest severity)
    if inputs.same_org[(mentor_id, mentee_id)]:
        org_name = _get_org_name(mentor_id, inputs)  # Helper to get org name
        return ExceptionClassification("E3", f"Same organization: {org_name}")

    # Check acceptability
    acceptability = inputs.acceptability[(mentor_id, mentee_id)]

    # Check for E2: Neither accepts (large penalty)
    if acceptability == "NEITHER":
        return ExceptionClassification("E2", "Neither participant ranked the other")

    # Check for E1: One-sided acceptance (medium penalty)
    if acceptability == "ONE_SIDED_MENTOR_ONLY":
        return ExceptionClassification("E1", "Mentee did not rank mentor")
    elif acceptability == "ONE_SIDED_MENTEE_ONLY":
        return ExceptionClassification("E1", "Mentor did not rank mentee")

    # Mutual acceptability - no exception
    return ExceptionClassification("", "No exception")


def get_penalty_info(
    mentor_id: int, mentee_id: int, inputs: PreparedInputs
) -> PenaltyInfo:
    """
    Get penalty information for a pair based on exception classification.

    This function determines penalty values based on the refactor plan's priority ordering.
    """
    classification = classify_exception(mentor_id, mentee_id, inputs)

    if classification.exception_type == "E3":  # Same org - largest penalty
        return PenaltyInfo(inputs.config["penalty_org"], "E3")
    elif classification.exception_type == "E2":  # Neither accepts - large penalty
        return PenaltyInfo(inputs.config["penalty_neither"], "E2")
    elif classification.exception_type == "E1":  # One-sided - medium penalty
        return PenaltyInfo(inputs.config["penalty_one_sided"], "E1")
    else:
        return PenaltyInfo(0, "")  # No penalty


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


def detect_ambiguity(matches: list, inputs: PreparedInputs) -> list:
    """Detect ambiguous matches based on score gaps.

    Scores in inputs.score are scaled integers (raw × score_scale).
    ambiguity_gap_threshold is in percentage points (0-100 scale).
    We convert to percentage scale before comparing.
    """
    if not matches:
        return []

    scale = inputs.config.get("score_scale", 1000)
    gap_threshold = inputs.config.get("ambiguity_gap_threshold", 5.0)
    ambiguities = []

    def _check_ambiguity(participant_id, matched_id, is_mentee):
        """Check if a participant's match is ambiguous vs their best alternative."""
        matched_score = inputs.score[(matched_id, participant_id)] if is_mentee else inputs.score[(participant_id, matched_id)]
        matched_pct = matched_score / scale

        # Find best alternative
        best_alt_pct = -1
        best_alt_id = None
        candidates = inputs.mentor_ids if is_mentee else inputs.mentee_ids
        for cid in candidates:
            if cid == matched_id:
                continue
            s = inputs.score[(cid, participant_id)] if is_mentee else inputs.score[(participant_id, cid)]
            pct = s / scale
            if pct > best_alt_pct:
                best_alt_pct = pct
                best_alt_id = cid

        if best_alt_id is not None and (matched_pct - best_alt_pct) <= gap_threshold:
            gap = matched_pct - best_alt_pct
            return {
                "participant_id": participant_id,
                "matched_with_id": matched_id,
                "matched_score": matched_score,
                "alternative_id": best_alt_id,
                "alternative_score": int(best_alt_pct * scale),
                "gap": int(gap * scale),
                "reason": f"Matched score ({matched_pct:.1f}%) vs alternative ({best_alt_pct:.1f}%) — gap {gap:.1f} ≤ {gap_threshold}",
            }
        return None

    # Build match lookup: mentee→mentor and mentor→mentee
    mentee_to_mentor = {}
    mentor_to_mentee = {}
    for m in matches:
        mentee_to_mentor[m["mentee_id"]] = m["mentor_id"]
        mentor_to_mentee[m["mentor_id"]] = m["mentee_id"]

    # Check each mentee
    for mentee_id in inputs.mentee_ids:
        if mentee_id in mentee_to_mentor:
            amb = _check_ambiguity(mentee_id, mentee_to_mentor[mentee_id], is_mentee=True)
            if amb:
                ambiguities.append(amb)

    # Check each mentor (skip if already recorded from mentee side)
    recorded = {(a["matched_with_id"], a["participant_id"]) for a in ambiguities}
    for mentor_id in inputs.mentor_ids:
        if mentor_id in mentor_to_mentee:
            mentee_id = mentor_to_mentee[mentor_id]
            if (mentee_id, mentor_id) not in recorded:
                amb = _check_ambiguity(mentor_id, mentee_id, is_mentee=False)
                if amb:
                    ambiguities.append(amb)

    return ambiguities


def _get_org_name(participant_id: int, inputs: PreparedInputs) -> str:
    """
    Helper to get organization name for a participant.
    """
    return inputs.participant_orgs.get(participant_id, "Unknown Organization")
