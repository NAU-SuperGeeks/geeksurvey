# TODO remove whole file?
# moved to signals.py for now

from decouple import config
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

# TODO rename function

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

valid_ipn_received.connect(show_me_the_money)
