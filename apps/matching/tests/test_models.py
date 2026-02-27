from django.test import TestCase
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference
from django.contrib.auth.models import User


class PreferenceModelTest(TestCase):
    def setUp(self):
        # Create a cohort
        self.cohort = Cohort.objects.create(name="Test Cohort", status="OPEN")

        # Create users
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
            organization="Test Org",
        )

        self.mentee = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentee_user,
            role_in_cohort="MENTEE",
            display_name="Test Mentee",
            organization="Test Org",
        )

    def test_preference_creation(self):
        """Test that a preference can be created successfully."""
        preference = Preference.objects.create(
            from_participant=self.mentor, to_participant=self.mentee, rank=1
        )

        self.assertEqual(preference.from_participant, self.mentor)
        self.assertEqual(preference.to_participant, self.mentee)
        self.assertEqual(preference.rank, 1)
        self.assertEqual(str(preference), "Test Mentor -> Test Mentee (rank 1)")

    def test_preference_unique_constraint(self):
        """Test that the unique constraint on from_participant and to_participant works."""
        # Create first preference
        Preference.objects.create(
            from_participant=self.mentor, to_participant=self.mentee, rank=1
        )

        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(Exception):
            Preference.objects.create(
                from_participant=self.mentor, to_participant=self.mentee, rank=2
            )
