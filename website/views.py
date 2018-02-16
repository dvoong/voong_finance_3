import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from website.models import Transaction

# Create your views here.
def is_authenticated(user):
    return user.is_authenticated

def index(request):
    if is_authenticated(request.user) == True:
        return redirect('home')
    else:
        return redirect('welcome')

def home(request):
    user = request.user
    return render(request, 'website/home.html', {'transactions': Transaction.objects.filter(user=user)})

def welcome(request):
    return render(request, 'website/welcome.html')

def register(request):
    email = request.POST['email']
    password = request.POST['password']
    user = User.objects.create_user(username=email, email=email, password=password)
    login(request, user)
    return redirect('home')

def login_view(request):
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return redirect('home')
    else:
        return redirect('welcome')

def create_transaction(request):
    date = request.POST['date']
    size = float(request.POST['size'])
    description = request.POST['description']
    try:
        last_transaction = Transaction.objects.latest('date')
        closing_balance = last_transaction.closing_balance + size
    except Transaction.DoesNotExist:
        closing_balance = size
    Transaction.objects.create(
        date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
        size=size,
        description=description,
        user=request.user,
        closing_balance=closing_balance
        )
    return redirect('home')
