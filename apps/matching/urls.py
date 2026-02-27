from django.urls import path
from . import views

app_name = "matching"

urlpatterns = [
    path(
        "cohorts/<int:cohort_id>/preferences/",
        views.preferences_view,
        name="preferences",
    ),
    path(
        "cohorts/<int:cohort_id>/preferences/submit/",
        views.submit_preferences_view,
        name="submit_preferences",
    ),
]
