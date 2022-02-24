from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

'''
@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender
    print(ipn_obj)
    print(ipn_obj.invoice)
    print(ipn_obj.mc_gross)
    print(ipn_obj.mc_currency)
    print(ipn_obj.__dict__())
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != 'sb-igrnp13847920@business.example.com':
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.
        try:

            expected_amount = 20
            assert ipn_obj.mc_gross == expected_amount and ipn_obj.mc_currency == 'USD'
        except Exception:
            logger.exception('Paypal ipn_obj data not valid!')
        else:
            print("passed tests, saving payment to db")
            # TODO save payment to db

    else:
        logger.debug('Paypal payment status not completed: %s' % ipn_obj.payment_status)
'''


@receiver(valid_ipn_received)
def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    print("IPN HOOK:")
    print(ipn_obj)
    print(ipn_obj.invoice)

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != config('PAYPAL_BIZ_EMAIL'):
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        # TODO Undertake some action depending upon `ipn_obj`.

        price = 20

        if ipn_obj.mc_gross == price and ipn_obj.mc_currency == 'USD':
            print("Y")
    else:
      print("X")


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

