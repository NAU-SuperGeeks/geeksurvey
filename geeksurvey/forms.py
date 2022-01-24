from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from .models import Study


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'age', 'user_exp', 'level_of_education', 'occupation']

class StudyUpdateForm(forms.ModelForm):
    class Meta:
        model = Study
        exclude = ['last_modified', 'enrolled', 'completed', 'owner', 'expiry_date']

