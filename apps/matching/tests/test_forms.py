from django.test import TestCase
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference
from apps.matching.forms import PreferencesForm
from django.contrib.auth.models import User


class PreferencesFormTest(TestCase):
    def setUp(self):
        # Create a cohort
        self.cohort = Cohort.objects.create(name="Test Cohort", status="OPEN")

        # Create users
        self.mentor_user = User.objects.create_user(
            username="mentor", email="mentor@example.com", password="testpass123"
        )

        self.mentee1_user = User.objects.create_user(
            username="mentee1", email="mentee1@example.com", password="testpass123"
        )

        self.mentee2_user = User.objects.create_user(
            username="mentee2", email="mentee2@example.com", password="testpass123"
        )

        # Create participants
        self.mentor = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentor_user,
            role_in_cohort="MENTOR",
            display_name="Test Mentor",
            organization="Test Org",
        )

        self.mentee1 = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentee1_user,
            role_in_cohort="MENTEE",
            display_name="Test Mentee 1",
            organization="Different Org",
        )

        self.mentee2 = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentee2_user,
            role_in_cohort="MENTEE",
            display_name="Test Mentee 2",
            organization="Another Org",
        )

        self.candidates = [self.mentee1, self.mentee2]

    def test_form_creation(self):
        """Test that the form is created with the correct fields."""
        form = PreferencesForm(participant=self.mentor, candidates=self.candidates)

        # Check that fields are created for each candidate
        self.assertIn("candidate_{}".format(self.mentee1.id), form.fields)
        self.assertIn("candidate_{}".format(self.mentee2.id), form.fields)

    def test_duplicate_rank_resolution(self):
        """Test that duplicate ranks are resolved correctly."""
        # Create form data with duplicate ranks
        form_data = {
            "candidate_{}".format(self.mentee1.id): 1,
            "candidate_{}".format(self.mentee2.id): 1,
        }

        form = PreferencesForm(
            data=form_data, participant=self.mentor, candidates=self.candidates
        )

        self.assertTrue(form.is_valid())

        # Save the form
        duplicate_warning, normalized_ranks = form.save()

        # Check that duplicate warning is True
        self.assertTrue(duplicate_warning)

        # Check that preferences were saved with resolved ranks
        preferences = Preference.objects.filter(from_participant=self.mentor)
        self.assertEqual(preferences.count(), 2)

        # Check that ranks are 1 and 2 (resolved from duplicate 1s)
        ranks = list(preferences.values_list("rank", flat=True))
        self.assertIn(1, ranks)
        self.assertIn(2, ranks)
