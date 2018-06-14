import datetime
import pandas as pd
import website.models as models
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from website.models import Transaction, RepeatTransaction
import datetime as dt

strptime = datetime.datetime.strptime

# Create your views here.
def is_authenticated(user):
    return user.is_authenticated

def index(request):
    if is_authenticated(request.user) == True:
        return redirect('home')
    else:
        return redirect('welcome')

@login_required    
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

    days = (end - start).days
    center_on_today_start = today - datetime.timedelta(days=days//2)
    center_on_today_end = today + datetime.timedelta(days=days - days//2)

    balances, transactions = models.get_balances(user, start, end)

    balances['date'] = balances['date'].dt.strftime('%Y-%m-%d')
    if len(transactions):
        transactions['date'] = transactions['date'].dt.strftime('%Y-%m-%d')

    repeat_transactions = RepeatTransaction.objects.filter(user=user)
    
    template_kwargs = {
        'transactions': transactions.to_json(orient='records'),
        'balances': balances.to_dict('records'),
        'start': start,
        'end': end,
        'today': today,
        'start_plus_7': start + datetime.timedelta(days=7),
        'end_plus_7': end + datetime.timedelta(days=7),
        'start_minus_7': start - datetime.timedelta(days=7),
        'end_minus_7': end - datetime.timedelta(days=7),
        'center_on_today_start': center_on_today_start,
        'center_on_today_end': center_on_today_end,
        'repeat_transactions': repeat_transactions,
    }
    return render(request, 'website/home.html', template_kwargs)

def welcome(request):
    return render(request, 'website/welcome.html')

def register(request):
    email = request.POST['email']
    password = request.POST['password']
    user = User.objects.create_user(username=email, email=email, password=password)
    user.is_active = False
    user.save()
    # login(request, user)

    subject = 'Verify your email'
    current_site = get_current_site(request)
    domain = current_site.domain
    body = 'This is a test message sent to {}.\nhttp://{}/activate'.format(email, domain)
    send_mail(subject, body, 'registration@voong-finance.co.uk', [email, ])

    return redirect('verify_email')
    # return redirect('home') # TODO

def verify_email(request):
    return render(request, 'website/verify-email.html')

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
            start_date__lte=end)
        
        for rt in repeat_transactions:
            for t in rt.generate_next_transaction(end):
                t.recalculate_closing_balances()

        t = Transaction(
            date=date,
            size=size,
            description=description,
            user=user,
            index=index
        )

        t.recalculate_closing_balances()
        
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
    today = datetime.date.today()
    if 'start' in request.POST:
        start = strptime(request.POST['start'], '%Y-%m-%d').date()
    else:
        start = today - datetime.timedelta(days=14)
    if  'end' in request.POST:
        end = strptime(request.POST['end'], '%Y-%m-%d').date()
    else:
        end = today + datetime.timedelta(days=14)
    update_how = request.POST.get('update_how', 'update_only_this_transaction')
    transaction = Transaction.objects.get(user=user, id=transaction_id)
    repeat_transaction = transaction.repeat_transaction
    date_changed = transaction.date != date

    if date_changed and update_how != 'update_only_this_transaction':
        raise Exception('asdf')

    if update_how == 'update_only_this_transaction':
        return update_only_this_transaction(user, date, size, description, transaction, start, end)

    # update repeat_transaction?
    repeat_transaction.size = size
    repeat_transaction.description = description
    repeat_transaction.save()

    if update_how == 'update_this_transaction_and_future_transactions':
        ts = Transaction.objects.filter(user=user,
                                        date__gte=transaction.date,
                                        repeat_transaction=repeat_transaction)
    elif update_how == 'update_all_transactions_of_this_kind':
        ts = Transaction.objects.filter(user=user,
                                        repeat_transaction=repeat_transaction)

    for t in ts:
        t.size = size
        t.description = description
        t.save()

    # transactions_to_recalculate_closing_balance
    first_t = min(ts, key=lambda t: (t.date, t.index))
    ts_to_recalculate = Transaction.objects.filter(
        Q(date__gt=first_t.date) | Q(date=first_t.date, index__gt=first_t.index),
        user=user).order_by('date', 'index')

    for t in ts_to_recalculate:
        try:
            last_transaction = Transaction.objects.filter(
                Q(date__lt=t.date) |
                Q(date__lte=t.date, index__lt=t.index),
                user=user).latest('date', 'index')
            closing_balance = last_transaction.closing_balance + t.size
        except Transaction.DoesNotExist:
            closing_balance = self.size
        t.closing_balance = closing_balance
        t.save()
    
    return redirect('/home?start={}&end={}'.format(start, end))

def update_only_this_transaction(user, date, size, description, t, start, end):
        
    # generate repeat transactions
    repeat_transactions = RepeatTransaction.objects.filter(
        user=user,
        start_date__lte=date)
        
    for rt in repeat_transactions:
        for t in rt.generate_next_transaction(date):
            t.recalculate_closing_balances()

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
            date__lt=old_date).exclude(id=t.id)
        transactions_to_update_2 = Transaction.objects.filter(
            user=user,
            date=old_date,
            index__lt=old_index).exclude(id=t.id)
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

    return redirect('/home?start={}&end={}'.format(start, end))

def modify_transaction(request):
    if request.POST['action'] == 'update':
        return update_transaction(request)
    elif request.POST['action'] == 'delete':
        return delete_transaction(request)

def delete_transaction(request):

    user = request.user
    transaction_id = int(request.POST['id'])
    date = request.POST['date']
    delete_how = request.POST.get('delete_how', 'delete_only_this_transaction')
    repeat_transaction_id = request.POST.get('repeat_transaction_id', None)
    today = datetime.date.today()
    if 'start' in request.POST:
        start = strptime(request.POST['start'], '%Y-%m-%d').date()
    else:
        start = today - datetime.timedelta(days=14)
    if  'end' in request.POST:
        end = strptime(request.POST['end'], '%Y-%m-%d').date()
    else:
        end = today + datetime.timedelta(days=14)

    if delete_how == 'delete_only_this_transaction':

        t = Transaction.objects.get(user=user, id=transaction_id)

        transactions_to_update = Transaction.objects.filter(Q(date__gt=t.date) |
                                                            Q(date=t.date, index__gt=t.index),
                                                            user=user)
        for t_ in transactions_to_update:
            t_.closing_balance -= t.size
            t_.save()

        t.delete()

    elif delete_how == 'delete_this_transaction_and_future_transactions':
        t = Transaction.objects.get(user=user, id=transaction_id)
        ts = Transaction.objects.filter(user=user,
                                        repeat_transaction_id=int(repeat_transaction_id),
                                        date__gte=date)
        ts.delete()

        transactions_to_update = Transaction.objects.filter(Q(date__gt=t.date) |
                                                            Q(date=t.date, index__gt=t.index),
                                                            user=user)

        for t_ in transactions_to_update:
            try:
                last_transaction = Transaction.objects.filter(
                    Q(date__lt=t_.date) |
                    Q(date__lte=t_.date, index__lt=t_.index),
                    user=user).latest('date', 'index')
                closing_balance = last_transaction.closing_balance + t_.size
            except Transaction.DoesNotExist:
                closing_balance = self.size
            t_.closing_balance = closing_balance
            t_.save()

        rt = t.repeat_transaction
        rt.end_date = t.date
        rt.save()

    elif delete_how == 'all_transactions_of_this_type':
        t = Transaction.objects.get(user=user, id=transaction_id)

        rt = t.repeat_transaction
        rt.end_date = t.date
        rt.save()

        ts = Transaction.objects.filter(
            user=user,
            repeat_transaction_id=int(repeat_transaction_id))

        ts.delete()

        transactions_to_update = Transaction.objects.filter(
            date__gte=rt.start_date,
            user=user)

        for t_ in transactions_to_update:
            try:
                last_transaction = Transaction.objects.filter(
                    Q(date__lt=t_.date) |
                    Q(date__lte=t_.date, index__lt=t_.index),
                    user=user).latest('date', 'index')
                closing_balance = last_transaction.closing_balance + t_.size
            except Transaction.DoesNotExist:
                closing_balance = t_.size
            t_.closing_balance = closing_balance
            t_.save()
        
    return redirect('/home?start={}&end={}'.format(start, end))

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

    balances = balances.where((pd.notnull(balances)), None)
    transactions = transactions.where((pd.notnull(transactions)), None)
    
    return JsonResponse(
        {
            'data':{
                'balances': balances.to_dict('records'),
                'transactions': transactions.to_dict('records')
            }
        })

def get_repeat_transaction_deletion_prompt(request):
    return render(request, 'website/html_snippets/repeat_transaction_deletion_prompt.html')

def get_repeat_transaction_update_prompt(request):
    return render(request, 'website/html_snippets/repeat_transaction_update_prompt.html')

def update_repeat_transaction(request):
    start = strptime(request.POST['start'], '%Y-%m-%d').date()
    end = strptime(request.POST['end'], '%Y-%m-%d').date()
    rt = RepeatTransaction.objects.get(user=request.user, id=request.POST['id'])
    old_start_date = rt.start_date
    old_size = rt.size
    rt.start_date = strptime(request.POST['start_date'], '%Y-%m-%d').date()
    rt.description = request.POST['description']
    rt.size = float(request.POST['size'].replace('£', ''))
    rt.save()

    ts = Transaction.objects.filter(user=request.user, repeat_transaction=rt)
    for t in ts:
        t.description = rt.description
        t.size = rt.size
        t.save()

    if old_start_date > rt.start_date:
        # create transactions from new start_date up to the old one
        rt.generate_transactions(rt.start_date, old_start_date - dt.timedelta(days=1))
    elif old_start_date < rt.start_date:
        # repeat transaction moved forward, delete those earlier
        ts = Transaction.objects.filter(
            date__gte=old_start_date,
            date__lt=rt.start_date,
            repeat_transaction=rt,
            user=request.user).order_by('date', 'index')

        earliest_transaction = ts[0]
        previous_transaction = ts[0].get_previous_transaction()
        closing_balance = previous_transaction.closing_balance if previous_transaction else 0
        ts.delete()


        later_transactions = Transaction.objects.filter(
            Q(date__gt=earliest_transaction.date) | Q(date=earliest_transaction.date,
                                                      index__gte=earliest_transaction.index),
            user=request.user
        ).order_by('date', 'index')
        
        for t in later_transactions:
            if t.date == earliest_transaction.date and t.index > earliest_transaction.index:
                t.index -= 1
            t.closing_balance = closing_balance + t.size
            closing_balance = t.closing_balance
            t.save()

    if old_size != rt.size:
        
        t = Transaction.objects.filter(
            repeat_transaction=rt,
            user=request.user
        ).order_by('date', 'index').first()

        previous_transaction = t.get_previous_transaction()
        closing_balance = previous_transaction.closing_balance if previous_transaction else 0

        ts = Transaction.objects.filter(
            Q(date__gt=t.date) | Q(date=t.date, index__gte=t.index),
            user=request.user
        ).order_by('date', 'index')
        
        for t in ts:
            t.closing_balance = closing_balance + t.size
            closing_balance = t.closing_balance
            t.save()

    
    return redirect('/home?start={start}&end={end}'.format(start=start, end=end))
