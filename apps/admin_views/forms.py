import csv
from django import forms
from django.core.exceptions import ValidationError
from apps.core.models import Participant
from apps.matching.models import MentorProfile


class CSVImportForm(forms.Form):
    """Form for uploading CSV files."""

    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload a CSV file with mentor data",
        widget=forms.FileInput(attrs={"data-testid": "csv-upload-input"}),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get("csv_file")
        if csv_file:
            if not csv_file.name.endswith(".csv"):
                raise ValidationError("File must be a CSV file.")
        return csv_file


class MenteeDesiredAttributesForm(forms.Form):
    """Form for mentee desired attributes."""

    desired_tags = forms.CharField(
        label="Desired Expertise Tags",
        required=False,
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "data-testid": "desired-tags-input",
                "placeholder": "e.g., backend, career growth, leadership",
            }
        ),
    )

    # We'll dynamically add checkboxes for boolean attributes
    notes = forms.CharField(
        label="Additional Notes",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Any additional information about your preferred mentor...",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.participant = kwargs.pop("participant", None)
        super().__init__(*args, **kwargs)

        # Add dynamic boolean attributes as checkboxes
        # In a real implementation, these would come from a configuration or database
        boolean_attributes = [
            ("same_organization_ok", "Okay with mentor from same organization"),
            ("remote_ok", "Okay with remote mentoring"),
            ("industry_experience_required", "Prefer mentor with industry experience"),
        ]

        for attr_key, attr_label in boolean_attributes:
            self.fields[f"desired_attr_{attr_key}"] = forms.BooleanField(
                label=attr_label,
                required=False,
                widget=forms.CheckboxInput(
                    attrs={
                        "class": "form-check-input",
                        "data-testid": f"desired-attr-{attr_key}",
                    }
                ),
            )


class MentorCSVParser:
    """Parser for mentor CSV files."""

    REQUIRED_HEADERS = [
        "mentor_email",
        "organization",
        "job_title",
        "function",
        "expertise_tags",
        "languages",
        "location",
        "years_experience",
        "coaching_topics",
        "bio",
    ]

    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.errors = []
        self.valid_rows = []
        self.invalid_rows = []

    def parse(self):
        """Parse the CSV file and validate rows."""
        decoded_file = self.csv_file.read().decode("utf-8")
        reader = csv.DictReader(decoded_file.splitlines(), delimiter=",")

        # Check headers
        headers = reader.fieldnames
        if not headers:
            self.errors.append("CSV file is empty or invalid")
            return False

        missing_headers = set(self.REQUIRED_HEADERS) - set(headers)
        if missing_headers:
            self.errors.append(
                f"Missing required headers: {', '.join(missing_headers)}"
            )
            return False

        # Process rows
        for row_num, row in enumerate(
            reader, start=2
        ):  # Start at 2 because of header row
            self._validate_row(row, row_num)

        return len(self.errors) == 0

    def _validate_row(self, row, row_num):
        """Validate a single row of the CSV."""
        row_errors = []

        # Check required fields
        if not row.get("mentor_email"):
            row_errors.append("Email is required")
        elif not self._validate_email(row["mentor_email"]):
            row_errors.append("Invalid email format")

        if not row.get("organization"):
            row_errors.append("Organization is required")

        # Validate years_experience as integer
        years_exp = row.get("years_experience")
        if years_exp:
            try:
                int(years_exp)
            except ValueError:
                row_errors.append("Years of experience must be a number")

        # Try to find participant by email
        try:
            participant = Participant.objects.get(
                user__email=row["mentor_email"], role_in_cohort="MENTOR"
            )
            row["participant_obj"] = participant
        except Participant.DoesNotExist:
            row_errors.append(f"No mentor found with email {row['mentor_email']}")

        if row_errors:
            row["errors_list"] = row_errors
            row["row_number"] = row_num
            self.invalid_rows.append(row)
        else:
            self.valid_rows.append(row)

    def _validate_email(self, email):
        """Basic email validation."""
        return "@" in email and "." in email
