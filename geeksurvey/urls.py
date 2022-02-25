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
    path('paypal/', include('paypal.standard.ipn.urls'), name='paypal-ipn'),
    path('paypal/success/', views.paypal_success, name='paypal-return'),
    path('paypal/failure/', views.paypal_failure, name='paypal-cancel'),
    path('paypal/fund-account/', views.profile_fund, name='paypal_fund'),
    path('paypal/claim-funds/', views.profile_claim, name='paypal_claim'),
    path('participate/', views.participate, name='participate'),
    path('participate/find/', views.part_discover, name='part_discover'),
    path('study/<uuid:study_id>/', views.study_landing_page, name='study_landing_page'),
    path('study/enroll/<uuid:study_id>/', views.study_enroll, name='study_enroll'),
    path('study/enroll/<uuid:study_id>/fail/', views.study_enroll_fail, name='study_enroll_fail'),
    path('study/complete/<uuid:study_id>/', views.study_complete, name='study_complete'),
    path('profile/', views.profile, name='profile'),
    path('profile/view/<str:username>', views.profile_view, name='profile_view'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('research/', views.research, name='research'),
    path('study/edit/<uuid:study_id>/', views.study_edit, name='study_edit'),
    path('study/create/', views.study_create, name='study_create'),
]
