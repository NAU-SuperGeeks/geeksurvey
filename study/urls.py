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
from django.urls import path, include

from . import views

urlpatterns = [
    path('<uuid:study_id>/', views.study_landing_page, name='study_landing_page'),
    path('enroll/<uuid:study_id>/', views.study_enroll, name='study_enroll'),
    path('enroll/<uuid:study_id>/fail/', views.study_enroll_fail, name='study_enroll_fail'),
    path('complete/<uuid:study_id>/', views.study_complete, name='study_complete'),
    path('edit/<uuid:study_id>/', views.study_edit, name='study_edit'),
    path('funds/<uuid:study_id>/', views.study_funds, name='study_funds'),
    path('create/', views.study_create, name='study_create'),
]

