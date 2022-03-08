from django import forms
from geeksurvey.models import Study
from datetime import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from crispy_forms.bootstrap import *

class StudyUpdateForm(forms.ModelForm):
    class Meta:
        class DateInput(forms.DateInput):
            input_type = 'date'
            input_value = 'expiry_date'

            def __init__(self, **kwargs):
                kwargs["format"] = "%Y-%m-%d"
                super().__init__(**kwargs)

        model = Study
        exclude = ['id', 'last_modified', 'enrolled', 'completed', 'compensated', 'owner', 'balance']
        widgets = {'expiry_date' : DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-6 mb-0'),
                Column('expiry_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            'completion_code',
            Row(
                Column(
                    PrependedText('compensation', '$'), css_class='form-group col-md-2 mb-0'),
                Column('max_participants', css_class='form-group col-md-2 mb-0'),
                Column('survey_url', css_class='form-group col-md-8 mb-0'),
                css_class='form-row'
            ),
            Accordion(
            AccordionGroup('Enrollment Criteria',
              Row(
                  Column(
                      AppendedText('min_age', 'years'), css_class='form-group col-md-3 mb-0'),
                  Column(
                      AppendedText('max_age', 'years'), css_class='form-group col-md-3 mb-0'),
                  css_class='form-row'
              ),
              HTML('<hr>'),
              'req_job',
              Row(
                  Column(
                      AppendedText('min_yoe', 'years'), css_class='form-group col-md-3 mb-0'),
                  Column(
                      AppendedText('max_yoe', 'years'), css_class='form-group col-md-3 mb-0'),
                  css_class='form-row'
              ),
              HTML('<hr>'),
              'req_edu',
              'req_rne',
              'req_sex',
              'req_oss'), active=False),
              Submit('submit', 'Submit')
        )

class StudyCompleteForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['completion_code']

class StudyFundsForm(forms.Form):
    amount = forms.DecimalField()

