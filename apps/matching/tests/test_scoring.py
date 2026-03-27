"""Tests for the scoring module."""

from django.test import TestCase
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference
from apps.matching.scoring import (
    compute_rank_score,
    compute_pair_score,
)
from django.contrib.auth.models import User


class ScoringTest(TestCase):
    def setUp(self):
        self.cohort = Cohort.objects.create(
            name="Test Cohort",
            status="OPEN",
        )

        self.mentor_user = User.objects.create_user(
            username="mentor", email="mentor@example.com", password="testpass123"
        )
        self.mentee_user = User.objects.create_user(
            username="mentee", email="mentee@example.com", password="testpass123"
        )

        self.mentor = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentor_user,
            role_in_cohort="MENTOR",
            display_name="Test Mentor",
            organization="OrgA",
        )
        self.mentee = Participant.objects.create(
            cohort=self.cohort,
            user=self.mentee_user,
            role_in_cohort="MENTEE",
            display_name="Test Mentee",
            organization="OrgB",
        )

    def test_compute_rank_score(self):
        """Test rank score computation."""
        self.assertEqual(compute_rank_score(1, 5), 100.0)
        self.assertEqual(compute_rank_score(3, 5), 50.0)
        self.assertEqual(compute_rank_score(5, 5), 0.0)

        # Edge cases
        self.assertEqual(compute_rank_score(0, 5), 0.0)
        self.assertEqual(compute_rank_score(1, 0), 0.0)

    def test_compute_pair_score_no_preferences(self):
        """Test pair score computation when no preferences exist."""
        score, breakdown = compute_pair_score(self.mentor, self.mentee, self.cohort)
        self.assertEqual(score, 0.0)
        self.assertIn("mutual_acceptability", breakdown)

    def test_compute_pair_score_with_preferences(self):
        """Test pair score computation with mutual preferences."""
        Preference.objects.create(
            from_participant=self.mentor, to_participant=self.mentee, rank=1
        )
        Preference.objects.create(
            from_participant=self.mentee, to_participant=self.mentor, rank=2
        )

        other_mentee = Participant.objects.create(
            cohort=self.cohort,
            user=User.objects.create_user(
                username="other", email="other@example.com", password="testpass123"
            ),
            role_in_cohort="MENTEE",
            display_name="Other Mentee",
            organization="OrgC",
        )
        Preference.objects.create(
            from_participant=self.mentor, to_participant=other_mentee, rank=2
        )
        Preference.objects.create(
            from_participant=self.mentee, to_participant=other_mentee, rank=1
        )

        score, breakdown = compute_pair_score(self.mentor, self.mentee, self.cohort)
        self.assertGreater(score, 0.0)
        self.assertIn("overall_score", breakdown)
