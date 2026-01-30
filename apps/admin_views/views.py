import csv
import io
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import CSVImportForm, MenteeDesiredAttributesForm, MentorCSVParser
from apps.core.models import Cohort, Participant
from apps.matching.models import MentorProfile, MenteeProfile, ImportJob


def is_admin(user):
    """Check if user is admin/staff."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def import_mentor_csv_view(request):
    """View for importing mentor data from CSV."""
    if request.method == "POST":
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]

            # Parse the CSV file
            parser = MentorCSVParser(csv_file)
            is_valid = parser.parse()

            if not is_valid:
                for error in parser.errors:
                    messages.error(request, error)
                return render(
                    request, "admin_views/import_mentor_csv.html", {"form": form}
                )

            # Store parsed data in session for confirmation step
            request.session["csv_valid_rows"] = parser.valid_rows
            request.session["csv_invalid_rows"] = parser.invalid_rows

            # Render preview
            return render(
                request,
                "admin_views/csv_preview.html",
                {
                    "valid_rows": parser.valid_rows,
                    "invalid_rows": parser.invalid_rows,
                    "form": form,
                },
            )
    else:
        form = CSVImportForm()

    return render(request, "admin_views/import_mentor_csv.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def confirm_import_view(request):
    """Confirm and process the CSV import."""
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("admin_views:import_mentor_csv")

    # Get data from session
    valid_rows = request.session.get("csv_valid_rows", [])
    invalid_rows = request.session.get("csv_invalid_rows", [])

    if not valid_rows and not invalid_rows:
        messages.error(request, "No data to import.")
        return redirect("admin_views:import_mentor_csv")

    # Process valid rows
    imported_count = 0
    for row in valid_rows:
        participant = row["participant_obj"]

        # Get or create mentor profile
        mentor_profile, created = MentorProfile.objects.get_or_create(
            participant=participant,
            defaults={
                "job_title": row.get("job_title", ""),
                "function": row.get("function", ""),
                "expertise_tags": row.get("expertise_tags", ""),
                "languages": row.get("languages", ""),
                "location": row.get("location", ""),
                "years_experience": int(row.get("years_experience"))
                if row.get("years_experience")
                else None,
                "coaching_topics": row.get("coaching_topics", ""),
                "bio": row.get("bio", ""),
            },
        )

        # If profile exists, update it
        if not created:
            mentor_profile.job_title = row.get("job_title", "")
            mentor_profile.function = row.get("function", "")
            mentor_profile.expertise_tags = row.get("expertise_tags", "")
            mentor_profile.languages = row.get("languages", "")
            mentor_profile.location = row.get("location", "")
            mentor_profile.years_experience = (
                int(row.get("years_experience"))
                if row.get("years_experience")
                else None
            )
            mentor_profile.coaching_topics = row.get("coaching_topics", "")
            mentor_profile.bio = row.get("bio", "")
            mentor_profile.save()

        imported_count += 1

    # Clean up session
    if "csv_valid_rows" in request.session:
        del request.session["csv_valid_rows"]
    if "csv_invalid_rows" in request.session:
        del request.session["csv_invalid_rows"]

    messages.success(
        request, f"Successfully imported {imported_count} mentor profiles."
    )
    return redirect("admin_views:import_mentor_csv")


@login_required
def mentee_desired_attributes_view(request, cohort_id):
    """View for mentees to set their desired mentor attributes."""
    cohort = get_object_or_404(Cohort, id=cohort_id)

    # Check if user is a participant in this cohort
    try:
        participant = Participant.objects.get(
            user=request.user, cohort=cohort, role_in_cohort="MENTEE"
        )
    except Participant.DoesNotExist:
        messages.error(request, "You are not a mentee in this cohort.")
        return redirect("core:home")

    # Get or create mentee profile
    mentee_profile, created = MenteeProfile.objects.get_or_create(
        participant=participant
    )

    if request.method == "POST":
        form = MenteeDesiredAttributesForm(request.POST, participant=participant)
        if form.is_valid():
            # Save desired attributes as JSON
            desired_attributes = {}

            # Process boolean attributes
            for field_name in form.fields:
                if field_name.startswith("desired_attr_"):
                    attr_key = field_name.replace("desired_attr_", "")
                    desired_attributes[attr_key] = form.cleaned_data.get(
                        field_name, False
                    )

            # Save to profile
            mentee_profile.desired_attributes = desired_attributes
            mentee_profile.notes = form.cleaned_data.get("notes", "")
            mentee_profile.save()

            messages.success(request, "Your preferences have been saved.")
            return redirect(
                "admin_views:mentee_desired_attributes", cohort_id=cohort_id
            )
    else:
        # Prepopulate form with existing data
        initial_data = {
            "notes": mentee_profile.notes,
        }

        # Prepopulate boolean attributes
        for attr_key, attr_value in mentee_profile.desired_attributes.items():
            initial_data[f"desired_attr_{attr_key}"] = attr_value

        form = MenteeDesiredAttributesForm(
            initial=initial_data, participant=participant
        )

    return render(
        request,
        "admin_views/mentee_desired_attributes.html",
        {
            "form": form,
            "cohort": cohort,
            "participant": participant,
        },
    )


@login_required
@user_passes_test(is_admin)
def download_csv_template_view(request):
    """Download a CSV template for mentor imports."""
    # Define the template headers
    headers = [
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

    # Create a response with CSV content
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="mentor_template.csv"'

    writer = csv.writer(response)
    writer.writerow(headers)

    # Add a sample row
    sample_row = [
        "mentor@example.com",
        "Example Corp",
        "Senior Engineer",
        "Engineering",
        "backend,python,career growth",
        "EN,ES",
        "New York",
        "10",
        "technical leadership,architecture",
        "Experienced engineer passionate about mentoring",
    ]
    writer.writerow(sample_row)

    return response
