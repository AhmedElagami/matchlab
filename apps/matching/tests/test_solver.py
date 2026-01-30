"""Tests for the OR-Tools solver functionality."""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from apps.core.models import Cohort, Participant
from apps.matching.models import Preference, PairScore, MatchRun, Match
from apps.matching.solver import solve_strict, detect_ambiguity
from apps.matching.services import run_strict_matching, export_match_run_csv


class SolverTest(TestCase):
    """Test cases for the OR-Tools solver."""

    def setUp(self):
        """Set up test data."""
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
        PairScore.objects.create(
            cohort=self.cohort, mentor=self.mentor1, mentee=self.mentee2, score=70.0
        )
        PairScore.objects.create(
            cohort=self.cohort, mentor=self.mentor2, mentee=self.mentee1, score=65.0
        )

    def test_solve_strict_success(self):
        """Test that strict solver produces feasible assignment when exists."""
        mentors = [self.mentor1, self.mentor2]
        mentees = [self.mentee1, self.mentee2]
        
        success, result = solve_strict(mentors, mentees, self.cohort)
        
        self.assertTrue(success)
        self.assertIn("matches", result)
        self.assertEqual(len(result["matches"]), 2)
        self.assertGreater(result["total_score"], 0)
        
        # Check that we got the optimal matches (highest scores)
        match_pairs = [(m["mentor"].id, m["mentee"].id) for m in result["matches"]]
        expected_pairs = [(self.mentor1.id, self.mentee1.id), (self.mentor2.id, self.mentee2.id)]
        
        for pair in expected_pairs:
            self.assertIn(pair, match_pairs)

    def test_detect_ambiguity_no_ambiguity(self):
        """Test ambiguity detection with clear score gaps."""
        matches = [
            {
                "mentor": self.mentor1,
                "mentee": self.mentee1,
                "score": 90.0,
            },
            {
                "mentor": self.mentor2,
                "mentee": self.mentee2,
                "score": 85.0,
            },
        ]
        
        mentors = [self.mentor1, self.mentor2]
        mentees = [self.mentee1, self.mentee2]
        
        # Create scores with large gaps
        scores = {
            (self.mentor1.id, self.mentee1.id): 90.0,
            (self.mentor1.id, self.mentee2.id): 50.0,  # Large gap
            (self.mentor2.id, self.mentee2.id): 85.0,
            (self.mentor2.id, self.mentee1.id): 40.0,  # Large gap
        }
        
        ambiguities = detect_ambiguity(matches, mentors, mentees, scores, gap_threshold=10.0)
        
        # Should have no ambiguities due to large gaps
        self.assertEqual(len(ambiguities), 0)

    def test_detect_ambiguity_with_ambiguity(self):
        """Test ambiguity detection with small score gaps."""
        matches = [
            {
                "mentor": self.mentor1,
                "mentee": self.mentee1,
                "score": 90.0,
            },
            {
                "mentor": self.mentor2,
                "mentee": self.mentee2,
                "score": 85.0,
            },
        ]
        
        mentors = [self.mentor1, self.mentor2]
        mentees = [self.mentee1, self.mentee2]
        
        # Create scores with small gaps
        scores = {
            (self.mentor1.id, self.mentee1.id): 90.0,
            (self.mentor1.id, self.mentee2.id): 88.0,  # Small gap
            (self.mentor2.id, self.mentee2.id): 85.0,
            (self.mentor2.id, self.mentee1.id): 82.0,  # Small gap
        }
        
        ambiguities = detect_ambiguity(matches, mentors, mentees, scores, gap_threshold=5.0)
        
        # Should have ambiguities due to small gaps
        self.assertGreater(len(ambiguities), 0)


class ServiceTest(TestCase):
    """Test cases for matching services."""

    def setUp(self):
        """Set up test data."""
        # Create cohort
        self.cohort = Cohort.objects.create(name="Test Cohort", status="OPEN")
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        
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

    def test_run_strict_matching_success(self):
        """Test that run_strict_matching creates MatchRun and Matches."""
        match_run = run_strict_matching(self.cohort, self.admin_user)
        
        # Check that match run was created successfully
        self.assertEqual(match_run.status, "SUCCESS")
        self.assertEqual(match_run.mode, "STRICT")
        self.assertEqual(match_run.cohort, self.cohort)
        self.assertEqual(match_run.created_by, self.admin_user)
        
        # Check that matches were created
        matches = Match.objects.filter(match_run=match_run)
        self.assertEqual(matches.count(), 2)
        
        # Check match details
        match1 = matches.get(mentor=self.mentor1)
        match2 = matches.get(mentor=self.mentor2)
        
        self.assertEqual(match1.mentee, self.mentee1)
        self.assertEqual(match1.score_percent, 90)
        self.assertEqual(match2.mentee, self.mentee2)
        self.assertEqual(match2.score_percent, 85)
        
        # Check that objective summary is populated
        self.assertIn("match_count", match_run.objective_summary)
        self.assertIn("total_score", match_run.objective_summary)
        self.assertEqual(match_run.objective_summary["match_count"], 2)

    def test_export_match_run_csv(self):
        """Test that match run CSV export contains correct data."""
        # First run a successful matching
        match_run = run_strict_matching(self.cohort, self.admin_user)
        
        # Export to CSV
        from apps.matching.services import export_match_run_csv
        csv_content = export_match_run_csv(match_run)
        
        # Check that CSV contains expected headers and data
        lines = csv_content.strip().split('\n')
        self.assertGreater(len(lines), 1)  # Header + at least 1 data row
        
        # Check header
        header = lines[0]
        expected_headers = [
            'mentor_name', 'mentor_email', 'mentor_org',
            'mentee_name', 'mentee_email', 'mentee_org',
            'match_percent', 'ambiguity_flag', 'ambiguity_reason',
            'exception_flag', 'exception_type', 'exception_reason'
        ]
        for expected_header in expected_headers:
            self.assertIn(expected_header, header)
        
        # Check that we have data rows
        self.assertGreater(len(lines), 1)
