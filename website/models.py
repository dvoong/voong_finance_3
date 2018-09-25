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
    
def get_balance(user, date):
    df_balances, df_transactions = get_balances(user, date, date)
    return df_balances['balance'].values[0]

def get_balances(user, start, end):

    # generate repeat transactions
    repeat_transactions = get_repeat_transactions(user)
    transactions = []
    for rt in repeat_transactions:
        transactions.extend(rt.generate_repeat_transactions(end))
    transactions = sorted(transactions, key=lambda t: (t.date, t.repeat_transaction_id))
    
    if len(transactions):
        # get previous transaction
        previous_transaction = get_previous_transaction(user, transactions[0].date)
        if previous_transaction is not None:
            closing_balance = previous_transaction.closing_balance
        else:
            closing_balance = 0.
        for t in transactions:
            index = len(Transaction.objects.filter(date=t.date))
            t.index = index
            closing_balance = closing_balance + t.size
            t.closing_balance = closing_balance
            t.save()
            t.repeat_transaction.previous_transaction_date = t.date
            t.repeat_transaction.save()

    previous_transaction = get_previous_transaction(user, start)
    if previous_transaction is not None:
        closing_balance = previous_transaction.closing_balance
    else:
        closing_balance = 0.

    dates = pd.date_range(start, end)
    df_balances = pd.DataFrame(dates, columns=['date'])
    df_balances['balance'] = closing_balance
    transactions = get_transactions(user, start, end)

    values = []
    for t in transactions:
        values.append(
            (
                t.date,
                t.size,
                t.description,
                t.closing_balance,
                t.id,
                t.repeat_transaction_id
            )
        )
    columns = ['date', 'size', 'description', 'closing_balance', 'id', 'repeat_transaction_id']
    df_transactions = pd.DataFrame(values, columns=columns)
    df_transactions['date'] = pd.to_datetime(df_transactions['date'])
    df_transactions['size'] = df_transactions['size'].astype(float)
    df_transactions_by_date = df_transactions.groupby('date')[['size']].sum().reset_index()
    df_balances = pd.merge(df_balances, df_transactions_by_date, on='date', how='left').fillna(0)
    df_balances['size'] = df_balances['size'].cumsum()
    df_balances['balance'] = df_balances['balance'] + df_balances['size']
    df_balances = df_balances[['date', 'balance']]

    return df_balances, df_transactions

def get_next_transaction_date(date, frequency, steps=1):
    for i in range(steps):
        date = frequency_string_to_next_date_function[frequency](date)
    return date

def get_previous_transaction(user, date, index=None):
    try:
        if index is not None:
            previous_transaction = Transaction.objects.filter(
                Q(date__lt=date) | Q(date=date, index__lt=index),
                user=user
            ).latest('date', 'index')
        else:
            previous_transaction = Transaction.objects.filter(
                date__lt=date,
                user=user
            ).latest('date', 'index')
            
    except Transaction.DoesNotExist:
        previous_transaction = None
    return previous_transaction

def get_repeat_transactions(user):
    return RepeatTransaction.objects.filter(user=user)

def get_transactions(user, start, end):
    return Transaction.objects.filter(
        user=user,
        date__gte=start,
        date__lte=end
    ).order_by('date', 'index')

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
    steps = models.IntegerField(null=True)

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
        date = get_next_transaction_date(self.previous_transaction_date, self.frequency, self.steps)
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

    def generate_repeat_transactions(self, end):
        return [t for t in self.generate_next_transaction(end)]
            
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
