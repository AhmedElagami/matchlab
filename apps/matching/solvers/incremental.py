"""Incremental matching solver - matches remaining unmatched participants."""

import logging
from apps.matching.data_prep import PreparedInputs
from apps.matching.solvers.strict import solve_strict
from apps.matching.solvers.exception import solve_exception

logger = logging.getLogger(__name__)


def solve_incremental(inputs: PreparedInputs, use_exceptions: bool = False):
    """
    Solve incremental matching for unmatched participants.
    
    This solver works on a filtered set of participants (those not already matched)
    and uses either strict or exception mode logic.
    
    Args:
        inputs: PreparedInputs containing only unmatched participants
        use_exceptions: If True, use exception mode; otherwise use strict mode
        
    Returns:
        SolverResult with matches for the unmatched participants
    """
    logger.info(f"Running incremental matching with {len(inputs.mentor_ids)} mentors "
                f"and {len(inputs.mentee_ids)} mentees (exceptions={use_exceptions})")
    
    # If no unmatched participants, return empty success
    if not inputs.mentor_ids or not inputs.mentee_ids:
        from apps.matching.solvers.strict import SolverResult
        logger.info("No unmatched participants to match")
        return SolverResult(
            success=True,
            matches=[],
            total_score=0,
            avg_score=0.0,
            solve_time=0.0,
        )
    
    # Use the appropriate solver based on mode
    if use_exceptions:
        result = solve_exception(inputs)
    else:
        result = solve_strict(inputs)
    
    logger.info(f"Incremental matching completed: {len(result.matches) if result.success else 0} new matches")
    
    return result
