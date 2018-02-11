from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def is_authenticated():
    return False

def index(request):
    if is_authenticated() == True:
        return redirect('/home')
    else:
        return redirect('/welcome')

def home(request):
    return render(request, 'website/home.html')

def welcome(request):
    return render(request, 'website/welcome.html')
