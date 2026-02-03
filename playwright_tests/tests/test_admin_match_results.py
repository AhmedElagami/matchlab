"""Playwright tests for admin match results page."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.matching.models import MatchRun, Match
from apps.core.models import Participant


@pytest.mark.django_db
def test_admin_match_results_page_displays_correctly(
    page, live_server, admin_user, test_cohort
):
    """Test that admin match results page displays correctly with all UI elements."""
    # Create a match run
    match_run = MatchRun.objects.create(
        cohort=test_cohort,
        created_by=admin_user,
        mode="STRICT",
        status="SUCCESS",
        objective_summary={
            "total_score": 85.5,
            "avg_score": 85.5,
            "match_count": 1,
            "ambiguity_count": 0,
            "solve_time": 0.1,
            "total_duration": 0.5,
        },
    )

    # Navigate to login page
    page.goto(f"{live_server.url}/auth/login/")

    # Login as admin
    page.fill("[data-testid='login-username']", "admin")
    page.fill("[data-testid='login-password']", "testpass123")
    page.click("[data-testid='login-button']")

    # Navigate to match results page
    results_url = reverse(
        "admin_views:match_results", kwargs={"match_run_id": match_run.id}
    )
    page.goto(f"{live_server.url}{results_url}")

    # Check that page loads correctly
    assert page.locator("h2").text_content() == f"Match Results - Run #{match_run.id}"

    # Check that export dropdown exists
    assert page.locator("[data-testid='export-dropdown-btn']").is_visible()

    # Check that filter checkboxes exist
    assert page.locator("[data-testid='filter-ambiguous-toggle']").is_visible()
    assert page.locator("[data-testid='filter-exceptions-toggle']").is_visible()
    assert page.locator("[data-testid='search-toggle']").is_visible()

    # Check that duration is displayed
    assert "0.50s" in page.text_content("body")


@pytest.mark.django_db
def test_admin_match_results_filters_work(page, live_server, admin_user, test_cohort):
    """Test that admin match results filters work correctly."""
    # Create a match run with matches
    match_run = MatchRun.objects.create(
        cohort=test_cohort,
        created_by=admin_user,
        mode="STRICT",
        status="SUCCESS",
        objective_summary={
            "total_score": 85.5,
            "avg_score": 85.5,
            "match_count": 2,
            "ambiguity_count": 1,
            "solve_time": 0.1,
            "total_duration": 0.5,
        },
    )

    # Create matches - one ambiguous, one normal
    mentor1 = Participant.objects.create(
        user=User.objects.create_user(
            username="m1", email="m1@test.com", password="testpass123"
        ),
        cohort=test_cohort,
        display_name="Mentor 1",
        role_in_cohort="MENTOR",
        organization="Org A",
        is_submitted=True,
    )
    mentor2 = Participant.objects.create(
        user=User.objects.create_user(
            username="m2", email="m2@test.com", password="testpass123"
        ),
        cohort=test_cohort,
        display_name="Mentor 2",
        role_in_cohort="MENTOR",
        organization="Org B",
        is_submitted=True,
    )

    mentee1 = Participant.objects.create(
        user=User.objects.create_user(
            username="t1", email="t1@test.com", password="testpass123"
        ),
        cohort=test_cohort,
        display_name="Mentee 1",
        role_in_cohort="MENTEE",
        organization="Org B",
        is_submitted=True,
    )

    mentee2 = Participant.objects.create(
        user=User.objects.create_user(
            username="t2", email="t2@test.com", password="testpass123"
        ),
        cohort=test_cohort,
        display_name="Mentee 2",
        role_in_cohort="MENTEE",
        organization="Org C",
        is_submitted=True,
    )

    # Create one ambiguous match and one normal match
    Match.objects.create(
        match_run=match_run,
        mentor=mentor1,
        mentee=mentee1,
        score_percent=85,
        ambiguity_flag=True,
        ambiguity_reason="Close scores",
        exception_flag=False,
    )

    Match.objects.create(
        match_run=match_run,
        mentor=mentor2,
        mentee=mentee2,
        score_percent=75,
        ambiguity_flag=False,
        exception_flag=False,
    )

    # Navigate to login page
    page.goto(f"{live_server.url}/auth/login/")

    # Login as admin
    page.fill("[data-testid='login-username']", "admin")
    page.fill("[data-testid='login-password']", "testpass123")
    page.click("[data-testid='login-button']")

    # Navigate to match results page
    results_url = reverse(
        "admin_views:match_results", kwargs={"match_run_id": match_run.id}
    )
    page.goto(f"{live_server.url}{results_url}")

    # Check initial count
    assert "2 matches displayed" in page.text_content("[data-testid='match-count']")

    # Enable ambiguous filter
    page.check("[data-testid='filter-ambiguous-toggle']")

    # Check that only one match is displayed
    assert "1 matches displayed" in page.text_content("[data-testid='match-count']")

    # Disable ambiguous filter and enable search
    page.uncheck("[data-testid='filter-ambiguous-toggle']")
    page.check("[data-testid='search-toggle']")
    page.fill("[data-testid='search-input']", "Mentee 1")

    # Check that only one match is displayed
    assert "1 matches displayed" in page.text_content("[data-testid='match-count']")

    # Clear search
    page.fill("[data-testid='search-input']", "")

    # Check that both matches are displayed again
    assert "2 matches displayed" in page.text_content("[data-testid='match-count']")


@pytest.mark.django_db
def test_admin_match_results_export_options(page, live_server, admin_user, test_cohort):
    """Test that export options are available and functional."""
    # Create a match run
    match_run = MatchRun.objects.create(
        cohort=test_cohort,
        created_by=admin_user,
        mode="STRICT",
        status="SUCCESS",
        objective_summary={
            "total_score": 85.5,
            "avg_score": 85.5,
            "match_count": 1,
            "ambiguity_count": 0,
            "solve_time": 0.1,
            "total_duration": 0.5,
        },
    )

    # Navigate to login page
    page.goto(f"{live_server.url}/auth/login/")

    # Login as admin
    page.fill("[data-testid='login-username']", "admin")
    page.fill("[data-testid='login-password']", "testpass123")
    page.click("[data-testid='login-button']")

    # Navigate to match results page
    results_url = reverse(
        "admin_views:match_results", kwargs={"match_run_id": match_run.id}
    )
    page.goto(f"{live_server.url}{results_url}")

    # Click export dropdown
    page.click("[data-testid='export-dropdown-btn']")

    # Check that both export options are available
    assert page.locator("[data-testid='export-csv-btn']").is_visible()
    assert page.locator("[data-testid='export-xlsx-btn']").is_visible()
