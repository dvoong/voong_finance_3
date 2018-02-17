import datetime
import pandas as pd
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
    today = datetime.date.today()
    start = request.GET.get('start', today - datetime.timedelta(days=14))
    end = request.GET.get('end', today + datetime.timedelta(days=15))
    dates = pd.DataFrame(pd.date_range(start, end - datetime.timedelta(days=1)), columns=['date'])
    balances = dates

    try:
        last_transaction = Transaction.objects.filter(user=user, date__lt=start).latest('date')
        closing_balance = last_transaction.closing_balance
    except Transaction.DoesNotExist:
        closing_balance = 0
    
    balances['balance'] = closing_balance
    
    transactions = Transaction.objects.filter(user=user, date__gte=start, date__lt=end).order_by('date')
    if len(transactions):
        transactions_df = pd.DataFrame(list(transactions.values()))
        transactions_df['date'] = transactions_df['date'].astype('datetime64[ns]')
        transactions_by_date = transactions_df.groupby('date')['size'].sum().reset_index()
        transactions_by_date = dates.merge(transactions_by_date, on='date', how='left').fillna(0)
        transactions_by_date['cumsum']  = transactions_by_date['size'].cumsum()
        balances['balance'] += transactions_by_date['cumsum']
    
    balances['date'] = balances['date'].dt.strftime('%Y-%m-%d')
    return render(request, 'website/home.html', {'transactions': transactions, 'balances': balances.to_dict('records')})

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
        last_transaction = Transaction.objects.filter(user=request.user, date__lt=date).latest('date')
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

    # update future transactions
    transactions = Transaction.objects.filter(date__gt=datetime.datetime.strptime(date, '%Y-%m-%d').date(), user=request.user)
    for t in transactions:
        t.closing_balance += size
        t.save()
    return redirect('home')
