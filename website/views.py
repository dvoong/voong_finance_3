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
    # start = request.GET.get('start', today - datetime.timedelta(days=14))
    # end = request.GET.get('end', today + datetime.timedelta(days=15))
    start = datetime.datetime.strptime(request.GET['start'], '%Y-%m-%d').date() if 'end' in request.GET else today - datetime.timedelta(days=14)
    end = datetime.datetime.strptime(request.GET['end'], '%Y-%m-%d').date() if 'end' in request.GET else today + datetime.timedelta(days=14)
    dates = pd.DataFrame(pd.date_range(start, end), columns=['date'])
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
    template_kwargs = {'transactions': transactions, 'balances': balances.to_dict('records'), 'start': start, 'end': end}
    return render(request, 'website/home.html', template_kwargs)

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
    index = len(Transaction.objects.filter(user=request.user, date=date))
    try:
        last_transaction = Transaction.objects.filter(user=request.user, date__lte=date).latest('date', 'index')
        closing_balance = last_transaction.closing_balance + size
    except Transaction.DoesNotExist:
        closing_balance = size

    Transaction.objects.create(
        date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
        size=size,
        description=description,
        user=request.user,
        closing_balance=closing_balance,
        index=index
    )

    # update future transactions
    transactions = Transaction.objects.filter(date__gt=datetime.datetime.strptime(date, '%Y-%m-%d').date(), user=request.user)
    for t in transactions:
        t.closing_balance += size
        t.save()
    return redirect('home')

def update_transaction(request):
    user = request.user
    transaction_id = int(request.POST['id'])
    date = datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date()
    size = float(request.POST['size'])
    description = request.POST['description']

    t = Transaction.objects.get(user=user, id=transaction_id)
    old_date = t.date
    old_size = t.size
    old_index = t.index

    # update transaction
    index = len(Transaction.objects.filter(user=user, date=date))
    t.date = date
    t.size = size
    t.description = description
    t.index = index

    # update transactions between old and new dates (assuming transaction size has not changed)
    if t.date < old_date: # moved back in time
        transactions_to_update = Transaction.objects.filter(user=user, date__gt=t.date, date__lt=old_date).exclude(id=transaction_id)
        transactions_to_update_2 = Transaction.objects.filter(user=user, date=old_date, index__lt=old_index).exclude(id=transaction_id)
        transactions_to_update = list(transactions_to_update) + list(transactions_to_update_2)
        for t_ in transactions_to_update:
            t_.closing_balance += old_size
            t.closing_balance -= t_.size
            t_.save()

    else: # moved forward in time
        transactions_to_update = Transaction.objects.filter(user=user, date__gt=old_date, date__lte=t.date)
        transactions_to_update_2 = Transaction.objects.filter(user=user, date=old_date, index__gt=old_index)
        transactions_to_update = list(transactions_to_update) + list(transactions_to_update_2)
        for t_ in transactions_to_update:
            t_.closing_balance -= old_size
            t.closing_balance += t_.size
            t_.save()

    # if transaction size has changed as well
    if t.size != old_size:
        t.closing_balance += t.size - old_size
        transactions_to_update = Transaction.objects.filter(user=user, date__gt=t.date)
        for t_ in transactions_to_update:
            t_.closing_balance += t.size - old_size
            t_.save()
            
    t.save()
    
    return redirect('home')

def modify_transaction(request):
    if request.POST['action'] == 'update':
        return update_transaction(request)
    elif request.POST['action'] == 'delete':
        return delete_transaction(request)

def delete_transaction(request):
    user = request.user
    transaction_id = int(request.POST['id'])
    date = datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date()
    size = float(request.POST['size'])
    description = request.POST['description']

    t = Transaction.objects.get(user=user, id=transaction_id)

    from django.db.models import Q

    transactions_to_update = Transaction.objects.filter(Q(date__gt=t.date) | Q(date=t.date, index__gt=t.index), user=user)
    for t_ in transactions_to_update:
        t_.closing_balance -= t.size
        t_.save()

    t.delete()

    return redirect('home')
