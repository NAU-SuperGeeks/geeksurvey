from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required

from decouple import config

from geeksurvey.settings import *
import json

from .models import Study, Profile

from .forms import *

def index(request):
    if request.user.is_authenticated:
      profile = Profile.objects.get(user=request.user)
      context = {
          'profile': profile,
        }
    else:
      context = {}
    return render(request, 'home.html', context)

def working(request):
    return render(request, 'working.html')

def help(request):
    return render(request, 'help.html')

@login_required
def participate(request):
    all_studies = Study.objects.all()
    enrolled_studies = []
    completed_studies = []
    for study in all_studies:
        if request.user in study.completed.all():
            completed_studies.append(study)
        elif request.user in study.enrolled.all():
            enrolled_studies.append(study)

    profile = Profile.objects.get(user=request.user)
    context = {
        'enrolled_studies':enrolled_studies,
        'completed_studies':completed_studies,
        'profile': profile,
      }

    return render(request, 'participate/index.html', context)

@login_required
def part_discover(request):
    user_profile = Profile.objects.get(user=request.user)
    all_studies = Study.objects.all()
    eligible_studies = []

    for study in all_studies:
        if user_profile.can_enroll(study):
            eligible_studies.append(study)

    context = {
        'studies': eligible_studies,
        'profile': user_profile,
      }
    return render(request, 'participate/discover.html', context)

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    context={'profile':profile}
    return render(request, 'profile/index.html', context)


# public profile view, accesible by url
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    context = {
        'user':user,
        'profile':profile,
      }

    return render(request, 'profile/view.html', context)

@login_required
def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            new_profile = p_form.save(commit=False)
            new_profile.updated_once = True
            new_profile.save()

            messages.success(request, f'Your account has been updated!')
            return redirect('profile') # Redirect back to profile page

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

        p_form['open_source_experience'].label = "Experienced With Open Source Development?"
        p_form['email_opt_in'].label = "Opt In For Email Notifications?"

    context = {
        'profile': profile,
        'u_form': u_form,
        'p_form': p_form
      }

    return render(request, 'profile/update.html', context)

@login_required
def research(request):
    profile = Profile.objects.get(user=request.user)

    # show existing studies created by the user
    studies = Study.objects.filter(owner=request.user)
    context = {
        'profile':profile,
        'studies':studies
      }
    return render(request, 'research/index.html', context)
