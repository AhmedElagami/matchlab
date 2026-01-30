"""Tests for Phase 7: Manual override + active run + audit trail."""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, MatchRun, Match, ActiveMatchRun
from apps.matching.services import run_exception_matching
from apps.matching import override


class Phase7TestCase(TestCase):
    """Test cases for Phase 7 implementation."""

    def setUp(self):
        """Set up test data."""
        # Create cohort
        self.cohort = Cohort.objects.create(name="Test Cohort Phase 7")

        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123",
            is_staff=True,
        )

        # Create participants for 3x3 scenario (using same structure as phase 6 tests)
        self.users_data = [
            ("m1", "M1", "m1@test.com", "OrgA", "MENTOR"),
            ("m2", "M2", "m2@test.com", "OrgA", "MENTOR"),
            ("m3", "M3", "m3@test.com", "OrgB", "MENTOR"),
            ("t1", "T1", "t1@test.com", "OrgA", "MENTEE"),
            ("t2", "T2", "t2@test.com", "OrgB", "MENTEE"),
            ("t3", "T3", "t3@test.com", "OrgB", "MENTEE"),
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

        # Set up preferences that will result in a valid match
        Preference.objects.create(
            from_participant=self.participants["m1"],
            to_participant=self.participants["t2"],
            rank=1,
        )
        Preference.objects.create(
            from_participant=self.participants["t2"],
            to_participant=self.participants["m1"],
            rank=1,
        )

        Preference.objects.create(
            from_participant=self.participants["m2"],
            to_participant=self.participants["t3"],
            rank=1,
        )
        Preference.objects.create(
            from_participant=self.participants["t3"],
            to_participant=self.participants["m2"],
            rank=1,
        )

        Preference.objects.create(
            from_participant=self.participants["m3"],
            to_participant=self.participants["t1"],
            rank=1,
        )
        Preference.objects.create(
            from_participant=self.participants["t1"],
            to_participant=self.participants["m3"],
            rank=1,
        )

        # Run matching to create a match run
        self.match_run = run_exception_matching(self.cohort, self.admin_user)
        
        # Get the actual mentor and mentee from the match
        self.mentor = self.participants["m1"]
        self.mentee = self.participants["t2"]

    def test_validate_override_pair_valid(self):
        """Test validation of valid override pair."""
        is_valid, error_msg = override.validate_override_pair(
            self.mentor, self.mentee, self.cohort, self.match_run
        )
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_validate_override_pair_wrong_roles(self):
        """Test validation fails with wrong participant roles."""
        # Try swapping roles
        is_valid, error_msg = override.validate_override_pair(
            self.mentee, self.mentor, self.cohort, self.match_run
        )
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "First participant must be a mentor")

    def test_validate_override_pair_different_cohorts(self):
        """Test validation fails with participants from different cohorts."""
        # Create a different cohort
        other_cohort = Cohort.objects.create(name="Other Cohort")
        other_user = User.objects.create_user(
            username="other_mentor",
            email="other_mentor@test.com",
            password="testpass123",
        )
        other_mentor = Participant.objects.create(
            user=other_user,
            cohort=other_cohort,
            display_name="Other Mentor",
            role_in_cohort="MENTOR",
            organization="OrgC",
            is_submitted=True,
        )
        
        is_valid, error_msg = override.validate_override_pair(
            other_mentor, self.mentee, self.cohort, self.match_run
        )
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "Both participants must be in the same cohort")

    def test_create_manual_override_success(self):
        """Test successful creation of manual override."""
        # Create another mentee
        other_mentee_user = User.objects.create_user(
            username="mentee2",
            email="mentee2@test.com",
            password="testpass123",
        )
        other_mentee = Participant.objects.create(
            user=other_mentee_user,
            cohort=self.cohort,
            display_name="Other Mentee",
            role_in_cohort="MENTEE",
            organization="OrgC",
            is_submitted=True,
        )
        
        # Create override
        success, message, match_obj = override.create_manual_override(
            self.match_run,
            self.mentor,
            other_mentee,
            "Testing override functionality",
            self.admin_user
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Override created successfully")
        self.assertIsNotNone(match_obj)
        self.assertTrue(match_obj.is_manual_override)
        self.assertEqual(match_obj.override_reason, "Testing override functionality")

    def test_create_manual_override_requires_reason_for_exception(self):
        """Test that override requires reason when creating exception."""
        # Create another mentee from same org (will create exception)
        same_org_mentee_user = User.objects.create_user(
            username="mentee_same_org",
            email="mentee_same_org@test.com",
            password="testpass123",
        )
        same_org_mentee = Participant.objects.create(
            user=same_org_mentee_user,
            cohort=self.cohort,
            display_name="Same Org Mentee",
            role_in_cohort="MENTEE",
            organization="OrgA",  # Same as mentor
            is_submitted=True,
        )
        
        # Try to create override without reason
        success, message, match_obj = override.create_manual_override(
            self.match_run,
            self.mentor,
            same_org_mentee,
            "",  # No reason
            self.admin_user
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Override reason is required when creating an exception match")

    def test_set_active_match_run_success(self):
        """Test setting a match run as active."""
        success, message = override.set_active_match_run(
            self.cohort, self.match_run, self.admin_user
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Active match run set successfully")
        
        # Verify it was set
        active_run = ActiveMatchRun.objects.get(cohort=self.cohort)
        self.assertEqual(active_run.match_run, self.match_run)
        self.assertEqual(active_run.set_by, self.admin_user)

    def test_get_active_match_for_participant(self):
        """Test getting active match for a participant."""
        # First set the match run as active
        success, message = override.set_active_match_run(self.cohort, self.match_run, self.admin_user)
        self.assertTrue(success)
        
        # Get the active match
        match = override.get_active_match_for_participant(self.mentor)
        
        self.assertIsNotNone(match)
        self.assertEqual(match.mentor, self.mentor)
        self.assertEqual(match.mentee, self.mentee)

    def test_get_active_match_no_active_run(self):
        """Test getting active match when no active run exists."""
        match = override.get_active_match_for_participant(self.mentor)
        self.assertIsNone(match)