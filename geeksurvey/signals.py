from decouple import config

import uuid

from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile, Payment, User

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

# TODO test this
@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    GITHUB_PROVIDER_ID = "github"
    if 'sociallogin' in kwargs:
        sociallogin = kwargs["sociallogin"]
        if sociallogin.account.provider == GITHUB_PROVIDER_ID:
            profile = Profile.objects.get(user=user)
            profile.is_auth_by_github = True
            profile.save()

