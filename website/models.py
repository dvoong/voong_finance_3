import datetime
import pandas as pd
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Transaction(models.Model):
    
    date = models.DateField()
    size = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closing_balance = models.FloatField()
    index = models.IntegerField()

class RepeatTransaction(models.Model):

    REPEAT_STATUSES = (
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    )

    start_date = models.DateField()
    previous_transaction_date = models.DateField(null=True)
    size = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    index = models.IntegerField()
    frequency = models.CharField(max_length=7)

    def generate_next_transaction(self):
        if self.previous_transaction_date is None:
            return Transaction(date=self.start_date,
                               size=self.size,
                               description=self.description,
                               user=self.user)
        else:
            f = {
                'daily': 1,
                'weekly': 7,
                'monthly': 28
            }[self.frequency]
            return Transaction(date=self.previous_transaction_date + datetime.timedelta(days=f),
                            size=self.size,
                            description=self.description,
                            user=self.user)

def get_transactions(user, start, end):
    
    return Transaction.objects.filter(user=user,
                                      date__gte=start,
                                      date__lte=end).order_by('date', 'index')
                               
def get_balances(user, start, end):

    repeat_transactions = RepeatTransaction.objects.filter(user=user,
                                                     start_date__lt=end)

    for rt in repeat_transactions:
        t = rt.generate_next_transaction()
        while t.date <= end:
            t_ = Transaction.objects.filter(user=user, date=t.date)
            t.index = len(t_)
            t.closing_balance = 0
            t.save()
            rt.previous_transaction_date = t.date
            t = rt.generate_next_transaction()
        rt.save()

    dates = pd.DataFrame(pd.date_range(start, end), columns=['date'])
    balances = dates

    try:
        last_transaction = Transaction.objects.filter(
            user=user,
            date__lt=start).latest(
                'date',
                'index')
        closing_balance = last_transaction.closing_balance
    except Transaction.DoesNotExist:
        closing_balance = 0
    
    balances['balance'] = closing_balance

    transactions = get_transactions(user, start, end)
    for t in transactions:
        closing_balance = closing_balance + t.size
        t.closing_balance = closing_balance
        t.save()
    
    transactions_df = pd.DataFrame(list(transactions.values()))
    if len(transactions):
        transactions_df['date'] = transactions_df['date'].astype('datetime64[ns]')
        transactions_by_date = transactions_df.groupby('date')['size'].sum().reset_index()
        transactions_by_date = dates.merge(transactions_by_date, on='date', how='left').fillna(0)
        transactions_by_date['cumsum']  = transactions_by_date['size'].cumsum()
        balances['balance'] += transactions_by_date['cumsum']
        

    return balances, transactions_df
