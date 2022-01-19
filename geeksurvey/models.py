import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

    def __str__(self):
        return self.user.username
