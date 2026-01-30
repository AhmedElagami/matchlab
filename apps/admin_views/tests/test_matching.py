"""Integration tests for admin matching views."""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, PairScore


class AdminMatchingViewTest(TestCase):
    """Test cases for admin matching views."""

    def setUp(self):
        """Set up test data."""
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        self.client = Client()
        self.client.login(username="admin", password="adminpass123")
        
        # Create cohort
        self.cohort = Cohort.objects.create(name="Test Cohort", status="OPEN")
        
        # Create users
        self.mentor1_user = User.objects.create_user(
            username="mentor1", email="mentor1@example.com", password="testpass123"
        )
        self.mentor2_user = User.objects.create_user(
            username="mentor2", email="mentor2@example.com", password="testpass123"
        )
        self.mentee1_user = User.objects.create_user(
            username="mentee1", email="mentee1@example.com", password="testpass123"
        )
        self.mentee2_user = User.objects.create_user(
            username="mentee2", email="mentee2@example.com", password="testpass123"
        )
        
        # Create participants
        self.mentor1 = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentor1_user,
            role_in_cohort="MENTOR",
            display_name="M1",
            organization="OrgA",
            is_submitted=True,
        )
        self.mentor2 = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentor2_user,
            role_in_cohort="MENTOR",
            display_name="M2",
            organization="OrgB",
            is_submitted=True,
        )
        self.mentee1 = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentee1_user,
            role_in_cohort="MENTEE",
            display_name="T1",
            organization="OrgB",
            is_submitted=True,
        )
        self.mentee2 = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentee2_user,
            role_in_cohort="MENTEE",
            display_name="T2",
            organization="OrgA",
            is_submitted=True,
        )
        
        # Create mutual preferences for feasible matching
        Preference.objects.create(
            from_participant=self.mentor1, to_participant=self.mentee1, rank=1
        )
        Preference.objects.create(
            from_participant=self.mentee1, to_participant=self.mentor1, rank=1
        )
        Preference.objects.create(
            from_participant=self.mentor2, to_participant=self.mentee2, rank=1
        )
        Preference.objects.create(
            from_participant=self.mentee2, to_participant=self.mentor2, rank=1
        )
        
        # Create pair scores
        PairScore.objects.create(
            cohort=self.cohort, mentor=self.mentor1, mentee=self.mentee1, score=90.0
        )
        PairScore.objects.create(
            cohort=self.cohort, mentor=self.mentor2, mentee=self.mentee2, score=85.0
        )

    def test_run_matching_view_get(self):
        """Test that run matching page loads correctly."""
        url = reverse("admin_views:run_matching", kwargs={"cohort_id": self.cohort.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Run Matching")
        self.assertContains(response, self.cohort.name)
        # Check for data-testid attributes
        self.assertContains(response, 'data-testid="mode-strict-radio"')
        self.assertContains(response, 'data-testid="run-strict-btn"')

    def test_run_matching_view_post_strict_success(self):
        """Test that running strict matching works and redirects to results."""
        url = reverse("admin_views:run_matching", kwargs={"cohort_id": self.cohort.id})
        response = self.client.post(url, {"mode": "STRICT"})
        
        # Should redirect to results page
        self.assertEqual(response.status_code, 302)
        
        # Get the match run ID from the redirect URL
        redirect_url = response.url
        self.assertIn("/results/", redirect_url)
        
    def test_match_results_view(self):
        """Test that match results page loads with data."""
        # First run matching to create a match run
        from apps.matching.services import run_strict_matching
        match_run = run_strict_matching(self.cohort, self.admin_user)
        
        url = reverse("admin_views:match_results", kwargs={"match_run_id": match_run.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Match Results")
        self.assertContains(response, f"Run #{match_run.id}")
        # Check for data-testid attributes
        self.assertContains(response, 'data-testid="results-table"')
        self.assertContains(response, 'data-testid="filter-ambiguous-toggle"')
        self.assertContains(response, 'data-testid="export-csv-btn"')

    def test_export_match_run_view(self):
        """Test that CSV export works."""
        # First run matching to create a match run
        from apps.matching.services import run_strict_matching
        match_run = run_strict_matching(self.cohort, self.admin_user)
        
        url = reverse("admin_views:export_match_run", kwargs={"match_run_id": match_run.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment;", response["Content-Disposition"])
        content = response.content.decode("utf-8")
        self.assertIn("mentor_name", content)
        self.assertIn("mentee_name", content)
