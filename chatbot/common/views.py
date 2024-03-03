from django.shortcuts import render, redirect
from django.contrib.auth import logout

# Create your views here.

def logout_view(request):
    logout(request)
    return redirect('chat_app:chat')
