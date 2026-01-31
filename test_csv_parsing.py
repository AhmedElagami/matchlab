#!/usr/bin/env python
import os
import sys
import django
from io import StringIO, BytesIO

# Setup Django environment
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.admin_views.forms import MentorCSVParser
from apps.core.models import Participant


def test_csv_parsing():
    print("Testing CSV parsing...")

    # Read the sample CSV file
    with open("/app/sample_mentors.csv", "rb") as f:
        csv_content = f.read()

    # Create a file-like object
    csv_file = BytesIO(csv_content)
    csv_file.name = "sample_mentors.csv"

    # Parse the CSV
    parser = MentorCSVParser(csv_file)
    is_valid = parser.parse()

    print(f"Parsing result: {'Valid' if is_valid else 'Invalid'}")
    print(f"Errors: {parser.errors}")
    print(f"Valid rows: {len(parser.valid_rows)}")
    print(f"Invalid rows: {len(parser.invalid_rows)}")

    if parser.invalid_rows:
        print("\nInvalid rows details:")
        for row in parser.invalid_rows:
            print(
                f"Row #{row['row_number']} - Email: {row.get('mentor_email', 'N/A')} - Errors: {row.get('errors_list', [])}"
            )

    if parser.valid_rows:
        print("\nValid rows details:")
        for row in parser.valid_rows:
            print(
                f"Email: {row.get('mentor_email')} - Name: {row.get('participant_obj').display_name if row.get('participant_obj') else 'N/A'}"
            )


if __name__ == "__main__":
    test_csv_parsing()
