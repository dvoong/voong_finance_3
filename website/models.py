import datetime
import pandas as pd
import numpy as np
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import datetime as dt

def add_1day(date):
    return date + datetime.timedelta(days=1)

def add_7days(date):
    return date + datetime.timedelta(days=7)

def next_month(date):
    day = date.day
    if date.month == 12:
        year = date.year + 1
        month = 1
    else:
        year = date.year
        month = date.month + 1

    try:
        next_month = datetime.date(year, month, day)
    except ValueError:
        # day is not valid for the next month, fallback to last day of that month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        next_month = datetime.date(year, month, 1) - datetime.timedelta(days=1)
    return next_month
        
def next_year(date):
    day = date.day
    month = date.month
    year = date.year + 1
    
    try:
        next_year = datetime.date(year, month, day)
    except ValueError:
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        next_year = datetime.date(year, month, 1) - datetime.timedelta(days=1)

    return next_year

frequency_string_to_next_date_function = {
    'daily': add_1day,
    'weekly': add_7days,
    'monthly': next_month,
    'annually': next_year
}

def get_next_transaction_date(date, frequency):
    return frequency_string_to_next_date_function[frequency](date)

class RepeatTransaction(models.Model):

    REPEAT_STATUSES = (
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    )
    MAX_GENERATIONS = 1000

    start_date = models.DateField()
    previous_transaction_date = models.DateField(null=True)
    size = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    index = models.IntegerField()
    frequency = models.CharField(max_length=7, null=True)
    end_date = models.DateField(null=True)

    def create_transaction(self, date):
        return  Transaction(
            date=date,
            size=self.size,
            description=self.description,
            user=self.user,
            index=len(Transaction.objects.filter(
                user=self.user,
                date=date)),
            repeat_transaction=self
        )

    def get_next_transaction_date(self):
        if self.previous_transaction_date is None:
            return self.start_date
        date = get_next_transaction_date(self.previous_transaction_date, self.frequency)
        if self.end_date is not None and date > self.end_date:
            return None
        return date

    def generate_next_transaction(self, end):
        counter = 0
        while True:
            date = self.get_next_transaction_date()
            if date is None or date > end:
                return

            self.previous_transaction_date = date
            yield self.create_transaction(date)
            counter += 1
            if counter >= self.MAX_GENERATIONS:
                # todo raise exception when too many transactions are generated
                return
            
# Create your models here.
class Transaction(models.Model):
    
    date = models.DateField()
    size = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closing_balance = models.FloatField(null=True)
    index = models.IntegerField()
    repeat_transaction = models.ForeignKey(RepeatTransaction,
                                           null=True,
                                           on_delete=models.CASCADE)

    def __str__(self):
        return str(
            (
                ('date', self.date),
                ('index', self.index),
                ('size', self.size),
                ('balance', self.closing_balance),
                ('description', self.description),
            )
        )

    def delete(self, *args, **kwargs):
        ts = Transaction.objects.filter(date=self.date, user=self.user, index__gt=self.index)
        for t in ts:
            t.index -= 1
            t.save()
        super().delete(*args, **kwargs)

    def get_following_transactions(self):
        return Transaction.objects.filter(
            Q(date__gt=self.date) | Q(date=self.date, index__gt=self.index),
            user=self.user
        ).order_by('date', 'index')

    def get_previous_transaction(self):
        return get_previous_transaction(self.user, self.date, self.index)
        
    def recalculate_closing_balances(self):

        transactions = self.get_following_transactions()

        closing_balance = self.closing_balance
        for t in transactions:
            closing_balance += t.size
            t.closing_balance = closing_balance
            t.save()
    
def get_balance(user, date):

    previous_transaction = get_previous_transaction(user, date)
    if previous_transaction is not None:
        closing_balance = previous_transaction.closing_balance
    else :
        closing_balance = 0.

    repeat_transactions = RepeatTransaction.objects.filter(user=user)
    transactions = []
    for rt in repeat_transactions:
        for t in rt.generate_next_transaction(date):
            transactions.append(t)

    transactions = sorted(transactions, key=lambda t: (t.date, t.repeat_transaction.id))

    date = None
    for t in transactions:
        if t.date != date:
            index = 0
        else:
            index += 1
        closing_balance += t.size
        t.index = index
        t.closing_balance = closing_balance
        t.save()
        t.repeat_transaction.previous_transaction_date = t.date
        t.repeat_transaction.save()

    return closing_balance
                               
def get_balances(user, start, end):

    repeat_transactions = RepeatTransaction.objects.filter(
        user=user,
        start_date__lte=end
    )

    generated_transactions = []
        
    for rt in repeat_transactions:
        for t in rt.generate_next_transaction(end):
            generated_transactions.append(t)
            # t.recalculate_closing_balances()

    generated_transactions = sorted(generated_transactions, key=lambda t: t.date)
            
    if len(generated_transactions):
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
            t.repeat_transaction.previous_transaction_date = t.date
            t.repeat_transaction.save()

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
    
    transactions_df = pd.DataFrame(list(transactions.values()))
    if len(transactions):
        transactions_df['date'] = transactions_df['date'].astype('datetime64[ns]')
        transactions_by_date = transactions_df.groupby('date')['size'].sum().reset_index()
        transactions_by_date = dates.merge(transactions_by_date, on='date', how='left').fillna(0)
        transactions_by_date['cumsum']  = transactions_by_date['size'].cumsum()
        balances['balance'] += transactions_by_date['cumsum']
        

    return balances, transactions_df

def get_previous_transaction(user, date, index=None):
    try:
        if index is not None:
            previous_transaction = Transaction.objects.filter(
                Q(date__lt=date) | Q(date=date, index__lt=index),
                user=user
            ).latest('date', 'index')
        else:
            previous_transaction = Transaction.objects.filter(
                date__lte=date,
                user=user
            ).latest('date', 'index')
            
    except Transaction.DoesNotExist:
        previous_transaction = None
    return previous_transaction

def get_transactions(user, start, end):
    return Transaction.objects.filter(
        user=user,
        date__gte=start,
        date__lte=end
    ).order_by('date', 'index')
