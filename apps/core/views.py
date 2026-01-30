from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Cohort, Participant
from .forms import ParticipantProfileForm


def logout_view(request):
    logout(request)
    return redirect("/auth/login/")


@login_required
def home_view(request):
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

    # Check if user is a participant in this cohort
    try:
        participant = Participant.objects.get(user=request.user, cohort=cohort)
    except Participant.DoesNotExist:
        messages.error(request, "You are not a participant in this cohort.")
        return redirect("core:home")

    if request.method == "POST":
        form = ParticipantProfileForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("core:profile", cohort_id=cohort_id)
    else:
        form = ParticipantProfileForm(instance=participant)

    return render(
        request,
        "core/profile.html",
        {
            "form": form,
            "cohort": cohort,
            "participant": participant,
        },
    )
