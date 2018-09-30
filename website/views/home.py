import datetime, math
import website.forms as forms
import website.models as models
from django.shortcuts import render
from django.views import View
from voong_finance.utils import iso_to_date

class HomeView(View):

    DEFAULT_DATE_RANGE = datetime.timedelta(days=84) # quarterly

    def get_start_and_end_dates(self, request, today):
        if 'start' not in request.GET and 'end' not in request.GET:
            days = self.DEFAULT_DATE_RANGE.total_seconds() / (3600 * 24)
            days_before = math.ceil(days / 2) - 1
            start = today - datetime.timedelta(days=days_before)
            end = start + self.DEFAULT_DATE_RANGE - datetime.timedelta(days=1)
        elif 'start' in request.GET and 'end' not in request.GET:
            start = iso_to_date(request.GET['start'])
            end = start + self.DEFAULT_DATE_RANGE - datetime.timedelta(days=1)
        elif 'end' in request.GET and 'start' not in request.GET:
            end = iso_to_date(request.GET['end'])
            start = end - self.DEFAULT_DATE_RANGE + datetime.timedelta(days=1)
        else:
            start = iso_to_date(request.GET['start'])
            end = iso_to_date(request.GET['end'])
            
        return start, end

    def parse_args(self, request):
        args = {}
        today = datetime.date.today()
        start, end = self.get_start_and_end_dates(request, today)
        args['start'] = start
        args['end'] = end
        args['user'] = request.user
        args['today'] = today
        args['days'] = (end - start).days
        args['center_on_today_start'] = today - datetime.timedelta(days=args['days']//2)
        args['center_on_today_end'] = today + datetime.timedelta(days=args['days'] - args['days']//2)
        return args

    def get(self, request):
        args = self.parse_args(request)
        balances, transactions = models.get_balances(args['user'], args['start'], args['end'])
        balances['date'] = balances['date'].dt.strftime('%Y-%m-%d')
        transactions['date'] = transactions['date'].dt.strftime('%Y-%m-%d')
        repeat_transactions = models.RepeatTransaction.objects.filter(user=args['user'])

        template_kwargs = {
            'transactions': transactions.to_json(orient='records'),
            'balances': balances.to_dict('records'),
            'start': args['start'],
            'end': args['end'],
            'today': args['today'],
            'start_plus_7': args['start'] + datetime.timedelta(days=7),
            'end_plus_7': args['end'] + datetime.timedelta(days=7),
            'start_minus_7': args['start'] - datetime.timedelta(days=7),
            'end_minus_7': args['end'] - datetime.timedelta(days=7),
            'center_on_today_start': args['center_on_today_start'],
            'center_on_today_end': args['center_on_today_end'],
            'repeat_transactions': repeat_transactions,
            'authenticated': args['user'].is_authenticated,
            'new_transaction_form': forms.NewTransactionForm(auto_id="%s")
        }
        return render(request, 'website/home.html', template_kwargs)
