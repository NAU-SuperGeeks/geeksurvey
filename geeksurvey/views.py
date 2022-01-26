from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

from .models import Study
from .models import Profile

from .forms import *

def study_landing_page(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    owner_profile = Profile.objects.get(user=study.owner)
    context = {
        'study':study,
        'owner_profile':owner_profile,
    }
    return render(request, 'study_landing_page.html', context)


def index(request):
  '''
  example_list = Example.objects.order_by('-pub_date')[:5]
  context = {
    'example_list': example_list,
  }
  '''
  return render(request, 'home.html')

def working(request):
  return render(request, 'working.html')

def help(request):
  return render(request, 'help.html')

def participate(request):
    all_studies = Study.objects.all()
    context = {
        'all_studies': all_studies,
    }
    return render(request, 'participate.html', context)

@login_required
def profile(request):
  profile = Profile.objects.get(user=request.user)
  context={'profile':profile}
  return render(request, 'profile.html', context)

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
        p_form.save()
        messages.success(request, f'Your account has been updated!')
        return redirect('profile') # Redirect back to profile page

  else:
      u_form = UserUpdateForm(instance=request.user)
      p_form = ProfileUpdateForm(instance=request.user.profile)

  context = {
      'profile': profile,
      'u_form': u_form,
      'p_form': p_form
  }

  return render(request, 'profile_update.html', context)

@login_required
def research_dashboard(request):
  profile = Profile.objects.get(user=request.user)

  # show existing studies created by the user
  studies = Study.object.get(owner=request.user)
  context = {'profile':profile,
             'studies':studies}
  return render(request, 'research.html', context)

@login_required
def study_create(request):
  profile = Profile.objects.get(user=request.user)
  if request.method == 'POST':
    study_form = StudyUpdateForm(request.POST, instance=request.user)
    if study_form.is_valid():
      s_title  = study_form.cleaned_data['title']
      s_descr  = study_form.cleaned_data['description']
      s_code   = study_form.cleaned_data['completion_code']
      s_survey = study_form.cleaned_data['survey_url']
      s_comp   = study_form.cleaned_data['compensation']

      study = Study(owner=request.user,
                    title=s_title,
                    description=s_descr,
                    completion_code=s_code,
                    survey_url=s_survey,
                    compensation=s_comp,
                    last_modified=datetime.now(),
                    expiry_date=datetime.now()+timedelta(days=365))
      study.save()

      messages.success(request, f'Your study has been created!')
      return redirect('profile')  # TODO redirect to research dashboard or study view page
  else:
    study_form = StudyUpdateForm(instance=Study())
  context={'profile':profile,
           'study_form':study_form}
  return render(request, 'study_create.html', context)
