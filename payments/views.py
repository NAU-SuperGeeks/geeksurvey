from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from paypal.standard.forms import PayPalPaymentsForm

from decouple import config
import requests
import json

from geeksurvey.models import Study, Profile, Payment

from .forms import *

@login_required
@csrf_exempt
def paypal_success(request):
    return render(request, 'payments/success.html')

@login_required
@csrf_exempt
def paypal_failure(request):
    return render(request, 'payments/failure.html')

@login_required
def fund(request):
    # Arbitrary amount reflected in signals.py
    # set for testing and proof of concept rather than
    # business purposes
    # This value must match the expected value in signals.py
    FUND_AMOUNT = 125
    payment = Payment(owner=request.user, amount=FUND_AMOUNT)
    payment.save()
    request.session['payment-id'] = str(payment.id)

    profile = Profile.objects.get(user=request.user)

    paypal_dict = {
            "business": config('PAYPAL_BIZ_EMAIL'),
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

    return render(request, 'payments/fund.html', context)

@login_required
def claim(request):
    # GET:
    # claim.html contains a form where
    # the user enter their paypal email address
    # -
    # POST:
    # if valid email address, send payment to paypal
    #    from BIZ to user_addr
    #     of amount profile.balance
    #     and set their balance to 0
    if request.method == 'GET':
        profile = Profile.objects.get(user=request.user)
        form    = ClaimFundsForm()
        form['email'].label = "Enter a VALID email address for your Paypal account"

        context = {
                'form': form,
                'profile': profile,
                }

        return render(request, 'payments/claim.html', context)
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
        PAYOUT_URL = "https://api.sandbox.paypal.com/v1/payments/payouts"
        TOKEN_URL = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        
        CLIENT_ID = config("PAYPAL_CLIENT_ID")
        CLIENT_SECRET = config("PAYPAL_CLIENT_SECRET")

        profile = Profile.objects.get(user=request.user)

        form = ClaimFundsForm(request.POST)
        receiver = form['email'].value()

        # Arbitrary claim range
        # because GeekSurvey covers fees for claims
        # and large values are likely to be exploits
        # This value should be shown in the UI
        MINIMUM_CLAIM = 5
        MAXIMUM_CLAIM = 500
        if profile.balance < MINIMUM_CLAIM or profile.balance > MAXIMUM_CLAIM:
            return redirect('profile')
            
        payment = Payment(owner=request.user, amount=(-1*profile.balance))
        payment.save()

        # GET ACCESS TOKEN
        headers = { 
                    "Content-Type": "application/json",
                    "Accept-Language": "en_US",
                }
        payload = {
                    "grant_type": "client_credentials",
                }

        token_response = requests.post(TOKEN_URL, data=payload, headers=headers, auth=(CLIENT_ID,CLIENT_SECRET))
        token_data = token_response.json()
        access_token = token_data['access_token']


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

        headers = {
                "Content-Type": "application/json",
                'Authorization': 'Bearer {}'.format(access_token)
                }

        # Since this is a batch payment, it is possible to group many users claims together
        # which could save a serious amount of money in fees
        payout_response = requests.post(PAYOUT_URL, data=json.dumps(payload), headers=headers)

        # In the sandbox, the above payment is always successful
        # But paypals live network may reject this kind of payment for various reasons.
        # For full deployment, there should be another hook in signals.py to listen
        #   for a notification of this payments success
        #     (and assert sender_item_id == some payment id in our database)
        #   and only update our internal balance after the external payment has been verified

        profile.balance = round(float(profile.balance) - amount, 2)
        profile.save()

        return redirect('profile')

