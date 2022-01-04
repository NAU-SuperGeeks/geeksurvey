from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required

from .models import Example
from .models import Profile

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def index(request):
  example_list = Example.objects.order_by('-pub_date')[:5]
  context = {
    'example_list': example_list,
  }
  return render(request, 'home.html', context)

def working(request):
  return render(request, 'working.html')
  
def help(request):
  return render(request, 'help.html')

@login_required
def profile(request):
  profile = Profile.objects.get(user=request.user)
  context={'profile':profile}
  print(profile.bio)
  return render(request, 'profile.html', context)

@login_required
def profile_update(request):
  profile = Profile.objects.get(user=request.user)
  if request.method == 'POST':
    u_form = UserUpdateForm(request.POST, instance=request.user)
    p_form = ProfileUpdateForm(request.POST,
                               request.FILES,
                               instance=request.user.profile)
    if u_form.is_valid() and p_form.is_valid():
        u_form.save()
        p_form.save()
        messages.success(request, f'Your account has been updated!')
        return redirect('profile') # Redirect back to profile page

  else:
      u_form = UserUpdateForm(instance=request.user)
      p_form = ProfileUpdateForm(instance=request.user.profile)

  context = {
      'profile': profile,
      'u_form': u_form,
      'p_form': p_form
  }

  return render(request, 'profile_update.html', context)

