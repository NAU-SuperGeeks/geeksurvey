from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from geeksurvey.models import Study, Profile, User

from datetime import datetime

from .forms import *
from .utils import *


@login_required
def study_edit(request, study_id):
    study = Study.objects.get(id=study_id)
    if (request.user != study.owner):
        return HttpResponse(status=401)

    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        study_form = StudyUpdateForm(request.POST, instance=study)
        if study_form.is_valid():
            study_form.save()
            return redirect('research')
    else:
        study_form = StudyUpdateForm(instance=study)

        # define custom labels for the form
        study_custom_labels(study_form)

        context={'profile':profile,
                 'study_form':study_form}
        return render(request, 'study/update.html', context)


@login_required
def study_create(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        study_form = StudyUpdateForm(request.POST)
        if study_form.is_valid():
            study = study_form.save(commit=False)
            study.owner = request.user
            study.save()

            study_send_mail(request, study)

        return redirect('research')
    else:
        study = Study()
        study_form = StudyUpdateForm(instance=study)

        # define custom labels for the form
        study_custom_labels(study_form)

        context={'profile':profile,
                 'study_form':study_form}
        return render(request, 'study/update.html', context)

@login_required
def study_participants(request, study_id):
    study = get_object_or_404(Study, pk=study_id)

    if request.user != study.owner:
        return HttpResponse(status=401)

    if request.method == 'POST':
        action = request.POST['action']
        username = request.POST['username']

        user = get_object_or_404(User, username=username)

        if action == "remove":
            if user in study.enrolled.all():
                study.enrolled.remove(user)
            if user in study.completed.all():
                study.completed.remove(user)
            if user in study.compensated.all():
                study.compensated.remove(user)

            study.save()

        elif action == "approve":
            # assert study has proper funds
            # and the user is enrolled and completed
            #   but not compensated
            if study.balance >= study.compensation and \
               user in study.enrolled.all() and \
               user in study.completed.all() and \
               user not in study.compensated.all():

                profile = get_object_or_404(Profile, user=user)

                study.balance = round(float(study.balance) - float(study.compensation), 2)
                profile.balance = round(float(profile.balance) + float(study.compensation), 2)

                study.compensated.add(user)

                study.save()
                profile.save()

    # sort participants to put actionable participants at the top
    sorted_parts = []
    all_parts = study.enrolled.all()
    for part in all_parts:
      if part in study.completed.all() and \
         part not in study.compensated.all():
          sorted_parts.append(part)
    for part in all_parts:
      if part not in sorted_parts and \
          part in study.completed.all():
          sorted_parts.append(part)
    for part in all_parts:
      if part not in sorted_parts:
          sorted_parts.append(part)

    context = { 'study':study,
                'parts':sorted_parts
              }
    return render(request, 'study/participants.html', context)


@login_required
def study_delete(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    owner_profile = Profile.objects.get(user=study.owner)

    if request.user != study.owner:
        return HttpResponse(status=401)

    if request.method == 'POST':
        study.delete()
        return redirect('research')

    context ={
        'user':request.user,
        'study':study,
        'owner_profile':owner_profile
        }

    return render(request, 'study/delete.html', context)

@login_required
def study_funds(request, study_id):
    study = Study.objects.get(id=study_id)
    if request.user != study.owner:
        return HttpResponse(status=401)

    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        funds_form = StudyFundsForm(request.POST)
        if funds_form.is_valid():

            # Negative amounts are allowed
            # they transfer money from your study to you
            # this is intentional behavior to meet requirements,
            # but should have a better UI in the future
            amount = float(funds_form.cleaned_data['amount'])
            if amount > float(profile.balance) or \
               float(study.balance) + amount < 0:
              # fail (do nothing)
              return redirect('study_funds', study_id)

            # NOTE beware anywhere that moves logical funds.
            # there could be exploits here (like overflow error)
            # that allow users to get free logical funds
            profile.balance = round(float(profile.balance) - amount, 2)
            study.balance = round(float(study.balance) + amount, 2)
            profile.save()
            study.save()

            return redirect('study_funds', study_id)
        return redirect('study_funds', study_id)
    else:
        funds_form = StudyFundsForm()

        # define custom labels for the form
        funds_form['amount'].label = "Amount (USD)"

        context={'profile':profile,
                'funds_form':funds_form,
                'study':study}

        return render(request, 'study/funds.html', context)


def study_landing_page(request, study_id):
    # TODO make a way to move funds from account to study
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
    if not user_profile.can_enroll(study):
        # if fail, go to failure page
        return redirect('study_enroll_fail', study_id)

    # if succeeed, go to study landing page
    # enroll the user
    study.enrolled.add(request.user)

    # redirect to landing page
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
                profile = Profile.objects.get(user=request.user)

                study.completed.add(request.user)
                study.save()
                profile.save()

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

