from django.core.mail import send_mail
from django.urls import reverse

from geeksurvey.models import Study, Profile, User
from geeksurvey.settings import *


def study_custom_labels(study_form):
    study_form['compensation'].label = "Compensation (USD)"
    study_form['survey_url'].label = "Survey URL"
    study_form['min_age'].label = "Minimum Age for Participants"
    study_form['max_age'].label = "Maximum Age for Participants"
    study_form['min_yoe'].label = "Minimum Years of Experience"
    study_form['max_yoe'].label = "Maximum Years of Experience"
    study_form['max_nop'].label = "Maximum Number of Participants"
    study_form['req_edu'].label = "Required Education"
    study_form['req_job'].label = "Required Occupation"
    study_form['req_rne'].label = "Required Race / Ethnicity"
    study_form['req_sex'].label = "Required Gender"
    study_form['req_oss'].label = "Require Experience With Open Source Development?"

def study_send_mail(request, study):
    all_users = User.objects.all()
    emails = []
    for user in all_users:
        profile = Profile.objects.get(user=user)
        if profile.can_enroll(study) and \
           profile.email_opt_in == 'Y' and \
           study.owner != user:
            emails.append(user.email)

    print([study.title + " SENDING MAIL TO ", emails])
    if emails == []: return

    study_url = request.build_absolute_uri(reverse('study_landing_page', args=(study.id,)))
    try:
        email_param = {
            'subject': 'New Study on GeekSurvey',
            'message': '',
            'html_message':
                f"""
                    <h2>You are eligible for a study at GeekSurvey!</h2>
                    <p>Follow this link to the Survey:</p>
                    <a href="{study_url}">Click here to participate</a>

                """,
            'from_email': EMAIL_HOST_USER,
            'recipient_list': emails,
        }
        res_mail = send_mail(**email_param)
    except Exception as e:
        print(e)

