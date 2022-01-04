from django.contrib import admin

from .models import Example
from .models import Profile

admin.site.register(Example)
admin.site.register(Profile)

