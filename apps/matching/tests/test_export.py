"""Tests for CSV export functionality."""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, MatchRun, Match
from apps.matching.services import run_exception_matching, export_match_run_csv


class ExportTestCase(TestCase):
    """Test cases for CSV export functionality."""

    def setUp(self):
        """Set up test data."""
        # Create cohort
        self.cohort = Cohort.objects.create(name="Test Export Cohort")

        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            is_staff=True,
        )

        # Create participants for 2x2 scenario
        self.users_data = [
            ("m1", "M1", "m1@test.com", "OrgA", "MENTOR"),
            ("m2", "M2", "m2@test.com", "OrgB", "MENTOR"),
            ("t1", "T1", "t1@test.com", "OrgB", "MENTEE"),
            ("t2", "T2", "t2@test.com", "OrgA", "MENTEE"),
        ]

        self.participants = {}
        for username, display_name, email, org, role in self.users_data:
            user = User.objects.create_user(
                username=username, email=email, password="testpass123"
            )
            participant = Participant.objects.create(
                user=user,
                cohort=self.cohort,
                display_name=display_name,
                role_in_cohort=role,
                organization=org,
                is_submitted=True,
            )
            self.participants[username] = participant

        # Set up valid preferences
        Preference.objects.create(
            from_participant=self.participants["m1"],
            to_participant=self.participants["t1"],
            rank=1,
        )
        Preference.objects.create(
            from_participant=self.participants["t1"],
            to_participant=self.participants["m1"],
            rank=1,
        )

        Preference.objects.create(
            from_participant=self.participants["m2"],
            to_participant=self.participants["t2"],
            rank=1,
        )
        Preference.objects.create(
            from_participant=self.participants["t2"],
            to_participant=self.participants["m2"],
            rank=1,
        )

        # Run matching
        self.match_run = run_exception_matching(self.cohort, self.admin_user)

    def test_csv_export_includes_audit_fields(self):
        """Test that CSV export includes all audit fields."""
        csv_content = export_match_run_csv(self.match_run)
        
        # Check that header includes our new fields
        self.assertIn("is_manual_override", csv_content)
        self.assertIn("override_reason", csv_content)
        
        # Check that it includes exception fields
        self.assertIn("exception_flag", csv_content)
        self.assertIn("exception_type", csv_content)
        self.assertIn("exception_reason", csv_content)
        
        # Check that it includes ambiguity fields
        self.assertIn("ambiguity_flag", csv_content)
        self.assertIn("ambiguity_reason", csv_content)