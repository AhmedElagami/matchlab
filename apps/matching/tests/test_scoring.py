"""Tests for the scoring module."""

from django.test import TestCase
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, MentorProfile, MenteeProfile
from apps.matching.scoring import (
    compute_rank_score,
    compute_tag_overlap_score,
    compute_attribute_match_score,
    compute_pair_score,
)
from django.contrib.auth.models import User


class ScoringTest(TestCase):
    def setUp(self):
        # Create a cohort
        self.cohort = Cohort.objects.create(
            name="Test Cohort",
            status="OPEN",
            cohort_config={
                "rank_weight": 0.6,
                "tag_overlap_weight": 0.2,
                "attribute_match_weight": 0.2,
            },
        )

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
        # Rank 1 out of 5 should be 100%
        score = compute_rank_score(1, 5)
        self.assertEqual(score, 100.0)

        # Rank 3 out of 5 should be 60%
        score = compute_rank_score(3, 5)
        self.assertEqual(score, 60.0)

        # Rank 5 out of 5 should be 20% (1/5)
        score = compute_rank_score(5, 5)
        self.assertEqual(score, 20.0)

        # Edge cases
        self.assertEqual(compute_rank_score(0, 5), 0.0)
        self.assertEqual(compute_rank_score(1, 0), 0.0)

    def test_compute_tag_overlap_score(self):
        """Test tag overlap score computation."""
        # Perfect match
        mentor_tags = ["python", "django", "javascript"]
        mentee_tags = ["python", "django", "javascript"]
        score = compute_tag_overlap_score(mentor_tags, mentee_tags)
        self.assertEqual(score, 100.0)

        # Partial match
        mentor_tags = ["python", "django", "javascript"]
        mentee_tags = ["python", "react", "css"]
        score = compute_tag_overlap_score(mentor_tags, mentee_tags)
        # Intersection: {"python"}, Union: {"python", "django", "javascript", "react", "css"}
        # Jaccard: 1/5 = 0.2 = 20%
        self.assertEqual(score, 20.0)

        # No match
        mentor_tags = ["python", "django"]
        mentee_tags = ["react", "css"]
        score = compute_tag_overlap_score(mentor_tags, mentee_tags)
        self.assertEqual(score, 0.0)

        # Empty tags
        score = compute_tag_overlap_score([], ["python"])
        self.assertEqual(score, 0.0)
        score = compute_tag_overlap_score(["python"], [])
        self.assertEqual(score, 0.0)

    def test_compute_attribute_match_score(self):
        """Test attribute match score computation."""
        # Perfect match
        mentee_attrs = {"senior_level": True, "remote_work": True}
        mentor_attrs = {"senior_level": True, "remote_work": True}
        score = compute_attribute_match_score(mentee_attrs, mentor_attrs)
        self.assertEqual(score, 100.0)

        # Partial match
        mentee_attrs = {"senior_level": True, "remote_work": True, "part_time": True}
        mentor_attrs = {"senior_level": True, "remote_work": False, "part_time": True}
        score = compute_attribute_match_score(mentee_attrs, mentor_attrs)
        # 3 desired attributes, 2 match -> 66.67%
        self.assertAlmostEqual(score, 66.67, places=2)

        # No match
        mentee_attrs = {"senior_level": True, "remote_work": True}
        mentor_attrs = {"senior_level": False, "remote_work": False}
        score = compute_attribute_match_score(mentee_attrs, mentor_attrs)
        self.assertEqual(score, 0.0)

        # No desired attributes
        score = compute_attribute_match_score({}, mentor_attrs)
        self.assertEqual(score, 0.0)

    def test_compute_pair_score_no_preferences(self):
        """Test pair score computation when no preferences exist."""
        score, breakdown = compute_pair_score(self.mentor, self.mentee, self.cohort)
        self.assertEqual(score, 0.0)
        self.assertIn("mutual_acceptability", breakdown)

    def test_compute_pair_score_with_preferences(self):
        """Test pair score computation with mutual preferences."""
        # Create mutual preferences
        Preference.objects.create(
            from_participant=self.mentor, to_participant=self.mentee, rank=1
        )
        Preference.objects.create(
            from_participant=self.mentee, to_participant=self.mentor, rank=2
        )

        # Add more preferences to establish max ranks
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

        # Should have a score greater than 0
        self.assertGreater(score, 0.0)

        # Check breakdown structure
        self.assertIn("rank_score", breakdown)
        self.assertIn("tag_overlap_score", breakdown)
        self.assertIn("attribute_match_score", breakdown)
        self.assertIn("overall_score", breakdown)
