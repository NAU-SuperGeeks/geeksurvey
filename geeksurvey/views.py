from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import Example

def index(request):
    example_list = Example.objects.order_by('-pub_date')[:5]
    context = {
      'example_list': example_list,
    }
    return render(request, 'index.html', context)


