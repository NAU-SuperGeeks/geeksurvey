import uuid
import pytz
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Allows for enumerated types
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError
from datetime import datetime

USD_DECIMAL_NUM = 2
USD_MAX_DIGITS = 17

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(User,
                              related_name="user_payments",
                              unique=False,
                              on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=USD_MAX_DIGITS,
                                    decimal_places=USD_DECIMAL_NUM)
    paid = models.BooleanField(default=False)


'''
Define Custom Profile Fields
'''
# Defines choices in the Profile model class as recommended by Django Docs
class LevelOfEducation(models.TextChoices):
    NONE             = '',   _('')
    PRIMARY_SCHOOL   = 'PS', _('Primary/Elementary School')
    SECONDARY_SCHOOL = 'SS', _('Secondary School (e.g. American High School or German Realschule)')
    SOME_COLLEGE     = 'SC', _('Some College/University Study Without Earning a Degree')
    ASSOCIATES       = 'AD', _('Associate\'s Degree (A.A., A.S., etc.)')
    BACHELORS        = 'BD', _('Bachelor\'s Degree (B.A., B.S., B.Eng., etc.)')
    MASTERS          = 'MD', _('Master\'s Degree (M.A., M.S., M.Eng., MBA, etc.)')
    PROFESSIONAL     = 'PRO', _('Professional Degree (JD, MD, etc.)')
    DOCTORATE        = 'DOC', _('Other Doctoral Degree (Ph.D., Ed.D., etc.)')

# Defines choices in the Profile model class as recommended by Django Docs
# Available choices based on 2021 Stack Overflow Developer Survey
class Occupation(models.TextChoices):
    NONE                                       = '',   _('')
    FULL_STACK_DEVELOPER                       = 'FSD', _('Full-stack Developer')
    BACK_END_DEVELOPER                         = 'BED', _('Back-end Developer')
    FRONT_END_DEVELOPER                        = 'FED', _('Front-end Developer')
    DESKTOP_ENTERPRISE_APPLICATION_DEVELOPER   = 'DEAD', _('Desktop/Enterprise Application Developer')
    MOBILE_DEVELOPER                           = 'MD', _('Mobile Developer')
    DEVOPS_SPECIALIST                          = 'DS', _('DevOps Specialist')
    SYSTEM_ADMINISTRATOR                       = 'SA', _('System Administrator')
    DATABASE_ADMINISTRATOR                     = 'DA', _('Database Administrator')
    DESIGNER                                   = 'D', _('Designer')
    EMBEDDED_APPLICATIONS_DEVICES_DEVELOPER    = 'EADD', _('Embedded Applications/Devices Developer')
    DATA_SCIENTIST_MACHINE_LEARNING_SPECIALIST = 'DSMLS', _('Data Scientist/Machine Learning Specialist')
    STUDENT                                    = 'S', _('Student')
    DATA_ENGINEER                              = 'DE', _('Data Engineer')
    ENGINEERING_MANAGER                        = 'EM', _('Engineering Manager')
    DATA_BUSINESS_ANALYST                      = 'DBA', _('Data/Business Analyst')
    QA_TEST_DEVELOPER                          = 'QTD', _('QA/Test Developer')
    PRODUCT_MANAGER                            = 'PM', _('Product Manager')
    ACADEMIC_RESEARCHER                        = 'AR', _('Academic Researcher')
    SITE_RELIABILITY_ENGINEER                  = 'SRE', _('Site Reliability Engineer')
    EDUCATOR                                   = 'E', _('Educator')
    GAME_GRAPHICS_DEVELOPER                    = 'GGD', _('Game/Graphics Developer')
    SCIENTIST                                  = 'SCI', _('Scientist')

# Available choices based on 2021 Stack Overflow Developer Survey
class RaceAndEthnicity(models.TextChoices):
    NONE                   = '',   _('')
    WHITE_EUROPEAN_DESCENT = 'WED', _('White or of European Descent')
    SOUTH_ASIAN            = 'SA', _('South Asian')
    HISPANIC_LATINO_A_X    = 'HL', _('Hispanic or Latino/a/x')
    MIDDLE_EASTERN         = 'ME', _('Middle Eastern')
    SOUTHEAST_ASIAN        = 'SEA', _('Southeast Asian')
    EAST_ASIAN             = 'EA', ('East Asian')
    BLACK_AFRICAN_DESCENT  = 'BAD', _('Black or of African Descent')
    INDIGENOUS             = 'I', _('Indigenous')
    PREFER_NOT_TO_SAY_IDK  = 'PNTSIDK', _('Prefer Not to Say or I Don\'t Know')

# Available choices based on 2021 Stack Overflow Developer Survey
class Gender(models.TextChoices):
    NONE                   = '',   _('')
    MAN                                        = 'M', _('Man')
    WOMAN                                      = 'W', _('Woman')
    NONBINARY_GENDERQUEER_GENDER_NONCONFORMING = 'NGGN', _('Non-binary/Genderqueer/Gender Non-conforming')
    PREFER_NOT_TO_SAY                          = 'PNTS', _('Prefer Not to Say')

class BooleanChoices(models.TextChoices):
    YES = 'Y', _('Yes')
    NO  = 'N', _('No')

'''
  End of Profile Fields
'''

class Study(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    last_modified = models.DateTimeField(auto_now=True)
    expiry_date = models.DateField('expiry date')
    balance = models.DecimalField(default=0, max_digits=USD_MAX_DIGITS,
                                    decimal_places=USD_DECIMAL_NUM)
    compensation = models.DecimalField(default=0, max_digits=USD_MAX_DIGITS,
                                    decimal_places=USD_DECIMAL_NUM)

    owner = models.ForeignKey(User,
                              related_name="user_studies",
                              unique=False,
                              on_delete=models.CASCADE)

    enrolled = models.ManyToManyField(User,
                                 related_name="enrolled",
                                 blank=True)

    completed = models.ManyToManyField(User,
                                 related_name="completed",
                                 blank=True)

    compensated = models.ManyToManyField(User,
                                 related_name="compensated",
                                 blank=True)

    max_participants = models.PositiveSmallIntegerField(default=50, blank=True)


    completion_code = models.TextField(max_length=32)

    survey_url = models.URLField(max_length=200)

    # begin enrollment criteria

    # age
    min_age = models.PositiveSmallIntegerField(default=0, blank=True)
    max_age = models.PositiveSmallIntegerField(default=150, blank=True)

    # years of experience
    min_yoe = models.PositiveSmallIntegerField(default=0, blank=True)
    max_yoe = models.PositiveSmallIntegerField(default=150, blank=True)

    req_edu = models.CharField(max_length=7,
                                choices=LevelOfEducation.choices,
                                default=LevelOfEducation.NONE,
                                blank=True)

    req_job = models.CharField(max_length=7,
                                choices=Occupation.choices,
                                default=Occupation.NONE,
                                blank=True)

    req_rne = models.CharField(max_length=7,
                                choices=RaceAndEthnicity.choices,
                                default=RaceAndEthnicity.NONE,
                                blank=True)

    req_sex = models.CharField(max_length=7,
                                choices=Gender.choices,
                                default=Gender.NONE,
                                blank=True)

    # require open source experience?
    req_oss = models.CharField(max_length=7,
                                choices=BooleanChoices.choices,
                                default=BooleanChoices.NO)

    # require github auth account?
    req_git = models.CharField(max_length=7,
                                choices=BooleanChoices.choices,
                                default=BooleanChoices.NO)

    # TODO required country

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        return self.title

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # false until the user manually updates their profile
    updated_once = models.BooleanField(default=False)

    bio = models.TextField(max_length=200)
    age = models.PositiveSmallIntegerField(default=18)

    balance = models.DecimalField(default=0, max_digits=USD_MAX_DIGITS, decimal_places=USD_DECIMAL_NUM)

    country_of_origin = CountryField(default="US", blank_label='(Select Country)')
    current_location = CountryField(default="US", blank_label='(Select Country)')


    # Adds level of education as a choosable field for the user profile
    level_of_education = models.CharField(max_length=3,
                                          choices=LevelOfEducation.choices,
                                          default=LevelOfEducation.PRIMARY_SCHOOL)


    # Adds occupation as a choosable field for the user profile
    # TODO: May want to add an "other" option that is a write in. May require custom model.
    occupation = models.CharField(max_length=5,
                                  choices=Occupation.choices,
                                  default=Occupation.STUDENT)
    # experience with occupation
    years_of_experience = models.PositiveSmallIntegerField(default=0)



    # Adds race and ethnicity as a choosable field for the user profile
    # TODO: May want to add an "other" option that is a write in. May require custom model.
    race_and_ethnicity = models.CharField(max_length=7,
                                          choices=RaceAndEthnicity.choices,
                                          default=RaceAndEthnicity.PREFER_NOT_TO_SAY_IDK)


    # Adds open source experience as a choosable field for the user profile
    open_source_experience = models.CharField(max_length=1,
                                              choices=BooleanChoices.choices,
                                              default=BooleanChoices.NO)


    # Adds gender as a choosable field for the user profile
    # TODO: May want to add an "other" option that is a write in. May require custom model.
    gender = models.CharField(max_length=4,
                              choices=Gender.choices,
                              default=Gender.PREFER_NOT_TO_SAY)

    # Adds email communication preference as a choosable field for the user profile.
    email_opt_in = models.CharField(max_length=1,
                                    choices=BooleanChoices.choices,
                                    default=BooleanChoices.NO)

    # record if authenticated by GitHub
    # if applicable, this gets set to True in .signals.py
    is_auth_by_github = models.BooleanField(default=False)

    
    # used to enforce enrollment criteria across the web application
    #   used for sending emails
    #            populated study discovery page
    #            actual enrollment
    def can_enroll(self, study):
        if self.updated_once == False:
            return False

        expiry_with_time = datetime(
              year=study.expiry_date.year,
              month=study.expiry_date.month,
              day=study.expiry_date.day)
        if datetime.now() > expiry_with_time:
            return False

        if self.age < study.min_age or \
           self.age > study.max_age or \
           self.years_of_experience < study.min_yoe or \
           self.years_of_experience > study.max_yoe:
           return False

        if study.req_edu != '' and \
           self.level_of_education != study.req_edu:
           return False

        if study.req_job != '' and \
           self.occupation != study.req_job:
           return False

        if study.req_rne != '' and \
           self.race_and_ethnicity != study.req_rne:
           return False

        if study.req_sex != '' and \
           self.gender != study.req_sex:
           return False

        if study.req_oss == 'Y' and \
           self.open_source_experience == 'N':
           return False

        if study.req_git == 'Y' and \
           not self.is_auth_by_github:
           return False

        if study.enrolled.count() >= study.max_participants:
            return False


        return True;

    def __str__(self):
        return self.user.username
