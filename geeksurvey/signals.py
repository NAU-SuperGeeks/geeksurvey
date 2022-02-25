from decouple import config

import uuid

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile, Payment, User

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

@receiver(valid_ipn_received)
def handle_payment(sender, **kwargs):
    ipn_obj = sender

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != config('PAYPAL_BIZ_EMAIL_P'):
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        price = 125

        if ipn_obj.mc_gross == price and ipn_obj.mc_currency == 'USD':
            payment_id = uuid.UUID(ipn_obj.invoice)
            payment = Payment.objects.get(id=payment_id)
            profile = Profile.objects.get(user=payment.owner)
            profile.balance += 100
            profile.save()

            payment.paid = True
            payment.save()
    else:
        return

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

