from django import forms
from django.urls import reverse
from django.views.generic import FormView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from .models import Study
import random

from paypal.standard.forms import PayPalPaymentsForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'age', 'years_of_experience', 'level_of_education', 'occupation', 'country_of_origin', 'current_location', 'race_and_ethnicity', 'open_source_experience', 'gender']

class StudyUpdateForm(forms.ModelForm):
    class Meta:
        model = Study
        exclude = ['id', 'last_modified', 'enrolled', 'completed', 'owner', 'expiry_date', 'balance']

class StudyCompleteForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['completion_code']

class ClaimFundsForm(forms.Form):
        email = forms.EmailField()

