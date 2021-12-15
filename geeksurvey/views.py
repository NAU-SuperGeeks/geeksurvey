from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login

from .models import Example

def index(request):
  example_list = Example.objects.order_by('-pub_date')[:5]
  context = {
    'example_list': example_list,
  }
  return render(request, 'home.html', context)

def working(request):
  context = {}
  return render(request, 'working.html', context)

