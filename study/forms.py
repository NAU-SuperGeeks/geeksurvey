from django import forms
from geeksurvey.models import Study
from datetime import datetime

class StudyUpdateForm(forms.ModelForm):
    class Meta:
        class DateInput(forms.DateInput):
            input_type = 'date'
            input_value = 'expiry_date'

            def __init__(self, **kwargs):
                kwargs["format"] = "%Y-%m-%d"
                super().__init__(**kwargs)

        model = Study
        exclude = ['id', 'last_modified', 'enrolled', 'completed', 'owner', 'balance']
        widgets = {'expiry_date' : DateInput()}

class StudyCompleteForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['completion_code']

class StudyFundsForm(forms.Form):
    amount = forms.DecimalField()

