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

def index(request):
    return render(request, 'home.html')

def working(request):
    return render(request, 'working.html')

def help(request):
    return render(request, 'help.html')

def participate(request):
    return render(request, 'participate/index.html')

@login_required
def part_discover(request):
    # TODO filter by criteria
    user_profile = Profile.objects.get(user=request.user)
    all_studies = Study.objects.all()
    eligible_studies = []

    for study in all_studies:
        if user_profile.can_enroll(study):
            eligible_studies.append(study)


    # (use profile.can_enroll())
    context = {
        'studies': eligible_studies,
    }
    return render(request, 'participate/discover.html', context)

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    context={'profile':profile}
    return render(request, 'profile/index.html', context)

@login_required
def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile') # Redirect back to profile page

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'profile': profile,
        'p_form': p_form
    }

    return render(request, 'profile/update.html', context)

@login_required
def research(request):
    profile = Profile.objects.get(user=request.user)

    # show existing studies created by the user
    studies = Study.objects.filter(owner=request.user)
    context = {'profile':profile,
               'studies':studies}
    return render(request, 'research/index.html', context)

def study_update_helper(request, study, study_form):
    s_title      = study_form.cleaned_data['title']
    s_descr      = study_form.cleaned_data['description']
    s_code       = study_form.cleaned_data['completion_code']
    s_survey     = study_form.cleaned_data['survey_url']
    s_comp       = study_form.cleaned_data['compensation']
    s_min_age    = study_form.cleaned_data['min_age']
    s_max_age    = study_form.cleaned_data['max_age']
    s_min_yoe    = study_form.cleaned_data['min_yoe']
    s_max_yoe    = study_form.cleaned_data['max_yoe']
    study.owner           = request.user
    study.title           = s_title
    study.description     = s_descr
    study.completion_code = s_code
    study.survey_url      = s_survey
    study.compensation    = s_comp
    study.min_age         = s_min_age
    study.max_age         = s_max_age
    study.min_yoe         = s_min_yoe
    study.max_yoe         = s_max_yoe
    study.last_modified   = datetime.now()
    study.expiry_date     = datetime.now()+timedelta(days=365)
    study.save()

@login_required
def study_edit(request, study_id):
    study = Study.objects.get(id=study_id)
    if (request.user != study.owner):
        return HttpResponse(status=401)

    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        study_form = StudyUpdateForm(request.POST, instance=request.user)
        if study_form.is_valid():
            study_update_helper(request, study, study_form)
            messages.success(request, f'Your study has been updated!')
            return redirect('research')  # TODO redirect to research dashboard or study view page
    else:
        study_form = StudyUpdateForm(instance=study)

        # define custom labels for the form
        study_form['compensation'].label = "Compensation (USD)"
        study_form['min_age'].label = "Minimum Age for Participants"
        study_form['max_age'].label = "Maximum Age for Participants"
        study_form['min_yoe'].label = "Minimum Years of Experience"
        study_form['max_yoe'].label = "Maximum Years of Experience"
        context={'profile':profile,
                'study_form':study_form}
        return render(request, 'study/update.html', context)

@login_required
def study_create(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        study_form = StudyUpdateForm(request.POST, instance=request.user)
        if study_form.is_valid():
            study = Study()
            study_update_helper(request, study, study_form)
            messages.success(request, f'Your study has been created!')
            return redirect('research')  # TODO redirect to research dashboard or study view page
    else:
        study_form = StudyUpdateForm(instance=Study())

        # define custom labels for the form
        study_form['compensation'].label = "Compensation (USD)"
        study_form['min_age'].label = "Minimum Age for Participants"
        study_form['max_age'].label = "Maximum Age for Participants"
        study_form['min_yoe'].label = "Minimum Years of Experience"
        study_form['max_yoe'].label = "Maximum Years of Experience"
        context={'profile':profile,
                 'study_form':study_form}
        return render(request, 'study/update.html', context)

def study_landing_page(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    owner_profile = Profile.objects.get(user=study.owner)
    context = {
        'user':request.user,
        'study':study,
        'owner_profile':owner_profile,
    }
    return render(request, 'study/landing.html', context)

@login_required
def study_enroll(request, study_id):
    if request.method != 'POST':
        return redirect('home')

    study = get_object_or_404(Study, pk=study_id)
    user_profile = Profile.objects.get(user=request.user)

    # enforce enrollment criteria
    '''
    if user_profile.age < study.min_age or \
       user_profile.age > study.max_age or \
       user.profile.years_of_experience < study.min_yoe or \
       user.profile.years_of_experience > study.max_yoe:
    '''
    if not user_profile.can_enroll(study):
        # TODO specify why you cant enroll.
        # if fail, go to failure page
        return redirect('study_enroll_fail', study_id)

    # if succeeed, go to study landing page
    # enroll the user
    study.enrolled.add(request.user)

    # redirect to landing page
    # TODO send to participation dashboard ?
    owner_profile = Profile.objects.get(user=study.owner)
    context = {
        'study':study,
        'owner_profile':owner_profile,
    }
    return redirect('study_landing_page', study_id)

@login_required
def study_enroll_fail(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    profile = Profile.objects.get(user=request.user)
    context = {
        'study':study,
        'profile':profile,
    }
    return render(request, 'study/enroll_fail.html', context)

@login_required
def study_complete(request, study_id):
    if request.method == 'POST':
        study = get_object_or_404(Study, pk=study_id)
        complete_form = StudyCompleteForm(request.POST)

        if complete_form.is_valid():
            code_input = complete_form.cleaned_data['completion_code']
            if code_input == study.completion_code:
                study.completed.add(request.user)
                study.save()

        return redirect('study_landing_page', study_id)
    else:
      study = get_object_or_404(Study, pk=study_id)

      # redirect if user not enrolled
      if request.user not in study.enrolled.all():
          return redirect('home')

      study.completion_code = ""  # set to none so info doesnt render for user
      complete_form = StudyCompleteForm(instance=study)
      context = {'study':study, 'complete_form':complete_form}
      return render(request, 'study/complete.html', context)
