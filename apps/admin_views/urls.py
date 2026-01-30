from django.urls import path
from . import views

app_name = "admin_views"

urlpatterns = [
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
]
