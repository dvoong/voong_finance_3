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

    argparser = ArgParser()
    argparser.add('start', iso_to_date, today - datetime.timedelta(days=14))
    argparser.add('end', iso_to_date, today + datetime.timedelta(days=14))
    args = argparser.parse_args(request, 'GET')

    start = args['start']
    end = args['end']
    
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
        'authenticated': request.user.is_authenticated,
        'new_transaction_form': forms.NewTransactionForm(auto_id="%s")
    }
    return render(request, 'website/home.html', template_kwargs)

def welcome(request):
    return render(request, 'website/welcome.html')

class RegisterView(View):

    @staticmethod
    def send_email_verification_email(request, email, user):
        subject = 'Verify your email'
        current_site = get_current_site(request)
        domain = current_site.domain
        
        account_activation_token = TokenGenerator()
        body = 'This is a test message sent to {}.\nhttp://{}/activate/{}/{}'.format(
            email,
            domain,
            force_text(urlsafe_base64_encode(force_bytes(user.pk))),
            account_activation_token.make_token(user)
        )
        send_mail(subject, body, 'registration@voong-finance.co.uk', [email, ])

    def post(self, request):

        argparser = ArgParser()
        argparser.add('email', required=True)
        argparser.add('password', required=True)
        args = argparser.parse_args(request, 'POST')
    
        email = args['email']
        password = args['password']
    
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False

        self.send_email_verification_email(request, email, user)

        user.save()
        return redirect('verify_email')

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

def create_transaction(request):
    date = strptime(request.POST['date'], '%Y-%m-%d').date()
    user = request.user
    size = float(request.POST['transaction_size'])
    description = request.POST['description']
    repeat_status = request.POST.get('repeats', 'does_not_repeat')
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
        # repeat_transactions = RepeatTransaction.objects.filter(
        #     user=user,
        #     start_date__lte=end)
        
        # for rt in repeat_transactions:
        #     for t in rt.generate_next_transaction(end):
        #         t.recalculate_closing_balances()

        #######

        repeat_transactions = RepeatTransaction.objects.filter(
            user=user,
            start_date__lte=end
        )

        generated_transactions = []
        
        for rt in repeat_transactions:
            for t in rt.generate_next_transaction(end):
                generated_transactions.append(t)
                # t.recalculate_closing_balances()

        t = Transaction(
            date=date,
            size=size,
            description=description,
            user=user,
        )

        generated_transactions.append(t)

        generated_transactions = sorted(generated_transactions, key=lambda t: t.date)
        
        t_first = generated_transactions[0]
        t_first.index = len(Transaction.objects.filter(user=user, date=t_first.date))

        if len(generated_transactions) > 1:
            for i in range(len(generated_transactions) - 1):
                t1 = generated_transactions[i]
                t2 = generated_transactions[i+1]
                if t1.date == t2.date:
                    t2.index = t1.index + 1
                else:
                    t2.index = len(Transaction.objects.filter(user=user, date=t2.date))

        transactions = list(Transaction.objects.filter(user=user, date__gt=t_first.date))
        transactions = transactions + generated_transactions
        transactions = sorted(transactions, key=lambda t: (t.date, t.index))
        
        try:
            last_transaction = Transaction.objects.filter(
                user=user,
                date__lte=t_first.date
            ).latest(
                'date',
                'index'
            )
            closing_balance = last_transaction.closing_balance
        except Transaction.DoesNotExist:
            closing_balance = 0

        for t in transactions:
            closing_balance += t.size
            t.closing_balance = closing_balance
            t.save()

        # #######
        
        #     index = len(Transaction.objects.filter(user=request.user, date=date))
        #     t = Transaction(
        #         date=date,
        #         size=size,
        #         description=description,
        #         user=user,
        #         index=index
        #     )

        #     t.recalculate_closing_balances()
        
    else:
        ends_how = request.POST.get('ends_how', 'never_ends')
        if ends_how  == 'never_ends':
            RepeatTransaction.objects.create(
                start_date=date,
                size=size,
                description=description,
                user=request.user,
                index=0,
                frequency=frequency
            )
        elif ends_how == 'n_transactions':
            
            def get_end_date(start, frequency, n_transactions):
                if frequency == 'daily':
                    return start + datetime.timedelta(days=n_transactions - 1)
                elif frequency == 'weekly':
                    return start + datetime.timedelta(days=7*(n_transactions - 1))
                elif frequency == 'monthly':

                    end = start
                    year_end = start.year + (start.month - 1 + n_transactions) // 12
                    month_end = (start.month - 1 + n_transactions) % 12
                    month_end = 12 if month_end == 0 else month_end
                    try:
                        return datetime.date(year_end, month_end, start.day)
                    except ValueError:
                        x = datetime.date(year_end, month_end, 1)
                        return x - datetime.timedelta(days=1)

            n_transactions = int(request.POST['n_transactions'])
            
            end_date = get_end_date(date,
                                    n_transactions=n_transactions,
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

        elif ends_how == 'ends_on_date':

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

        ts = Transaction.objects.filter(user=user,
                                        repeat_transaction_id=int(repeat_transaction_id)
        )
        
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

        if(len(ts) == 0):
            RepeatTransaction.objects.get(id=int(repeat_transaction_id)).delete()

    elif delete_how == 'all_transactions_of_this_type':
        t = Transaction.objects.get(user=user, id=transaction_id)
        rt = t.repeat_transaction
        rt.delete()

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
