from django.dispatch import receiver

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

from decouple import config

import uuid

from geeksurvey.models import Profile, Payment


@receiver(valid_ipn_received)
def handle_payment(sender, **kwargs):
    ipn_obj = sender

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != config('PAYPAL_BIZ_EMAIL', default=""):
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        # FUND_AMOUNT is set for testing and proof of concept
        # rather than for business purposes
        # This value must match the payment value in the profile_fund view
        FUND_AMOUNT = 125

        # FUND_RESULT is less than FUND_AMOUNT.
        # The PayPal business account does not recieve the full FUND_AMOUNT
        #   It should receive ipn_obj.mc_gross - ipn_obj.mc_fees
        # So GeekSurvey cuts off some extra $ to fund itself
        FUND_RESULT = 100

        # FUND_AMOUNT and FUND_RESULT should be clearly shown to users
        # In the frontend before their purchase

        if ipn_obj.mc_gross == FUND_AMOUNT and ipn_obj.mc_currency == 'USD':
            payment_id = uuid.UUID(ipn_obj.invoice)
            payment = Payment.objects.get(id=payment_id)
            profile = Profile.objects.get(user=payment.owner)
            profile.balance += FUND_RESULT
            profile.save()

            payment.paid = True
            payment.save()
    else:
        return

