import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Allows for enumerated types
from django.utils.translation import gettext_lazy as _

class Example(models.Model):
    example_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
      return self.example_text

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

    def __str__(self):
        return self.user.username
