"""Data preparation layer - isolates ORM queries from solver logic."""

import logging
from typing import Dict, List, Tuple, Set, NamedTuple
from django.db.models import Max
from apps.core.models import Participant, Cohort
from apps.matching.models import Preference, PairScore

logger = logging.getLogger(__name__)


class PreparedInputs(NamedTuple):
    """Pure data structure for solver inputs."""

    # Participant IDs
    mentor_ids: List[int]
    mentee_ids: List[int]

    # Organization constraint matrix (True if same org)
    same_org: Dict[Tuple[int, int], bool]

    # Acceptability classification matrix
    acceptability: Dict[
        Tuple[int, int], str
    ]  # Values: MUTUAL, ONE_SIDED_MENTOR_ONLY, ONE_SIDED_MENTEE_ONLY, NEITHER

    # Score matrix (scaled integers for solver)
    score: Dict[Tuple[int, int], int]

    # Configuration
    config: Dict[str, any]


def prepare_inputs(cohort: Cohort) -> PreparedInputs:
    """
    Prepare all inputs for solver from database.

    This function performs all ORM queries in a bounded number of database calls
    and returns pure data structures suitable for solver consumption.
    """
    logger.info(f"Preparing inputs for cohort {cohort.id}")

    # Get participants
    mentors = list(
        Participant.objects.filter(
            cohort=cohort, role_in_cohort="MENTOR", is_submitted=True
        )
    )
    mentees = list(
        Participant.objects.filter(
            cohort=cohort, role_in_cohort="MENTEE", is_submitted=True
        )
    )

    logger.info(f"Found {len(mentors)} mentors and {len(mentees)} mentees")

    # Extract IDs
    mentor_ids = [m.id for m in mentors]
    mentee_ids = [m.id for m in mentees]

    # Build organization matrix
    same_org = _build_same_org_matrix(mentors, mentees)

    # Build acceptability matrix
    acceptability = _build_acceptability_matrix(mentors, mentees)

    # Get scores
    score = _get_scaled_scores(mentors, mentees, cohort)

    # Configuration
    config = _get_config(cohort)

    return PreparedInputs(
        mentor_ids=mentor_ids,
        mentee_ids=mentee_ids,
        same_org=same_org,
        acceptability=acceptability,
        score=score,
        config=config,
    )


def _build_same_org_matrix(
    mentors: List[Participant], mentees: List[Participant]
) -> Dict[Tuple[int, int], bool]:
    """Build matrix indicating which pairs are in the same organization."""
    same_org = {}

    for mentor in mentors:
        for mentee in mentees:
            same_org[(mentor.id, mentee.id)] = (
                mentor.organization == mentee.organization
            )

    return same_org


def _build_acceptability_matrix(
    mentors: List[Participant], mentees: List[Participant]
) -> Dict[Tuple[int, int], str]:
    """
    Build acceptability matrix using pure logic.

    Acceptability values:
    - MUTUAL: Both participants ranked each other
    - ONE_SIDED_MENTOR_ONLY: Only mentor ranked mentee
    - ONE_SIDED_MENTEE_ONLY: Only mentee ranked mentor
    - NEITHER: Neither participant ranked the other
    """
    # Get all preferences in bulk
    all_participants = mentors + mentees
    preferences = Preference.objects.filter(from_participant__in=all_participants)

    # Build preference lookup maps
    gives_preference = {}  # participant_id -> set of preferred_participant_ids
    for pref in preferences:
        if pref.from_participant_id not in gives_preference:
            gives_preference[pref.from_participant_id] = set()
        gives_preference[pref.from_participant_id].add(pref.to_participant_id)

    # Build acceptability matrix
    acceptability = {}

    for mentor in mentors:
        for mentee in mentees:
            mentor_gives = (
                mentor.id in gives_preference
                and mentee.id in gives_preference[mentor.id]
            )
            mentee_gives = (
                mentee.id in gives_preference
                and mentor.id in gives_preference[mentee.id]
            )

            if mentor_gives and mentee_gives:
                acceptability[(mentor.id, mentee.id)] = "MUTUAL"
            elif mentor_gives and not mentee_gives:
                acceptability[(mentor.id, mentee.id)] = "ONE_SIDED_MENTOR_ONLY"
            elif not mentor_gives and mentee_gives:
                acceptability[(mentor.id, mentee.id)] = "ONE_SIDED_MENTEE_ONLY"
            else:
                acceptability[(mentor.id, mentee.id)] = "NEITHER"

    return acceptability


def _get_scaled_scores(
    mentors: List[Participant], mentees: List[Participant], cohort: Cohort
) -> Dict[Tuple[int, int], int]:
    """Get scaled scores for all mentor-mentee pairs."""
    # Get all pair scores for this cohort
    pair_scores = PairScore.objects.filter(cohort=cohort)

    # Create lookup dictionary
    score_lookup = {}
    for ps in pair_scores:
        score_lookup[(ps.mentor.id, ps.mentee.id)] = ps.score

    # Scale scores to integers for solver
    score_scale = 1000  # As defined in original solver
    scores = {}

    for mentor in mentors:
        for mentee in mentees:
            raw_score = score_lookup.get((mentor.id, mentee.id), 0.0)
            scores[(mentor.id, mentee.id)] = int(raw_score * score_scale)

    return scores


def _get_config(cohort: Cohort) -> Dict[str, any]:
    """Get configuration parameters."""
    # Default configuration values (from scoring.py)
    DEFAULT_CONFIG = {
        "rank_weight": 0.6,
        "tag_overlap_weight": 0.2,
        "attribute_match_weight": 0.2,
        "min_options_strict": 3,
        "strict_time_limit": 5,  # seconds
        "exception_time_limit": 10,  # seconds
        "penalty_org": 1000000,
        "penalty_one_sided": 100000,
        "penalty_neither": 300000,
        "score_scale": 1000,
        "ambiguity_gap_threshold": 5.0,
    }

    config = DEFAULT_CONFIG.copy()
    config.update(cohort.cohort_config)
    return config
