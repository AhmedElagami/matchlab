from django.urls import path
from . import views
from . import run_matching
from . import override_views
from . import admin_dashboard

app_name = "admin_views"

urlpatterns = [
    path("dashboard/", admin_dashboard.admin_dashboard_view, name="admin_dashboard"),
    path("import/mentor-csv/", views.import_mentor_csv_view, name="import_mentor_csv"),
    path("import/confirm/", views.confirm_import_view, name="confirm_import"),
    path(
        "download-csv-template/",
        views.download_csv_template_view,
        name="download_csv_template",
    ),
    path(
        "mentee/<int:cohort_id>/desired-attributes/",
        views.mentee_desired_attributes_view,
        name="mentee_desired_attributes",
    ),
    path(
        "cohort/<int:cohort_id>/dashboard/",
        views.cohort_dashboard_view,
        name="cohort_dashboard",
    ),
    path(
        "cohort/<int:cohort_id>/run-matching/",
        run_matching.run_matching_view,
        name="run_matching",
    ),
    path(
        "match-run/<int:match_run_id>/results/",
        run_matching.match_results_view,
        name="match_results",
    ),
    path(
        "match-run/<int:match_run_id>/export/",
        run_matching.export_match_run_view,
        name="export_match_run",
    ),
    path(
        "match-run/<int:match_run_id>/override/",
        override_views.override_view,
        name="override",
    ),
    path(
        "cohort/<int:cohort_id>/match-run/<int:match_run_id>/set-active/",
        override_views.set_active_run_view,
        name="set_active_run",
    ),
    path(
        "cohort/<int:cohort_id>/my-match/",
        override_views.my_match_view,
        name="my_match",
    ),
]
