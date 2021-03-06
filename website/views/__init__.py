import datetime, math
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
from django.views import View
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from website.models import Transaction, RepeatTransaction
import datetime as dt
from voong_finance.utils import iso_to_date
from voong_finance.utils.argparse import ArgParser
from voong_finance.utils import TokenGenerator
from website import forms
from django.contrib.auth import views as auth_views
from website.views.create_transaction import CreateTransactionView
from website.views.home import HomeView
from website.views.register import RegisterView

strptime = datetime.datetime.strptime

# Create your views here.
def is_authenticated(user):
    return user.is_authenticated

create_transaction = login_required(CreateTransactionView.as_view())
home = login_required(HomeView.as_view())

def index(request):
    if is_authenticated(request.user) == True:
        return redirect('home')
    else:
        return redirect('welcome')
register = RegisterView.as_view()

def welcome(request):
    return render(request, 'website/welcome.html')

def activate(request, uidb64, token):

    account_activation_token = TokenGenerator()

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')

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
        size_old = t.size
        t.size = size
        t.description = description
        t.save(update_downstream=size_old != t.size)

    # # transactions_to_recalculate_closing_balance
    # first_t = min(ts, key=lambda t: (t.date, t.index))
    # ts_to_recalculate = Transaction.objects.filter(
    #     Q(date__gt=first_t.date) | Q(date=first_t.date, index__gt=first_t.index),
    #     user=user).order_by('date', 'index')

    # for t in ts_to_recalculate:
    #     try:
    #         last_transaction = Transaction.objects.filter(
    #             Q(date__lt=t.date) |
    #             Q(date__lte=t.date, index__lt=t.index),
    #             user=user).latest('date', 'index')
    #         closing_balance = last_transaction.closing_balance + t.size
    #     except Transaction.DoesNotExist:
    #         closing_balance = self.size
    #     t.closing_balance = closing_balance
    #     t.save()
    
    return redirect('/home?start={}&end={}'.format(start, end))

def update_only_this_transaction(user, date, size, description, t, start, end):
        
    # generate repeat transactions
    repeat_transactions = RepeatTransaction.objects.filter(
        user=user,
        start_date__lte=date)
        
    for rt in repeat_transactions:
        for t in rt.generate_next_transaction(date):
            t.recalculate_closing_balances()
        rt.save()

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
            t_.save(update_downstream=False)

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
            t_.save(update_downstream=False)

    # if transaction size has changed as well
    if t.size != old_size:
        t.closing_balance += t.size - old_size
        transactions_to_update = Transaction.objects.filter(user=user, date__gt=t.date)
        for t_ in transactions_to_update:
            t_.closing_balance += t.size - old_size
            t_.save(update_downstream=False)
            
    t.save(update_downstream=False)

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
            t_.save(update_downstream=False)

        t.delete()

    elif delete_how == 'delete_this_transaction_and_future_transactions':

        t = Transaction.objects.get(user=user, id=transaction_id)
        rt = t.repeat_transaction
        date = t.date
        index = t.index

        transactions = Transaction.objects.filter(
            repeat_transaction=rt,
            date__gte=date
        )

        for t in transactions:
            t.delete()

        if len(Transaction.objects.filter(repeat_transaction=rt)) == 0:
            rt.delete()
        else:
            rt.end_date = date
            rt.save()
        
        transactions_to_update = Transaction.objects.filter(
            Q(date__gt=date) |
            Q(date=date, index__gt=index),
            user=user
        ).order_by('date', 'index')

        try:
            last_transaction = Transaction.objects.filter(
                Q(date__lt=date) |
                Q(date=date, index__lt=index),
                user=user
            ).latest('date', 'index')
            closing_balance = last_transaction.closing_balance
        except Transaction.DoesNotExist:
            closing_balance = 0

        for t in transactions_to_update:
            closing_balance = closing_balance + t.size
            t.closing_balance = closing_balance
            t.save(update_downstream=False)

    elif delete_how == 'all_transactions_of_this_type':
        t = Transaction.objects.get(user=user, id=transaction_id)
        date = t.date
        index = t.index
        rt = t.repeat_transaction

        transactions = Transaction.objects.filter(
            repeat_transaction=rt
        ).order_by('date', 'index')

        for t in transactions:
            t.delete()
        rt.delete()
            
        first_transaction = transactions.first()
        
        transactions_to_update = Transaction.objects.filter(
            Q(date__gt=first_transaction.date) |
            Q(date=first_transaction.date, index__gt=first_transaction.index),
            user=user
        ).order_by('date', 'index')

        try:
            last_transaction = Transaction.objects.filter(
                Q(date__lt=first_transaction.date) |
                Q(date=first_transaction.date, index__lt=first_transaction.index),
                user=user
            ).latest('date', 'index')
            closing_balance = last_transaction.closing_balance
        except Transaction.DoesNotExist:
            closing_balance = 0

        for t in transactions_to_update:
            closing_balance = closing_balance + t.size
            t.closing_balance = closing_balance
            t.save(update_downstream=False)
        
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

    repeat_transaction_id = int(request.POST['id'])
    rt = RepeatTransaction.objects.get(user=request.user, id=repeat_transaction_id)
    
    def convert_end_date(end_date):
        if end_date.lower() == '':
            return None
        else:
            return iso_to_date(end_date)
    
    arg_parser = ArgParser()
    arg_parser.add('start', iso_to_date, dt.date.today() - dt.timedelta(days=14))
    arg_parser.add('end', iso_to_date, dt.date.today() + dt.timedelta(days=14))
    arg_parser.add('start_date', iso_to_date, rt.start_date)
    arg_parser.add('end_date', convert_end_date, rt.end_date)
    arg_parser.add('size', lambda x: float(x.replace('£', '').replace(',', '')), rt.size)
    arg_parser.add('description', str, rt.description)
    args = arg_parser.parse_args(request, 'POST')
    
    start = args['start']
    end = args['end']
    start_date = args['start_date']
    end_date = args['end_date']
    size = args['size']
    description = args['description']
    
    old_start_date = rt.start_date
    old_size = rt.size
    old_end_date = rt.end_date

    # update repeat transaction
    rt.start_date = start_date
    rt.description = description 
    rt.size = size
    rt.end_date = end_date
    rt.previous_transaction_date = None
    rt.save()

    # delete previous transactions
    ts = Transaction.objects.filter(user=request.user, repeat_transaction=rt)
    ts.delete()

    return redirect('/home?start={start}&end={end}'.format(start=start, end=end))

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):

    def post(self, request):

        return HttpResponse('hi')
