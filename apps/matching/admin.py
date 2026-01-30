from django.contrib import admin
from .models import Preference, MentorProfile, MenteeProfile, ImportJob


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "from_participant",
        "to_participant",
        "rank",
    )
    list_filter = (
        "from_participant__cohort",
        "from_participant__role_in_cohort",
    )
    search_fields = (
        "from_participant__display_name",
        "to_participant__display_name",
    )
    ordering = (
        "from_participant__cohort",
        "from_participant",
        "rank",
    )


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "participant",
        "job_title",
        "function",
        "location",
        "years_experience",
    )
    list_filter = (
        "participant__cohort",
        "function",
        "location",
    )
    search_fields = (
        "participant__display_name",
        "participant__user__email",
        "job_title",
        "function",
        "expertise_tags",
    )
    ordering = ("participant__cohort", "participant__display_name")


@admin.register(MenteeProfile)
class MenteeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "participant",
        "get_desired_attributes_count",
    )
    search_fields = (
        "participant__display_name",
        "participant__user__email",
    )
    ordering = ("participant__cohort", "participant__display_name")

    def get_desired_attributes_count(self, obj):
        return len(obj.desired_attributes)
    get_desired_attributes_count.short_description = "Desired Attributes Count"


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "total_rows",
        "processed_rows",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
