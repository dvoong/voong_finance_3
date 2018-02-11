from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User

# Create your views here.
def is_authenticated():
    return False

def index(request):
    if is_authenticated() == True:
        return redirect('home')
    else:
        return redirect('welcome')

def home(request):
    return render(request, 'website/home.html')

def welcome(request):
    return render(request, 'website/welcome.html')

def register(request):
    # get email and password
    email = request.POST['email']
    password = request.POST['password']
    # create new user
    User.objects.create_user(username=email, email=email, password=password)
    # log new user in
    # redirect to home page
    return redirect('home')
