"""geeksurvey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

from .forms import *

urlpatterns = [
    path('', views.index, name='home'),
    path('working.html', views.working, name='working'),
    path('help/', views.help, name='help'),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('payments/', include('payments.urls')),
    path('study/', include('study.urls')),
    path('paypal/', include('paypal.standard.ipn.urls'), name='paypal-ipn'),
    path('participate/', views.participate, name='participate'),
    path('participate/find/', views.part_discover, name='part_discover'),
    path('profile/', views.profile, name='profile'),
    path('profile/view/<str:username>', views.profile_view, name='profile_view'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('research/', views.research, name='research'),

]
