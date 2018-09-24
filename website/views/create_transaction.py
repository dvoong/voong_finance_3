import datetime
import website.models as models
from django.shortcuts import redirect
from django.views import View
from website.models import RepeatTransaction, Transaction

strptime = datetime.datetime.strptime

class CreateTransactionView(View):


    def parse_args(self, request):
        date = strptime(request.POST['date'], '%Y-%m-%d').date()
        user = request.user
        size = float(request.POST['transaction_size'])
        steps = int(request.POST.get('steps', 1))
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
        ends_how = request.POST.get('ends_how', None)
        
        if 'end_date' in request.POST and request.POST['end_date'] != '':
            end_date = strptime(request.POST['end_date'], '%Y-%m-%d')
        else:
            end_date = None
        if 'n_transactions' in request.POST and request.POST['n_transactions'] != '':
            n_transactions = int(request.POST['n_transactions'])
        else:
            n_transactions = None

        return {
            'date': date,
            'user': user,
            'size': size,
            'description': description,
            'repeat_status': repeat_status,
            'frequency': frequency,
            'today': today,
            'start': start,
            'steps': steps,
            'end': end,
            'end_date': end_date,
            'ends_how': ends_how,
            'n_transactions': n_transactions,
        }

    def create_repeat_transaction(self, args):
        user = args['user']
        date = args['date']
        repeat_transactions = RepeatTransaction.objects.filter(user=user, start_date=date)
        index = len(repeat_transactions)
        
        rt = RepeatTransaction(
            start_date=args['date'],
            size=args['size'],
            description=args['description'],
            user=args['user'],
            index=index,
            frequency=args['frequency'],
            steps=args['steps']
        )

        if args['ends_how'] == 'never_ends':
            end_date = None
        elif args['ends_how'] == 'n_transactions':
            end_date = rt.start_date
            for i in range(args['n_transactions'] - 1):
                end_date = models.get_next_transaction_date(end_date, rt.frequency, args['steps'])
        elif args['ends_how'] == 'ends_on_date':
            end_date = args['end_date']
        else:
            raise Exception('unrecognised repeat transaction type: {}'.format(args['ends_how']))
        
        rt.end_date = end_date
        rt.save()
        
    def create_transaction(self, args):
        closing_balance = models.get_balance(user=args['user'], date=args['date']) + args['size']
        index = len(Transaction.objects.filter(user=args['user'], date=args['date']))

        t = Transaction(
            date=args['date'],
            size=args['size'],
            description=args['description'],
            user=args['user'],
            closing_balance=closing_balance,
            index=index
        )
        
        t.save()
        t.recalculate_closing_balances()
        
    def post(self, request):
        args = self.parse_args(request)

        if args['repeat_status'] == 'does_not_repeat':
            self.create_transaction(args)
        else:
            self.create_repeat_transaction(args)

        return redirect('/home?start={}&end={}'.format(args['start'], args['end']))
