from django.contrib import admin
from .models import Cohort, Participant


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "user",
        "cohort",
        "role_in_cohort",
        "organization",
        "is_submitted",
    )
    list_filter = ("role_in_cohort", "cohort", "is_submitted")
    search_fields = ("display_name", "user__email", "organization")
    ordering = ("cohort", "role_in_cohort", "display_name")
