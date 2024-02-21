from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView



# Create your views here.

def chat(request):    
    return render(request, 'chat/chat.html')