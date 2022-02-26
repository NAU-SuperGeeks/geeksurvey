from django import forms
from geeksurvey.models import Study

class StudyUpdateForm(forms.ModelForm):
    class Meta:
        model = Study
        exclude = ['id', 'last_modified', 'enrolled', 'completed', 'owner', 'expiry_date', 'balance']

class StudyCompleteForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['completion_code']

class StudyFundsForm(forms.Form):
    amount = forms.DecimalField()

