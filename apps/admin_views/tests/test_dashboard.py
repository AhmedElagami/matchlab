"""Integration tests for the cohort dashboard view."""

from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference
from django.contrib.auth.models import User


class CohortDashboardTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="userpass123"
        )

        # Create a cohort
        self.cohort = Cohort.objects.create(
            name="Test Cohort", status="OPEN", cohort_config={"min_options_strict": 2}
        )

        # Create users for participants
        self.mentor_user = User.objects.create_user(
            username="mentor", email="mentor@example.com", password="testpass123"
        )

        self.mentee_user = User.objects.create_user(
            username="mentee", email="mentee@example.com", password="testpass123"
        )

        # Create participants
        self.mentor = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentor_user,
            role_in_cohort="MENTOR",
            display_name="Test Mentor",
            organization="OrgA",
            is_submitted=True,
        )

        self.mentee = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentee_user,
            role_in_cohort="MENTEE",
            display_name="Test Mentee",
            organization="OrgB",
            is_submitted=True,
        )

        # Create mutual preferences
        Preference.objects.create(
            from_participant=self.mentor, to_participant=self.mentee, rank=1
        )
        Preference.objects.create(
            from_participant=self.mentee, to_participant=self.mentor, rank=1
        )

        # Create clients
        self.admin_client = Client()
        self.admin_client.login(username="admin", password="adminpass123")

        self.regular_client = Client()
        self.regular_client.login(username="regular", password="userpass123")

    def test_cohort_dashboard_requires_admin(self):
        """Test that cohort dashboard requires admin access."""
        url = reverse(
            "admin_views:cohort_dashboard", kwargs={"cohort_id": self.cohort.id}
        )

        # Regular user should be redirected
        response = self.regular_client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Admin user should have access
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cohort_dashboard_loads_successfully(self):
        """Test that cohort dashboard loads successfully for admin."""
        url = reverse(
            "admin_views:cohort_dashboard", kwargs={"cohort_id": self.cohort.id}
        )

        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cohort.name)

        # Check that key elements are present
        self.assertContains(response, "Readiness Status")
        self.assertContains(response, "Organization Distribution")
        self.assertContains(response, "Top Match Scores")

    def test_cohort_dashboard_has_testids(self):
        """Test that dashboard contains required data-testid attributes."""
        url = reverse(
            "admin_views:cohort_dashboard", kwargs={"cohort_id": self.cohort.id}
        )

        response = self.admin_client.get(url)

        # Check for required data-testid attributes
        self.assertContains(response, 'data-testid="readiness-status"')
        self.assertContains(response, 'data-testid="blockers-list"')
        self.assertContains(response, 'data-testid="org-distribution-table"')
