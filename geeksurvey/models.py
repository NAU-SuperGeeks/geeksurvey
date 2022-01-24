import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Allows for enumerated types
from django.utils.translation import gettext_lazy as _

class Study(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=400)
    last_modified = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField('expiry date')

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

    def __str__(self):
      return self.title

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # avatar = models.ImageField(default='/static/pfp_participant.png')
    bio = models.TextField(max_length=200)
    age = models.IntegerField(default=0)
    user_exp = models.IntegerField(default=0)

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
