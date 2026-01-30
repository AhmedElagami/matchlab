import io
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.core.models import Cohort, Participant
from apps.matching.models import MentorProfile
from django.contrib.auth.models import User
from ..forms import CSVImportForm, MenteeDesiredAttributesForm, MentorCSVParser


class CSVImportFormTest(TestCase):
    def test_csv_import_form_valid(self):
        """Test that the CSV import form is valid with a CSV file."""
        csv_content = b"test,data\n1,2"
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
        form = CSVImportForm(files={"csv_file": csv_file})
        self.assertTrue(form.is_valid())

    def test_csv_import_form_invalid_extension(self):
        """Test that the CSV import form is invalid with a non-CSV file."""
        txt_content = b"test data"
        txt_file = SimpleUploadedFile("test.txt", txt_content, content_type="text/plain")
        form = CSVImportForm(files={"csv_file": txt_file})
        self.assertFalse(form.is_valid())


class MenteeDesiredAttributesFormTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user("testuser", "test@example.com", "pass")
        self.cohort = Cohort.objects.create(name="Test Cohort")
        self.participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTEE",
            display_name="Test Mentee"
        )

    def test_mentee_desired_attributes_form_valid(self):
        """Test that the mentee desired attributes form is valid."""
        form_data = {
            "desired_tags": "backend,python",
            "notes": "Looking for experienced mentor",
            "desired_attr_same_organization_ok": True,
            "desired_attr_remote_ok": False,
            "desired_attr_industry_experience_required": True,
        }
        form = MenteeDesiredAttributesForm(data=form_data, participant=self.participant)
        self.assertTrue(form.is_valid())

    def test_mentee_desired_attributes_form_empty_valid(self):
        """Test that the mentee desired attributes form is valid when empty."""
        form_data = {}
        form = MenteeDesiredAttributesForm(data=form_data, participant=self.participant)
        self.assertTrue(form.is_valid())


class MentorCSVParserTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user("mentor1", "mentor1@example.com", "pass")
        self.cohort = Cohort.objects.create(name="Test Cohort")
        self.participant = Participant.objects.create(
            cohort=self.cohort,
            user=self.user,
            role_in_cohort="MENTOR",
            display_name="Test Mentor",
            organization="Test Org"
        )

    def test_parser_valid_csv(self):
        """Test parsing a valid CSV."""
        csv_content = (
            "mentor_email,organization,job_title,function,expertise_tags,"
            "languages,location,years_experience,coaching_topics,bio\n"
            "mentor1@example.com,Test Org,Engineer,Engineering,backend,EN,NYC,5,leadership,Experienced\n"
        )
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode(), content_type="text/csv")
        
        parser = MentorCSVParser(csv_file)
        result = parser.parse()
        
        self.assertTrue(result)
        self.assertEqual(len(parser.valid_rows), 1)
        self.assertEqual(len(parser.invalid_rows), 0)

    def test_parser_invalid_email(self):
        """Test parsing CSV with invalid email."""
        csv_content = (
            "mentor_email,organization,job_title,function,expertise_tags,"
            "languages,location,years_experience,coaching_topics,bio\n"
            "invalid-email,Test Org,Engineer,Engineering,backend,EN,NYC,5,leadership,Experienced\n"
        )
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode(), content_type="text/csv")
        
        parser = MentorCSVParser(csv_file)
        result = parser.parse()
        
        self.assertTrue(result)  # Parser itself is valid
        self.assertEqual(len(parser.valid_rows), 0)
        self.assertEqual(len(parser.invalid_rows), 1)
        self.assertIn("No mentor found with email invalid-email", parser.invalid_rows[0]["_errors"])

    def test_parser_missing_organization(self):
        """Test parsing CSV with missing organization."""
        csv_content = (
            "mentor_email,organization,job_title,function,expertise_tags,"
            "languages,location,years_experience,coaching_topics,bio\n"
            "mentor1@example.com,,Engineer,Engineering,backend,EN,NYC,5,leadership,Experienced\n"
        )
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode(), content_type="text/csv")
        
        parser = MentorCSVParser(csv_file)
        result = parser.parse()
        
        self.assertTrue(result)  # Parser itself is valid
        self.assertEqual(len(parser.valid_rows), 0)
        self.assertEqual(len(parser.invalid_rows), 1)
        self.assertIn("Organization is required", parser.invalid_rows[0]["_errors"])

    def test_parser_invalid_years_experience(self):
        """Test parsing CSV with invalid years_experience."""
        csv_content = (
            "mentor_email,organization,job_title,function,expertise_tags,"
            "languages,location,years_experience,coaching_topics,bio\n"
            "mentor1@example.com,Test Org,Engineer,Engineering,backend,EN,NYC,abc,leadership,Experienced\n"
        )
        csv_file = SimpleUploadedFile("test.csv", csv_content.encode(), content_type="text/csv")
        
        parser = MentorCSVParser(csv_file)
        result = parser.parse()
        
        self.assertTrue(result)  # Parser itself is valid
        self.assertEqual(len(parser.valid_rows), 0)
        self.assertEqual(len(parser.invalid_rows), 1)
        self.assertIn("Years of experience must be a number", parser.invalid_rows[0]["_errors"])
