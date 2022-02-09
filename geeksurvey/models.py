import datetime
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Allows for enumerated types
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError

USD_DECIMAL_NUM = 2
USD_MAX_DIGITS = 17

class Study(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    last_modified = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField('expiry date')
    balance = models.DecimalField(default=0, max_digits=USD_MAX_DIGITS,
                                    decimal_places=USD_DECIMAL_NUM)
    compensation = models.DecimalField(default=0, max_digits=USD_MAX_DIGITS,
                                    decimal_places=USD_DECIMAL_NUM)

    owner = models.ForeignKey(User,
                              related_name="owner",
                              unique=False,
                              on_delete=models.CASCADE)

    enrolled = models.ManyToManyField(User,
                                 related_name="enrolled",
                                 blank=True)

    completed = models.ManyToManyField(User,
                                 related_name="completed",
                                 blank=True)

    completion_code = models.TextField(max_length=32)

    survey_url = models.URLField(max_length=200)

    # begin enrollment criteria

    # age
    min_age = models.PositiveSmallIntegerField(default=0)
    max_age = models.PositiveSmallIntegerField(default=150)

    # years of experience
    min_yoe = models.PositiveSmallIntegerField(default=0)
    max_yoe = models.PositiveSmallIntegerField(default=150)

    # TODO add more criteria

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        return self.title

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # avatar = models.ImageField(default='/static/pfp_participant.png')
    bio = models.TextField(max_length=200)
    age = models.PositiveSmallIntegerField(default=0)
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    balance = models.DecimalField(default=0, max_digits=USD_MAX_DIGITS, decimal_places=USD_DECIMAL_NUM)
    country_of_origin = CountryField(default="US", blank_label='(Select Country)')
    current_location = CountryField(default="US", blank_label='(Select Country)')

    # Defines choices in the Profile model class as recommended by Django Docs
    class LevelOfEducation(models.TextChoices):
        HIGH_SCHOOL = 'HS', _('High School or Equivalent')
        BACHELORS = 'BD', _('Bachelor\'s Degree')
        MASTERS = 'MD', _('Master\'s Degree')
        DOCTORATE = 'PHD', _('PhD or Equivalent')
    # Adds level of education as a choosable field for the user profile
    level_of_education = models.CharField(max_length=3,
        choices=LevelOfEducation.choices,
        default=LevelOfEducation.HIGH_SCHOOL)

    # Defines choices in the Profile model class as recommended by Django Docs
    class Occupation(models.TextChoices):
        SOFTWARE_ENGINEER = 'SWE', _('Software Engineer/Developer')
        DATA_SCIENTIST = 'DSCI', _('Data Scientist')
        SYSTEMS_ADMINISTRATOR = 'SYSA', _('System Administrator/Analyst')
        PRODUCT_MANAGER = 'PRDM', _('Product Manager')
        NETWORK_ADMINISTRATOR = 'NWA', _('Network Administrator/Analyst')
        DATABASE_ADMINISTRATOR = 'DBA', _('Database Administrator/Analyst')
        SECURITY_ANALYST = 'SECA', _('Security Analyst')
        PROFESSOR = 'PROF', _('Professor/Instructor')
        RESEARCHER = 'RSCHR', _('Researcher')
        SOFTWARE_TESTER = 'SWT', _('Software Tester')
    # Adds occupation as a choosable field for the user profile
    # TODO: May want to add an "other" option that is a write in. May require custom model.
    occupation = models.CharField(max_length=5,
        choices=Occupation.choices,
        default=Occupation.SOFTWARE_ENGINEER)

    def __str__(self):
        return self.user.username
