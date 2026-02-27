"""Tests for the readiness module."""

from django.test import TestCase
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference
from apps.matching.readiness import (
    check_counts_mismatch,
    check_missing_org,
    check_missing_submissions,
    check_mutual_acceptability,
    check_readiness,
    get_zero_option_participants,
    get_lowest_option_participants,
    get_org_distribution,
)
from django.contrib.auth.models import User


class ReadinessTest(TestCase):
    def setUp(self):
        # Create a cohort
        self.cohort = Cohort.objects.create(
            name="Test Cohort", status="OPEN", cohort_config={"min_options_strict": 2}
        )

        # Create users
        self.mentor_users = []
        self.mentee_users = []

        for i in range(3):
            mentor_user = User.objects.create_user(
                username=f"mentor{i}",
                email=f"mentor{i}@example.com",
                password="testpass123",
            )
            self.mentor_users.append(mentor_user)

            mentee_user = User.objects.create_user(
                username=f"mentee{i}",
                email=f"mentee{i}@example.com",
                password="testpass123",
            )
            self.mentee_users.append(mentee_user)

        # Create participants
        self.mentors = []
        self.mentees = []

        orgs = ["OrgA", "OrgB", "OrgC"]

        for i, user in enumerate(self.mentor_users):
            mentor = Participant.objects.create(
                cohort=self.cohort,
                user=user,
                role_in_cohort="MENTOR",
                display_name=f"Test Mentor {i}",
                organization=orgs[i],
                is_submitted=True,
            )
            self.mentors.append(mentor)

        for i, user in enumerate(self.mentee_users):
            mentee = Participant.objects.create(
                cohort=self.cohort,
                user=user,
                role_in_cohort="MENTEE",
                display_name=f"Test Mentee {i}",
                organization=orgs[
                    (i + 1) % 3
                ],  # Different org than corresponding mentor
                is_submitted=True,
            )
            self.mentees.append(mentee)

    def test_check_counts_mismatch_balanced(self):
        """Test counts mismatch check with balanced mentors and mentees."""
        is_ready, message = check_counts_mismatch(self.cohort)
        self.assertTrue(is_ready)
        self.assertIn("balanced", message)

    def test_check_missing_org_no_missing(self):
        """Test missing org check when all participants have organizations."""
        is_ready, message = check_missing_org(self.cohort)
        self.assertTrue(is_ready)
        self.assertIn("All participants", message)

    def test_check_missing_org_with_missing(self):
        """Test missing org check when some participants are missing organizations."""
        # Remove organization from one participant
        self.mentors[0].organization = ""
        self.mentors[0].save()

        is_ready, message = check_missing_org(self.cohort)
        self.assertFalse(is_ready)
        self.assertIn("missing organization", message)

    def test_check_missing_submissions_no_missing(self):
        """Test missing submissions check when all participants have submitted."""
        is_ready, message = check_missing_submissions(self.cohort)
        self.assertTrue(is_ready)
        self.assertIn("All participants", message)

    def test_check_missing_submissions_with_missing(self):
        """Test missing submissions check when some participants haven't submitted."""
        # Mark one participant as not submitted
        self.mentors[0].is_submitted = False
        self.mentors[0].save()

        is_ready, message = check_missing_submissions(self.cohort)
        self.assertFalse(is_ready)
        self.assertIn("haven't submitted", message)

    def test_check_mutual_acceptability_sufficient(self):
        """Test mutual acceptability check with sufficient mutual options."""
        # Create mutual preferences between all cross-org pairs
        for mentor in self.mentors:
            for mentee in self.mentees:
                # Skip same-org pairs
                if mentor.organization != mentee.organization:
                    Preference.objects.create(
                        from_participant=mentor, to_participant=mentee, rank=1
                    )
                    Preference.objects.create(
                        from_participant=mentee, to_participant=mentor, rank=1
                    )

        is_ready, message = check_mutual_acceptability(self.cohort)
        self.assertTrue(is_ready)
        self.assertIn("have at least", message)

    def test_check_readiness_all_ready(self):
        """Test overall readiness check when all checks pass."""
        # Setup data for all checks to pass
        for mentor in self.mentors:
            for mentee in self.mentees:
                if mentor.organization != mentee.organization:
                    Preference.objects.create(
                        from_participant=mentor, to_participant=mentee, rank=1
                    )
                    Preference.objects.create(
                        from_participant=mentee, to_participant=mentor, rank=1
                    )

        results = check_readiness(self.cohort)
        self.assertTrue(results["overall_ready"])
        self.assertTrue(results["counts_mismatch"]["ready"])
        self.assertTrue(results["missing_org"]["ready"])
        self.assertTrue(results["missing_submissions"]["ready"])
        self.assertTrue(results["mutual_acceptability"]["ready"])

    def test_get_zero_option_participants(self):
        """Test getting participants with zero mutual options."""
        # Only create mutual preferences for mentor0 and mentee0
        Preference.objects.create(
            from_participant=self.mentors[0], to_participant=self.mentees[0], rank=1
        )
        Preference.objects.create(
            from_participant=self.mentees[0], to_participant=self.mentors[0], rank=1
        )

        zero_options = get_zero_option_participants(self.cohort)

        # Should have participants with zero options (those other than mentor0/mentee0)
        self.assertGreater(len(zero_options), 0)

        # Check structure
        for participant_info in zero_options:
            self.assertIn("participant", participant_info)
            self.assertIn("display_name", participant_info)
            self.assertIn("role", participant_info)
            self.assertIn("organization", participant_info)
            self.assertIn("mutual_count", participant_info)

    def test_get_lowest_option_participants(self):
        """Test getting participants with lowest mutual option counts."""
        # Create different numbers of mutual preferences
        # mentor0 has 2 mutual options
        Preference.objects.create(
            from_participant=self.mentors[0], to_participant=self.mentees[0], rank=1
        )
        Preference.objects.create(
            from_participant=self.mentees[0], to_participant=self.mentors[0], rank=1
        )
        Preference.objects.create(
            from_participant=self.mentors[0], to_participant=self.mentees[1], rank=1
        )
        Preference.objects.create(
            from_participant=self.mentees[1], to_participant=self.mentors[0], rank=1
        )

        # mentor1 has 1 mutual option
        Preference.objects.create(
            from_participant=self.mentors[1], to_participant=self.mentees[0], rank=1
        )
        Preference.objects.create(
            from_participant=self.mentees[0], to_participant=self.mentors[1], rank=1
        )

        # Get lowest option participants
        lowest_options = get_lowest_option_participants(self.cohort, limit=5)

        # Should return participants sorted by mutual count
        self.assertGreater(len(lowest_options), 0)

        # Check structure
        for participant_info in lowest_options:
            self.assertIn("participant", participant_info)
            self.assertIn("display_name", participant_info)
            self.assertIn("role", participant_info)
            self.assertIn("organization", participant_info)
            self.assertIn("mutual_count", participant_info)

    def test_get_org_distribution(self):
        """Test getting organization distribution."""
        org_distribution = get_org_distribution(self.cohort)

        # Should have entries for all organizations
        self.assertIn("OrgA", org_distribution)
        self.assertIn("OrgB", org_distribution)
        self.assertIn("OrgC", org_distribution)

        # Check structure
        for org, stats in org_distribution.items():
            self.assertIn("MENTOR", stats)
            self.assertIn("MENTEE", stats)
            self.assertIn("TOTAL", stats)
