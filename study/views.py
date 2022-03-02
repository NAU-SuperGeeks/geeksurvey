from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from geeksurvey.models import Study, Profile, User

from datetime import datetime, timedelta

from .forms import *

def study_update_helper(request, study, study_form):
    title      = study_form.cleaned_data['title']
    descr      = study_form.cleaned_data['description']
    code       = study_form.cleaned_data['completion_code']
    survey     = study_form.cleaned_data['survey_url']
    comp       = study_form.cleaned_data['compensation']
    min_age    = study_form.cleaned_data['min_age']
    max_age    = study_form.cleaned_data['max_age']
    min_yoe    = study_form.cleaned_data['min_yoe']
    max_yoe    = study_form.cleaned_data['max_yoe']
    req_edu    = study_form.cleaned_data['req_edu']
    req_job    = study_form.cleaned_data['req_job']
    req_rne    = study_form.cleaned_data['req_rne']
    req_sex    = study_form.cleaned_data['req_sex']
    req_oss    = study_form.cleaned_data['req_oss']
    study.owner           = request.user
    study.title           = title
    study.description     = descr
    study.completion_code = code
    study.survey_url      = survey
    study.compensation    = comp
    study.min_age         = min_age
    study.max_age         = max_age
    study.min_yoe         = min_yoe
    study.max_yoe         = max_yoe
    study.req_edu         = req_edu
    study.req_job         = req_job
    study.req_rne         = req_rne
    study.req_sex         = req_sex
    study.req_oss         = req_oss
    study.last_modified   = datetime.now()
    study.expiry_date     = datetime.now()+timedelta(days=365)
    study.save()

def study_custom_labels(study_form):
    study_form['compensation'].label = "Compensation (USD)"
    study_form['survey_url'].label = "Survey URL"
    study_form['min_age'].label = "Minimum Age for Participants"
    study_form['max_age'].label = "Maximum Age for Participants"
    study_form['min_yoe'].label = "Minimum Years of Experience"
    study_form['max_yoe'].label = "Maximum Years of Experience"
    study_form['req_edu'].label = "Required Education"
    study_form['req_job'].label = "Required Occupation"
    study_form['req_rne'].label = "Required Race / Ethnicity"
    study_form['req_sex'].label = "Required Gender"
    study_form['req_oss'].label = "Require Experience With Open Source Development?"

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
            return redirect('research')
    else:
        study_form = StudyUpdateForm(instance=study)

        # define custom labels for the form
        study_custom_labels(study_form)

        context={'profile':profile,
                'study_form':study_form}
        return render(request, 'study/update.html', context)

@login_required
def study_funds(request, study_id):
    study = Study.objects.get(id=study_id)
    if (request.user != study.owner):
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

def send_mail_to_users(request, users, study):

    emails = []
    study_id = study.id
    for user in users:
        emails.append(user.email)
    print(emails)
    try:
        email_param = {
            'subject': 'New Study on GeekSurvey',
            'message': '',
            'html_message':
                f"""
                    <h2>You are eligable for a study at GeekSurvey!</h2>
                    <p>Follow this link to the Survey:</p>
                    <a href="{request.build_absolute_uri(reverse('study_landing_page',
                                                                 args=(study_id,)))}">Click here to participate</a>

                """,
            'from_email': EMAIL_HOST_USER,
            'recipient_list':emails,
        }
        res_mail = send_mail(**email_param)
    except Exception as e:
        print(e)


@login_required
def study_create(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        study_form = StudyUpdateForm(request.POST, instance=request.user)
        if study_form.is_valid():
            study = Study()
            study_update_helper(request, study, study_form)

            # collect all eligible users
            all_users = User.objects.all()
            eligible_users = []
            for user in all_users:
                user_profile = Profile.objects.get(user=user)
                if user_profile.can_enroll(study):
                    eligible_users.append(user)

            send_mail_to_users(request, eligible_users, study)

            messages.success(request, f'Your study has been created!')
            return redirect('research')
    else:
        study_form = StudyUpdateForm(instance=Study())

        # define custom labels for the form
        study_custom_labels(study_form)

        context={'profile':profile,
                 'study_form':study_form}
        return render(request, 'study/update.html', context)

@login_required
def study_delete(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    owner_profile = Profile.objects.get(user=study.owner)

    if request.method == 'POST':
        study.delete()
        return redirect('research')

    context ={
        'user':request.user,
        'study':study,
        'owner_profile':owner_profile
        }

    return render(request, 'study/delete.html', context)

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

        # assert study has proper funds
        if study.balance < study.compensation:
            # TODO use messages to show user why they couldn't complete
            # exit before completing
            return redirect('study_landing_page', study_id)

        complete_form = StudyCompleteForm(request.POST)

        if complete_form.is_valid():
            code_input = complete_form.cleaned_data['completion_code']
            if code_input == study.completion_code:
                profile = Profile.objects.get(user=request.user)

                study.balance = round(float(study.balance) - float(study.compensation), 2)
                profile.balance = round(float(profile.balance) + float(study.compensation), 2)

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
