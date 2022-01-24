from django.contrib import admin

from .models import Study
from .models import Profile

admin.site.register(Study)
admin.site.register(Profile)

