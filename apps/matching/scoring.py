"""Scoring engine for mentor-mentee match percentages.

Score is based purely on mutual preference rank (spec §6.2 rank component).
"""

from typing import Dict, Any, Tuple
from django.db.models import Max
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, PairScore


def compute_rank_score(rank: int, max_rank: int) -> float:
    """Compute rank score per spec §6.2: rank_score = 1 - (r-1)/max(K-1,1).

    Returns 0-100 scale. Rank 1 → 100, last rank → 0.
    """
    if rank <= 0 or max_rank <= 0:
        return 0.0
    return (1 - (rank - 1) / max(max_rank - 1, 1)) * 100


def get_max_rank(participant: Participant) -> int:
    """Get the maximum rank for a participant's preferences."""
    return Preference.objects.filter(from_participant=participant).aggregate(
        max_rank=Max("rank")
    )["max_rank"] or 0


def compute_pair_score(
    mentor: Participant, mentee: Participant, cohort: Cohort
) -> Tuple[float, Dict[str, float]]:
    """Compute match score between a mentor and mentee pair.

    Returns (overall_score, breakdown_dict) where overall_score is 0-100.
    """
    try:
        mentor_pref = Preference.objects.get(from_participant=mentor, to_participant=mentee)
        mentee_pref = Preference.objects.get(from_participant=mentee, to_participant=mentor)
    except Preference.DoesNotExist:
        return 0.0, {"mutual_acceptability": 0.0}

    mentor_rank_score = compute_rank_score(mentor_pref.rank, get_max_rank(mentor))
    mentee_rank_score = compute_rank_score(mentee_pref.rank, get_max_rank(mentee))
    overall = (mentor_rank_score + mentee_rank_score) / 2

    breakdown = {
        "mentor_rank_score": round(mentor_rank_score, 2),
        "mentee_rank_score": round(mentee_rank_score, 2),
        "overall_score": round(overall, 2),
    }
    return overall, breakdown


def compute_all_pair_scores(cohort: Cohort) -> None:
    """Compute and store scores for all mentor-mentee pairs in a cohort."""
    mentors = Participant.objects.filter(cohort=cohort, role_in_cohort="MENTOR")
    mentees = Participant.objects.filter(cohort=cohort, role_in_cohort="MENTEE")

    PairScore.objects.filter(cohort=cohort).delete()

    for mentor in mentors:
        for mentee in mentees:
            score, breakdown = compute_pair_score(mentor, mentee, cohort)
            PairScore.objects.create(
                cohort=cohort, mentor=mentor, mentee=mentee,
                score=score, score_breakdown=breakdown,
            )
