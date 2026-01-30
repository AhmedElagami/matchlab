from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("cohorts/<int:cohort_id>/profile/", views.profile_view, name="profile"),
]
