from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Cohort, Participant
from .forms import ParticipantProfileForm, RegistrationForm
from apps.matching.models import MentorProfile, MenteeProfile


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}!")
            login(request, user)
            return redirect("core:home")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def home_view(request):
    # If user is admin/staff, redirect to admin dashboard
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_views:admin_dashboard")

    # Get all cohorts for the current user
    user_participations = Participant.objects.filter(user=request.user).select_related(
        "cohort"
    )
    cohorts = [p.cohort for p in user_participations]

    if len(cohorts) == 1:
        # If user is in only one cohort, redirect to that cohort's profile
        return redirect("core:profile", cohort_id=cohorts[0].id)
    else:
        # Show cohort selection page
        return render(request, "core/cohort_selector.html", {"cohorts": cohorts})


@login_required
def profile_view(request, cohort_id):
    cohort = get_object_or_404(Cohort, id=cohort_id)

    try:
        participant = Participant.objects.get(user=request.user, cohort=cohort)
    except Participant.DoesNotExist:
        messages.error(request, "You are not a participant in this cohort.")
        return redirect("core:home")

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "detailed":
            _save_detailed_profile(request, participant)
            messages.success(request, "Profile details updated successfully.")
            return redirect("core:profile", cohort_id=cohort_id)
        else:
            form = ParticipantProfileForm(request.POST, instance=participant)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("core:profile", cohort_id=cohort_id)
    else:
        form = ParticipantProfileForm(instance=participant)

    # Load detailed profile for template context
    mentor_profile = None
    mentee_profile = None
    if participant.role_in_cohort == "MENTOR":
        mentor_profile, _ = MentorProfile.objects.get_or_create(participant=participant)
    else:
        mentee_profile, _ = MenteeProfile.objects.get_or_create(participant=participant)

    return render(
        request,
        "core/profile.html",
        {
            "form": form,
            "cohort": cohort,
            "participant": participant,
            "mentor_profile": mentor_profile,
            "mentee_profile": mentee_profile,
        },
    )


def _save_detailed_profile(request, participant):
    """Save the detailed mentor/mentee profile from POST data."""
    if participant.role_in_cohort == "MENTOR":
        profile, _ = MentorProfile.objects.get_or_create(participant=participant)
        profile.job_title = request.POST.get("job_title", "")
        profile.function = request.POST.get("function", "")
        profile.years_experience = request.POST.get("years_experience") or None
        profile.expertise_tags = request.POST.get("expertise_tags", "")
        profile.bio = request.POST.get("bio", "")
        profile.save()
    else:
        profile, _ = MenteeProfile.objects.get_or_create(participant=participant)
        profile.job_title = request.POST.get("job_title", "")
        profile.function = request.POST.get("function", "")
        profile.years_experience = request.POST.get("years_experience") or None
        preferred = request.POST.get("preferred_expertise", "")
        profile.desired_attributes = {
            "preferred_expertise": [t.strip() for t in preferred.split(",") if t.strip()]
        }
        profile.bio = request.POST.get("bio", "")
        profile.save()
