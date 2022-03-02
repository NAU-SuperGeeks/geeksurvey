from django import forms
from geeksurvey.models import Study
from datetime import datetime

class StudyUpdateForm(forms.ModelForm):
    class Meta:
        class DateTimeInput(forms.DateTimeInput):
            input_type = 'datetime-local'
            input_value = 'expiry_date'

        model = Study
        exclude = ['id', 'last_modified', 'enrolled', 'completed', 'owner', 'balance']
        widgets = {'expiry_date' : DateTimeInput()}

class StudyCompleteForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['completion_code']

class StudyFundsForm(forms.Form):
    amount = forms.DecimalField()
