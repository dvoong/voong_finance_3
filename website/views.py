import datetime
import pandas as pd
import website.models as models
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from website.models import Transaction, RepeatTransaction
from django.db.models import Q

strptime = datetime.datetime.strptime

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
    if 'start' in request.GET:
        start = strptime(request.GET['start'], '%Y-%m-%d').date()
    else:
        start = today - datetime.timedelta(days=14)
    if  'end' in request.GET:
        end = strptime(request.GET['end'], '%Y-%m-%d').date()
    else:
        end = today + datetime.timedelta(days=14)

    balances, transactions = models.get_balances(user, start, end)

    balances['date'] = balances['date'].dt.strftime('%Y-%m-%d')
    if len(transactions):
        transactions['date'] = transactions['date'].dt.strftime('%Y-%m-%d')
    template_kwargs = {
        'transactions': transactions.to_dict('records'),
        'balances': balances.to_dict('records'),
        'start': start,
        'end': end,
        'today': datetime.date.today(),
        'start_plus_7': start + datetime.timedelta(days=7),
        'end_plus_7': end + datetime.timedelta(days=7),
        'start_minus_7': start - datetime.timedelta(days=7),
        'end_minus_7': end - datetime.timedelta(days=7),
    }
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
    date = strptime(request.POST['date'], '%Y-%m-%d').date()
    user = request.user
    size = float(request.POST['size'])
    description = request.POST['description']
    index = len(Transaction.objects.filter(user=request.user, date=date))
    repeat_status = request.POST.get('repeat_status', 'does_not_repeat')
    frequency = request.POST.get('frequency', None)
    today = datetime.date.today()
    if 'start' in request.POST:
        start = strptime(request.POST['start'], '%Y-%m-%d').date()
    else:
        start = today - datetime.timedelta(days=14)
    if  'end' in request.POST:
        end = strptime(request.POST['end'], '%Y-%m-%d').date()
    else:
        end = today + datetime.timedelta(days=14)

    if repeat_status == 'does_not_repeat':

        # generate repeat transactions
        repeat_transactions = RepeatTransaction.objects.filter(
            user=user,
            start_date__lt=end)
        transactions = []
        for rt in repeat_transactions:
            t = rt.generate_next_transaction()
            while t.date <= end:
                t_ = Transaction.objects.filter(user=user, date=t.date)
                t.index = len(t_)
                transactions.append(t)
                rt.previous_transaction_date = t.date
                t = rt.generate_next_transaction()
            rt.save()

        if len(transactions):
            t = min(transactions, key=lambda t: (t.date, t.index)) 

            try:
                last_transaction = Transaction.objects.filter(
                    Q(date__lt=t.date) | Q(date__lte=t.date, index__lt=t.index),
                    user=user
                ).latest('date', 'index')
                closing_balance = last_transaction.closing_balance
            except Transaction.DoesNotExist:
                closing_balance = 0

            for t in transactions:
                closing_balance += t.size
                t.closing_balance = closing_balance
                t.save()

        try:
            last_transaction = Transaction.objects.filter(
                user=request.user,
                date__lte=date
            ).latest('date', 'index')
            closing_balance = last_transaction.closing_balance + size
        except Transaction.DoesNotExist:
            closing_balance = size

        Transaction.objects.create(
            date=date,
            size=size,
            description=description,
            user=request.user,
            closing_balance=closing_balance,
            index=index
        )
        
        # update future transactions
        transactions = Transaction.objects.filter(date__gt=date,
                                                  user=request.user)
        for t in transactions:
            t.closing_balance += size
            t.save()

    else:
        end_condition = request.POST.get('end_condition', 'never_ends')
        if end_condition  == 'never_ends':
            RepeatTransaction.objects.create(
                start_date=date,
                size=size,
                description=description,
                user=request.user,
                index=0,
                frequency=frequency
            )
        elif end_condition == 'n_occurrences':
            
            def get_end_date(start, frequency, occurrences):
                if frequency == 'daily':
                    return start + datetime.timedelta(days=occurrences - 1)
                elif frequency == 'weekly':
                    return start + datetime.timedelta(days=7*(occurrences - 1))
                elif frequency == 'monthly':
                    month_start = start.month
                    month_end = (month_start + (occurrences - 1)) % 12
                    month_end = 12 if month_end == 0 else month_end

                    months_remainder = occurrences - (12 - month_start + 1)
                    months_remainder = max(0, months_remainder)
                    year_end += ((months_remainder > 0) * 12 + months_remainder) // 12

                    try:
                        return datetime.date(year_end, month_end, start.day)
                    except ValueError:
                        if month_end == 12:
                            month_end = 1
                            year_end += 1
                        else:
                            month_end += 1
                        x = datetime.date(year_end, month_end, 1)
                        return x - datetime.timedelta(days=1)

            occurrences = int(request.POST['n_occurrences'])
            
            end_date = get_end_date(date,
                                    occurrences=occurrences,
                                    frequency=frequency)

            RepeatTransaction.objects.create(
                start_date=date,
                size=size,
                description=description,
                user=request.user,
                index=0,
                frequency=frequency,
                end_date=end_date
            )

        elif end_condition == 'ends_on_date':

            RepeatTransaction.objects.create(
                start_date=date,
                size=size,
                description=description,
                user=request.user,
                index=0,
                frequency=frequency,
                end_date=request.POST['end_date']
            )
            
            
    return redirect('/home?start={}&end={}'.format(start, end))

def update_transaction(request):
    user = request.user
    transaction_id = int(request.POST['id'])
    date = datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date()
    size = float(request.POST['size'])
    description = request.POST['description']

    # generate repeat transactions
    repeat_transactions = RepeatTransaction.objects.filter(
        user=user,
        start_date__lt=date)
    transactions = []
    for rt in repeat_transactions:
        t = rt.generate_next_transaction()
        while t.date <= date:
            t_ = Transaction.objects.filter(user=user, date=t.date)
            t.index = len(t_)
            transactions.append(t)
            rt.previous_transaction_date = t.date
            t = rt.generate_next_transaction()
            rt.save()

    if len(transactions):
        t = min(transactions, key=lambda t: (t.date, t.index)) 

        try:
            last_transaction = Transaction.objects.filter(
                Q(date__lt=t.date) | Q(date__lte=t.date, index__lt=t.index),
                user=user
            ).latest('date', 'index')
            closing_balance = last_transaction.closing_balance
        except Transaction.DoesNotExist:
            closing_balance = 0

        for t in transactions:
            closing_balance += t.size
            t.closing_balance = closing_balance
            t.save()

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
        transactions_to_update = Transaction.objects.filter(
            user=user,
            date__gt=t.date,
            date__lt=old_date).exclude(id=transaction_id)
        transactions_to_update_2 = Transaction.objects.filter(
            user=user,
            date=old_date,
            index__lt=old_index).exclude(id=transaction_id)
        transactions_to_update = list(transactions_to_update) + list(transactions_to_update_2)
        for t_ in transactions_to_update:
            t_.closing_balance += old_size
            t.closing_balance -= t_.size
            t_.save()

    else: # moved forward in time
        transactions_to_update = Transaction.objects.filter(
            user=user, date__gt=old_date,
            date__lte=t.date)
        transactions_to_update_2 = Transaction.objects.filter(
            user=user,
            date=old_date,
            index__gt=old_index)
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

    t = Transaction.objects.get(user=user, id=transaction_id)

    from django.db.models import Q

    transactions_to_update = Transaction.objects.filter(Q(date__gt=t.date) | Q(date=t.date, index__gt=t.index), user=user)
    for t_ in transactions_to_update:
        t_.closing_balance -= t.size
        t_.save()

    t.delete()

    return redirect('home')

def sign_out(request):
    logout(request)
    return redirect('welcome')

def get_balances(request):
    user = request.user
    today = datetime.date.today()
    if 'start' in request.GET:
        start = strptime(request.GET['start'], '%Y-%m-%d').date()
    else:
        start = today - datetime.timedelta(days=14)
    if 'end' in request.GET:
        end = strptime(request.GET['end'], '%Y-%m-%d').date()
    else:
        end = today + datetime.timedelta(days=14)

    balances, transactions = models.get_balances(user, start, end)
    
    balances['date'] = balances['date'].dt.strftime('%Y-%m-%d')
    if len(transactions):
        transactions['date'] = transactions['date'].dt.strftime('%Y-%m-%d')
    return JsonResponse(
        {
            'data':{
                'balances': balances.to_dict('records'),
                'transactions': transactions.to_dict('records')
            }
        })
