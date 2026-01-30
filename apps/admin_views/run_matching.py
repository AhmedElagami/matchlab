"""Admin views for running matching."""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from apps.core.models import Cohort
from apps.matching.models import MatchRun
from apps.matching.services import run_strict_matching, export_match_run_csv

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is admin/staff."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def run_matching_view(request, cohort_id):
    """View for running matching algorithms."""
    cohort = get_object_or_404(Cohort, id=cohort_id)
    
    if request.method == 'POST':
        mode = request.POST.get('mode', 'STRICT')
        
        if mode == 'STRICT':
            # Run strict matching
            match_run = run_strict_matching(cohort, request.user)
            
            if match_run.status == 'SUCCESS':
                messages.success(request, 'Strict matching completed successfully!')
                return redirect('admin_views:match_results', match_run_id=match_run.id)
            else:
                messages.error(request, f'Strict matching failed: {match_run.failure_report.get("message", "Unknown error")}')
                return render(request, 'admin_views/run_matching.html', {
                    'cohort': cohort,
                    'match_run': match_run,
                })
        else:
            messages.error(request, f'Unsupported mode: {mode}')
            return redirect('admin_views:run_matching', cohort_id=cohort_id)
    
    # GET request - show run matching page
    # Get recent match runs for this cohort
    recent_runs = MatchRun.objects.filter(cohort=cohort).order_by('-created_at')[:10]
    
    return render(request, 'admin_views/run_matching.html', {
        'cohort': cohort,
        'recent_runs': recent_runs,
    })


@login_required
@user_passes_test(is_admin)
def match_results_view(request, match_run_id):
    """View for displaying match results."""
    match_run = get_object_or_404(MatchRun, id=match_run_id)
    
    # Verify user has access to this cohort
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    # Get matches
    matches = match_run.matches.select_related('mentor', 'mentee').all()
    
    # Stats
    total_matches = matches.count()
    ambiguous_count = matches.filter(ambiguity_flag=True).count()
    exception_count = matches.filter(exception_flag=True).count()
    
    return render(request, 'admin_views/match_results.html', {
        'match_run': match_run,
        'matches': matches,
        'total_matches': total_matches,
        'ambiguous_count': ambiguous_count,
        'exception_count': exception_count,
    })


@login_required
@user_passes_test(is_admin)
def export_match_run_view(request, match_run_id):
    """Export match run results as CSV."""
    match_run = get_object_or_404(MatchRun, id=match_run_id)
    
    # Verify user has access to this cohort
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    if match_run.status != 'SUCCESS':
        messages.error(request, 'Cannot export failed match run.')
        return redirect('admin_views:match_results', match_run_id=match_run_id)
    
    # Generate CSV
    csv_content = export_match_run_csv(match_run)
    
    # Create response
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="match_results_{match_run.id}.csv"'
    
    return response
