from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta
import smtplib
import ssl
import requests

from paypal.standard.forms import PayPalPaymentsForm
from decouple import config

from geeksurvey.settings import *
import json

from .models import Study, Profile, Payment

from .forms import *



def index(request):
    return render(request, 'home.html')

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

    context = {
        'enrolled_studies':enrolled_studies,
        'completed_studies':completed_studies,
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

    return render(request, 'profile/update.html', context)

@login_required
def profile_fund(request):
    payment = Payment(owner=request.user, amount=125)
    payment.save()
    request.session['payment-id'] = str(payment.id)

    profile = Profile.objects.get(user=request.user)

    paypal_dict = {
            # TODO get this from decouple config
            "business": config('PAYPAL_BIZ_EMAIL_P'),
            "amount": payment.amount,
            "currency_code": "USD",
            "item_name": 'Fund GeekSurvey Account',
            "invoice": str(payment.id),
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('paypal-return')),
            "cancel_return": request.build_absolute_uri(reverse('paypal-cancel')),
            "lc": 'EN',
            "no_shipping": '1',
        }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        'profile': profile,
        'form': form,
        }

    return render(request, 'profile/fund.html', context)

@login_required
def profile_claim(request):
    # GET:
    # claim.html contains a form where
    # the user enter their paypal email address
    # -
    # POST:
    # if valid email address, send payment to paypal
    # from BIZ to user_addr
    # of amount profile.balance
    # in IPN, set their balance to 0
    if request.method == 'GET':
        profile = Profile.objects.get(user=request.user)
        form    = ClaimFundsForm()
        form['email'].label = "Enter a VALID email address for your Paypal account"

        context = {
                'form': form,
                'profile': profile,
                }

        return render(request, 'profile/claim.html', context)
    elif request.method == 'POST':

        '''
        Here we manually hit Paypals REST API
        Watch out for cyber attacks!
        -
        To move this to a live payment system,
            PAYOUT_URL and TOKEN_URL must be changed
            to paypals real API instead of the
            sandbox
        '''

        form = ClaimFundsForm(request.POST)
        receiver = form['email'].value()

        PAYOUT_URL = "https://api.sandbox.paypal.com/v1/payments/payouts"
        TOKEN_URL = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

        
        CLIENT_ID = config("PAYPAL_CLIENT_ID")
        CLIENT_SECRET = config("PAYPAL_CLIENT_SECRET")


        profile = Profile.objects.get(user=request.user)


        if profile.balance < 5:
            return redirect('profile')
            
        payment = Payment(owner=request.user, amount=-1*profile.balance)
        payment.save()

        # GET ACCESS TOKEN
        headers = { 
                    "Content-Type": "application/json",
                    "Accept-Language": "en_US",
                }
        payload = {
                    "grant_type": "client_credentials",
                }

        r = requests.post(TOKEN_URL, data=payload, headers=headers, auth=(CLIENT_ID,CLIENT_SECRET))
        data = r.json()
        access_token = data['access_token']


        # SEND PAYMENT
        amount = float(profile.balance)
        payload = { 
                    "sender_batch_header":{
                        "sender_batch_id":"batch-"+str(payment.id),
                        "email_subject":"You have a GeekSurvey payout!",
                        "recipient_type":"EMAIL"
                      },
                    "items": [
                        {
                          "recipient_type":"EMAIL",
                          "amount":{
                            "value":str(amount),
                            "currency":"USD"
                            },
                          "note":"Thanks for your participation!",
                          "sender_item_id":str(payment.id),
                          "receiver":receiver
                        }
                      ]
                }

        head = {
                "Content-Type": "application/json",
                'Authorization': 'Bearer {}'.format(access_token)
                }
        rb = requests.post(PAYOUT_URL, data=json.dumps(payload), headers=head)
        profile.balance = round(float(profile.balance) - amount, 2)
        profile.save()

        return redirect('profile')

@login_required
@csrf_exempt
def paypal_success(request):
    return render(request, 'paypal/success.html')

@login_required
@csrf_exempt
def paypal_failure(request):
    return render(request, 'paypal/failure.html')

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
    study_form['req_oss'].label = "Require Experience With Open Source?"

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
    '''
    if user_profile.age < study.min_age or \
       user_profile.age > study.max_age or \
       user.profile.years_of_experience < study.min_yoe or \
       user.profile.years_of_experience > study.max_yoe:
    '''
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
                # TODO move compensation amount
                #      from study balance to user
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

